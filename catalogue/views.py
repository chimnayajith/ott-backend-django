import traceback
from django.contrib.auth import login, get_user_model
from rest_framework.response import Response
from django.http import JsonResponse, HttpResponse
from rest_framework import generics, status
from rest_framework.views import APIView

from app.settings import MEDIA_ROOT
from .models import User, HistoryItem, WatchlistItem
from .serializers import UserSerializer, HistoryItemSerializer, WatchlistItemSerializer
import jwt
import datetime
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authentication import BaseAuthentication
from rest_framework.permissions import IsAuthenticated, BasePermission
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.urls import reverse
from django.template.loader import render_to_string
from .serializers import PasswordResetSerializer
from .fetch_data import tmdb_reviews, \
    tmdb_search, tmdb_details, get_media_data, debug_print
from .signals import user_active

# user authentication
def user_auth(email=None, password=None):
    UserModel = get_user_model()
    try:
        user = UserModel.objects.get(email=email)
    except UserModel.DoesNotExist:
        return None

    if user.check_password(password):
        return user


def get_user(user_id):
    UserModel = get_user_model()
    try:
        return UserModel.objects.get(pk=user_id)
    except UserModel.DoesNotExist:
        return None


# search and analytics
# ----------------------------------------------------------------------------------------------------------------------


# User Views
# ----------------------------------------------------------------------------------------------------------------------
class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        debug_print(password)

        user = user_auth(email=email, password=password)

        if user is not None:
            login(request, user)
            serializer = UserSerializer(user)

            expiration_time = datetime.datetime.utcfromtimestamp(4102444800)
            payload = {
                'id': user.id,
                'exp': expiration_time,
                'iat': datetime.datetime.utcnow()
            }
            token = jwt.encode(payload, 'secret', algorithm='HS256')

            response = Response()
            response.set_cookie(key='jwt', value=token, httponly=True)

            response.data = {
                'jwt': token
            }

            # return  response

            debug_print(serializer.data)
            return (response)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class DecodeJwtView(APIView):
    def post(self, request):
        token = request.data['jwt']
        if not token:
            raise AuthenticationFailed('Unauthenticated')
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated')
        user = User.objects.filter(id=payload['id']).first()
        serializer = UserSerializer(user)

        return Response(serializer.data)


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.headers.get("Authorization")
        if not token:
            raise AuthenticationFailed('Unauthenticated')
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated')
        user = User.objects.filter(id=payload['id']).first()
        if user:
            # emitting custom signal to log active users.
            user_active.send(sender=self.__class__, user=user, request=request) 
            return (user, None)
        else:
            raise AuthenticationFailed("Unauthenticated")


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, User):
            return obj == request.user
        else:
            return obj.user == request.user


# Check the jwt token
class UserView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return Response(self.request.user)


class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsOwner]
    queryset = User.objects.all()
    serializer_class = UserSerializer


# HistoryItem Views
class HistoryItemListCreateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        content = request.data.get('content')
        HistoryItem.objects.create(user=self.request.user, content=content)
        return Response({'success': True, 'message': content})


class History(APIView):
    def get(self, request):
        try:
            y = [obj.to_dict() for obj in list(HistoryItem.objects.all())]
            response = {"history": y}
            return Response(response)
        except Exception as e:
            debug_print(e)
            return Response({"Error": str(e)})


class HistoryItemRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsOwner]
    queryset = HistoryItem.objects.all()
    serializer_class = HistoryItemSerializer


# WatchlistItem Views
class WatchlistItemListCreateView(generics.ListCreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        id = request.data.get('id')
        type = request.data.get('type')
        content = {
            "id": id,
            "type": type
        }
        WatchlistItem.objects.create(user=self.request.user, content=content)
        return Response({'success': True, 'message': content})

    def get(self, request):
        try:
            watchlist = [obj.to_dict() for obj in list(WatchlistItem.objects.filter(user=self.request.user))]
            response = {"watchlist": watchlist}
            return Response(response)
        except Exception as e:
            debug_print(e)
            return Response({"Error": str(e)})


class WatchlistItemRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsOwner]
    queryset = WatchlistItem.objects.all()
    serializer_class = WatchlistItemSerializer


# Movie data Views
# ----------------------------------------------------------------------------------------------------------------------
class MovieSearchView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            _type = request.data.get("type", "multi")
            query = request.data.get("search")
            query = query.replace(" ", "%20")
            data = tmdb_search(_type, query)

            response = {"results": []}

            for i in data['results']:
                response['results'].append(i)

            return JsonResponse(response)
        except Exception as e:
            traceback.print_exc()
            return Response({"Error": str(e)})


class MovieDetailsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        _type = request.data.get("type")
        id = request.data.get("id")
        try:
            tmdb_id = int(id)
            dat = tmdb_details(_type, tmdb_id)
            debug_print(dat)
            content = {
                "id": dat.id,
                "type": dat.type
            }
            HistoryItem.objects.create(user=self.request.user, content=content)
            return JsonResponse(dat.to_json())
        except Exception as e:
            traceback.print_exc()
            debug_print("error fetching movie details")
            return JsonResponse({"error": str(Exception(e))})


class TopRatedView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        response = get_media_data('top_rated')
        return Response({"releases": response})


class ReleasesView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        response = get_media_data('releases')
        return Response({"releases": response})


class TrendingView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        response = get_media_data('trending')
        return Response({"releases": response})


class UpcomingView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        response = get_media_data('upcoming')
        return Response({"releases": response})


# ----------------------------------------------------------
# TV Series
# ----------------------------------------------------------
class TvAiringTodayView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        response = get_media_data('tv_airing_today')
        return Response({"releases": response})


class TvOnTheAirView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        response = get_media_data('tv_on_air')
        return Response({"releases": response})


class TvPopularView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        response = get_media_data('tv_popular')
        return Response({"releases": response})


class TvTopRatedView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        response = get_media_data('tv_top_rated')
        return Response({"releases": response})


class TvTrendingView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        response = get_media_data('tv_trending')
        return Response({"releases": response})


# Reviews
# ----------------------------------------------------------------------------------------------------------------------
class ReviewsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            id = request.data.get("id")
            _type = request.data.get("type")
            if _type in ["movie", "tv"]:
                # returns reviews in a list
                response = tmdb_reviews(_type, id)
                debug_print(str(response))
                return Response(response['results'])
            else:
                return JsonResponse({"error": "Invalid type"}, status=400)
        except Exception as e:
            debug_print(e)
            return JsonResponse({"error": str(e)}, status=400)


# Media
# ----------------------------------------------------------------------------------------------------------------------
def default_image(request):
    image_path = f"{MEDIA_ROOT}/default-video.png"
    with open(image_path, "rb") as f:
        return HttpResponse(f.read(), content_type="image/png")


# ----------------------------------------------------------
# Password Reset
# ----------------------------------------------------------
class PasswordResetView(generics.GenericAPIView):
    serializer_class = PasswordResetSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        user = User.objects.get(email=email)
        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_url = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            reset_link = request.build_absolute_uri(reset_url)

            context = {
                'user': user,
                'reset_link': reset_link,
                'validity_period': '24 hours',
                'support_email': 'support@example.com'
            }

            email_subject = 'Password Reset Request'
            email_body = render_to_string('catalogue/password_reset_email.html', context)

            email = EmailMultiAlternatives(
                subject=email_subject,
                body=email_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            email.attach_alternative(email_body, "text/html")
            email.send()
            return Response({"message": "Password reset email has been sent."}, status=status.HTTP_200_OK)
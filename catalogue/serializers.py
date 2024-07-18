from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import HistoryItem, User, WatchlistItem, Source, CastMember
import traceback 

# Custom serializer field classes
# ----------------------------------------------------------------------------------------------------------------------
class PriceField(serializers.FloatField):
    def to_internal_value(self, data):
        try:
            price = float(data)
            return price
        except (TypeError, ValueError):
            return None

    def to_representation(self, value):
        return float(value) if value is not None else None

class DeeplinkField(serializers.CharField):
    def to_internal_value(self, data):
        try:
            if isinstance(data , str):
                if "://" in data and " " not in data:
                    return data
            else:
                return None
        except Exception as _:
            traceback.print_exc()
            raise ValidationError("Invalid Deeplink url")

# Custom serializer classes
# ----------------------------------------------------------------------------------------------------------------------

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, style={'input_type': 'password'})

    class Meta:
        model = get_user_model()
        fields = ('id', 'email', 'username', 'password', 'country', 'date_of_birth', 'phone_number')
        extra_kwargs = {
            'date_of_birth': {'required': False},
            'phone_number':{'required':False}
        }

    def __init__(self, *args, **kwargs):
        super(UserSerializer, self).__init__(*args, **kwargs)
        if self.instance is None:
            self.fields['password'].required = True

    def create(self, validated_data):
        user = get_user_model().objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            country=validated_data['country']
        )
        user.set_password(validated_data['password'])
        if 'date_of_birth' in validated_data:
            user.date_of_birth=validated_data['date_of_birth']
        if 'phone_number' in validated_data:
            user.phone_number=validated_data['phone_number']
        user.save()
        return user

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class HistoryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoryItem
        fields = ['user', 'content', 'object_id', 'timestamp']

class WatchlistItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = WatchlistItem
        fields = ['user', 'content', 'object_id', 'timestamp']


class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = '__all__'


class CastMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = CastMember
        fields = '__all__'

class StreamingServiceSerializer(serializers.Serializer):
    source_id = serializers.IntegerField()
    name = serializers.CharField(max_length=100)
    type = serializers.CharField(max_length=10)
    region = serializers.CharField(max_length=2)
    ios_url = DeeplinkField(allow_null=True, required=False)
    android_url = DeeplinkField(allow_null=True, required=False)
    web_url = DeeplinkField(allow_null=True, required=False)
    format = serializers.CharField(max_length=10, allow_null=True, required=False)
    price = PriceField(allow_null=True)
    seasons = serializers.IntegerField(allow_null=True, required=False)
    episodes = serializers.IntegerField(allow_null=True, required=False)
    logo_url = DeeplinkField(allow_null=True, required=True)

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("There is no user registered with this email address.")
        return value
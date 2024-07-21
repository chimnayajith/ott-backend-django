from django.urls import path
from .views import (
    PasswordResetView, UserListCreateView, UserRetrieveUpdateDestroyView,
    HistoryItemListCreateView, HistoryItemRetrieveUpdateDestroyView,
    WatchlistItemListCreateView, WatchlistItemRetrieveUpdateDestroyView, MovieDetailsView,
    MovieSearchView, LoginView,
    DecodeJwtView, ReviewsView, TrendingView, ReleasesView, UpcomingView, TopRatedView,
    TvAiringTodayView, TvOnTheAirView, TvPopularView, TvTopRatedView, TvTrendingView, default_image
)
from catalogue import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    #path('user_search/', VectorSearchView.as_view(), name='user_search'),
    path('user_view/', DecodeJwtView.as_view()),

    path('login/', LoginView.as_view(), name='login'),
    path('register/', UserListCreateView.as_view(), name='user-create'),
    path('users/', UserRetrieveUpdateDestroyView.as_view(), 
         name='user-retrieve-update-destroy'),

    path('history/', HistoryItemListCreateView.as_view(), 
         name='history-list-create'),
    path('history/<int:pk>/', HistoryItemRetrieveUpdateDestroyView.as_view(), 
         name='history-retrieve-update-destroy'),

    path('history/all/', views.History.as_view(), name='history-retrieve-all'),

    path('watchlist/', WatchlistItemListCreateView.as_view(), name='watchlist-list-create'),
    path('watchlist/<int:pk>/', WatchlistItemRetrieveUpdateDestroyView.as_view(), 
         name='watchlist-retrieve-update-destroy'),
 
    #path('movie/genres/', MovieGenres.as_view(), name='list-genres'),
    #path('movie/genre/',MovieGenresList.as_view(), name='list-titles-of-a-genre'),
    path('movie/search/', MovieSearchView.as_view(), name='title-search'),
    path('movie/details/', MovieDetailsView.as_view(), name='title-details'),
    path('movie/releases/', ReleasesView.as_view(), name='title-releases'),
    path('movie/trending/', TrendingView.as_view(), name='trending-releases'),
    path('movie/upcoming/', UpcomingView.as_view(), name='upcoming-releases'),
    path('movie/top_rated/', TopRatedView.as_view(), name='top-rated-releases'),

    path('tv/trending/', TvTrendingView.as_view(), name='tv-trending'),
    path('tv/airing_today/', TvAiringTodayView.as_view(), name='tv-airing-today'),
    path('tv/on_air/', TvOnTheAirView.as_view(), name='tv-on-the-air'),
    path('tv/popular/', TvPopularView.as_view(), name='tv-popular'),
    path('tv/top_rated/', TvTopRatedView.as_view(), name='tv-top-rated'),

    path('reviews/', ReviewsView.as_view(), name='reviews'),

    path('media/default-video.png/', default_image, name='default_image'),

    path('reset/', PasswordResetView.as_view(), name='password_reset'),
    path('reset/<uidb64>/<token>/', 
        auth_views.PasswordResetConfirmView.as_view(template_name="catalogue/password_reset_confirm.html"), 
        name='password_reset_confirm'),
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(template_name="catalogue/password_reset_complete.html"), 
         name='password_reset_complete'),
]
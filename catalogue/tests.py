from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
import json
from .models import User, HistoryItem, WatchlistItem

import os
from dotenv import find_dotenv

# ========== Checking if the api keys exist ================
# ==========================================================
class TestAPIKeysExist(TestCase):
    def test_api_key_exist(self):
        tmdb_auth = os.environ.get("TMDB_AUTH") if find_dotenv() == '' else os.getenv("TMDB_AUTH") 
        watchmode_auth = os.environ.get("WATCHMODE_API_KEY") if find_dotenv() == '' else os.getenv("WATCHMODE_API_KEY")
        self.assertIsNotNone(tmdb_auth,"TMDB_AUTH environment variable is not set")
        self.assertIsNotNone(watchmode_auth,"WATCHMODE_API_KEY environment variable is not set")

# ========== Testing the register and login endpoints ======
# ==========================================================
class AuthenticationTest(TestCase):

    def setUp(self):
        self.client = APIClient()
    
    def test_user_registration(self):
        data = {
            'username': 'testUser',
            'email': 'testuser@example.com',
            'password': 'StrongPassword123!',
            'country' : "US"
        }
        
        response = self.client.post('/register/', data, format='json')

        self.assertEqual(response.status_code, 201) # checking whether the response code is 201 
        self.assertEqual(response.data['username'], data['username'])  
        self.assertEqual(response.data['email'], data['email'])
        self.assertEqual(response.data['country'] , data['country'])
        self.assertNotIn('password', response.data) # checking that the password is not retuned


    def test_user_login(self):
        # creating a user for testing user login
        user = get_user_model().objects.create_user(
            username='testUser',
            email='testuser@example.com',
            password='StrongPassword123!',
            country = 'US'
        )

        self.client.force_login(user)

        data = {
            'email' : 'testuser@example.com',
            'password' : 'StrongPassword123!'
        }

        response = self.client.post('/login/' , data , format='json')

        self.assertEqual(response.status_code , 200)
        self.assertIn('jwt' , response.data)



# ========== Testing the movie search and details endpoints ======
# ================================================================
class MovieTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = get_user_model().objects.create_user(
            username='testUser',
            email='testuser@example.com',
            password='StrongPassword123!',
            country = 'US'
        )
        self.client.force_login(self.user)
        data = {
            'email' : 'testuser@example.com',
            'password' : 'StrongPassword123!'
        }
        response = self.client.post('/login/' , data , format='json')
        self.jwt = response.data['jwt']

    # fetching search results of a common movie title with a high probability of successful retrieval
    def test_movie_search(self):
        data = {
            "type":"movie",
            "search" : 'The Shawshank Redemption'
        }
        headers = {'Authorization':self.jwt}
        response = self.client.post('/movie/search/' ,headers=headers, data=data , format='json')
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertGreaterEqual(len(response_data['results']), 1)
        self.assertEqual(response_data['results'][0]['name'], 'The Shawshank Redemption')

    
    # fetching details of a particular movie.
    def test_movie_details(self):
        data = {
            'type':'movie',
            'id' : 278
        }
        headers = {'Authorization':self.jwt}
        response = self.client.post('/movie/details/' ,headers=headers, data=data , format='json')
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['tmdb_id'] , 278)
        self.assertEqual(response_data['title'] , "The Shawshank Redemption")

    
    # testing the movie releases endpoint
    def test_movie_releases(self):
        headers = {'Authorization':self.jwt}
        response = self.client.get('/movie/releases/',headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('releases', response.data)


    # testing the trending movies endpoint
    def test_movie_trending(self):
        headers = {'Authorization':self.jwt}
        response = self.client.get('/movie/trending/',headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('releases', response.data)
    

    # testing the upcoming movies endpoint
    def test_movie_upcoming(self):
        headers = {'Authorization':self.jwt}
        response = self.client.get('/movie/upcoming/',headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('releases', response.data)
    

    # testing the top rated movies endpoint
    def test_movie_top_rated(self):
        headers = {'Authorization':self.jwt}
        response = self.client.get('/movie/top_rated/',headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('releases', response.data)
    

    # testing the movie review endpoint
    def test_movie_reviews(self):
        data = {
            'id' : 278,
            'type' : 'movie'
        }
        headers = {'Authorization':self.jwt}
        response = self.client.post('/reviews/' ,headers=headers, data=data, format='json')
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertGreaterEqual(len(response_data) , 1)

    

# ========== Testing the movie search and details endpoints ======
# ================================================================    
class TVTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = get_user_model().objects.create_user(
            username='testUser',
            email='testuser@example.com',
            password='StrongPassword123!',
            country = 'US'
        )
        self.client.force_login(self.user)
        data = {
            'email' : 'testuser@example.com',
            'password' : 'StrongPassword123!'
        }
        response = self.client.post('/login/' , data , format='json')
        self.jwt = response.data['jwt']

    # fetching search results of a common tv show title with a high probability of successful retrieval
    def test_tv_search(self):
        data = {
            "type":"tv",
            "search" : 'The Office'
        }
        headers = {'Authorization':self.jwt}
        response = self.client.post('/movie/search/' ,headers=headers, data=data , format='json')
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertGreaterEqual(len(response_data['results']), 1)
        self.assertEqual(response_data['results'][0]['name'], 'The Office')

    
    # fetching details of a particular tv show.
    def test_tv_details(self):
        data = {
            'type':'tv',
            'id' : 2316
        }
        headers = {'Authorization':self.jwt}
        response = self.client.post('/movie/details/' ,headers=headers, data=data , format='json')
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['tmdb_id'] , 2316)
        self.assertEqual(response_data['title'] , "The Office")

    
    # testing the airing today tv shows endpoint
    def test_tv_releases(self):
        headers = {'Authorization':self.jwt}
        response = self.client.get('/tv/airing_today/',headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('releases', response.data)


    # testing the trending tv shows endpoint
    def test_tv_trending(self):
        headers = {'Authorization':self.jwt}
        response = self.client.get('/tv/trending/',headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('releases', response.data)
    

    # testing the on air tv shows endpoint
    def test_tv_upcoming(self):
        headers = {'Authorization':self.jwt}
        response = self.client.get('/tv/on_air/',headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('releases', response.data)
    

    # testing the top rated tv shows endpoint
    def test_tv_top_rated(self):
        headers = {'Authorization':self.jwt}
        response = self.client.get('/tv/top_rated/',headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('releases', response.data)
    
    # testing the popular tv shows endpoint
    def test_tv_popular(self):
        headers = {'Authorization':self.jwt}
        response = self.client.get('/tv/popular/',headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('releases', response.data)

    # testing the tv show review endpoint
    def test_tv_reviews(self):
        data = {
            'id' : 2316,
            'type' : 'tv'
        }
        headers = {'Authorization':self.jwt}
        response = self.client.post('/reviews/' ,headers=headers, data=data, format='json')
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertGreaterEqual(len(response_data) , 1)


# ========== Testing the user CRUD operations ==============
# ==========================================================
class UserRetrieveUpdateDestroyAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()
        # Create a test user
        self.user = get_user_model().objects.create_user(
            username='testUser',
            email='testuser@example.com',
            password='StrongPassword123!',
            country = 'US'
        )
        self.client.force_login(self.user)
        data = {
            'email' : 'testuser@example.com',
            'password' : 'StrongPassword123!'
        }
        response = self.client.post('/login/' , data , format='json')
        self.jwt = response.data['jwt']

    # test retreiving a user data using GET
    def test_retrieve_user(self):
        headers = {'Authorization':self.jwt}
        response = self.client.get(f"/users/{self.user.pk}/", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['username'], self.user.username)


    def test_update_user(self):
        data = {
            'username': 'testUser_updated',
            'email': 'testuserUpdated@example.com',
            'password': 'StrongPasswordUpdated123!',
            'country' : "UK"
        }
        headers = {'Authorization':self.jwt}
        response = self.client.put(f"/users/{self.user.pk}/", headers=headers, data=data, format='json')
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()  # Refresh user object after update
        self.assertEqual(self.user.username, data['username'])
        self.assertEqual(self.user.email, data['email'])
        self.assertEqual(self.user.password, data['password'])
        self.assertEqual(self.user.country, data['country'])


    # test updating only certain fields of a user using PATCH request
    def test_partial_update_user(self):
        data = {'email': 'testuserUpdated@example.com'}  # updating only the email
        headers = {'Authorization':self.jwt}
        response = self.client.patch(f"/users/{self.user.pk}/", headers=headers, data=data, format='json')
        self.user.refresh_from_db() # refreshing the database 
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user.email, data['email'])
        self.assertEqual(self.user.username, self.user.username)


    # test deleting a user using DELETE request
    def test_delete_user(self):
        headers = {'Authorization':self.jwt}
        response = self.client.delete(f"/users/{self.user.pk}/", headers=headers, format='json')
        self.assertEqual(response.status_code, 204)
        self.assertRaises(User.DoesNotExist, self.user.refresh_from_db)




# ========== Testing the history CRUD operations ===========
# ==========================================================
class HistoryAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create a test user
        self.user = get_user_model().objects.create_user(
            username='testUser',
            email='testuser@example.com',
            password='StrongPassword123!',
            country = 'US'
        )
        self.client.force_login(self.user)
        data = {
            'email' : 'testuser@example.com',
            'password' : 'StrongPassword123!'
        }
        response = self.client.post('/login/' , data , format='json')
        self.jwt = response.data['jwt']

        self.history = HistoryItem.objects.create(
            user = self.user , 
            content = {
                "id":278,
                "type":"movie"
            }
        )
            
    # adding content to the history of the user
    def test_history_create(self):
        data = {
            'content':{
                "id":278,
                "type":"movie"
            }
        }
        headers = {
            'Authorization' : self.jwt,
        }
        response = self.client.post('/history/' , headers=headers , data=data , format='json')
        self.assertEqual(response.status_code , 200)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['message'] , data['content'])
    
    # retrieving history list of all users
    def test_history_all(self):
        # adding two items to history
        HistoryItem.objects.create(
            user = self.user , 
            content ={
                "id":278,
                "type":"movie"
            }
        )
        HistoryItem.objects.create(
            user = self.user , 
            content = {
                "id":252,
                "type":"tv"
            }
        )
        response = self.client.get('/history/all/')
        self.assertEqual(response.status_code , 200)
        self.assertIn('history' , response.data)
        self.assertEqual(len(response.data['history']) , 3)
            
    
    def test_retrieve_history(self):
        headers = {'Authorization': self.jwt}
        response = self.client.get(f'/history/{self.history.pk}/' , headers=headers)
        self.assertEqual(response.status_code , 200)
        self.assertEqual(response.data['user'] , self.user.pk)
        self.assertEqual(response.data['content'] , self.history.content)
    

    # testing by updating only the content of the history using PATCH request
    def test_partial_update_history(self):
        data = {
            'content':{
                "id":252,
                "type":"tv"
            }
        }
        headers = {'Authorization': self.jwt}
        response = self.client.patch(f"/history/{self.history.pk}/" , headers=headers, data=data , format='json')
        self.history.refresh_from_db()
        self.assertEqual(response.status_code , 200)
        self.assertEqual(response.data['content'] , self.history.content)


    # testing by updating both fields of the history item using PUT request
    def test_update_history(self):
        data = {
            'user' : self.user.id,
            'content':{
                "id":278,
                "type":"movie"
            }
        }
        headers = {'Authorization': self.jwt}
        response = self.client.put(f"/history/{self.history.pk}/" , headers=headers , data=data , format='json')
        self.history.refresh_from_db()
        self.assertEqual(response.status_code , 200)
        self.assertEqual(response.data['user'] , data['user'])
        self.assertEqual(response.data['content']['id'], data['content']['id'])


    # testing deleting a history item and ensuring the item is not in the db
    def test_delete_history(self):
        headers = {'Authorization': self.jwt}
        response = self.client.delete(f"/history/{self.history.pk}/" , headers=headers)
        self.assertEqual(response.status_code , 204)
        self.assertRaises(HistoryItem.DoesNotExist, self.history.refresh_from_db)




# ========== Testing the watchlist CRUD endpoints ===========
# ==========================================================
class WatchlistTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        # Create a test user
        self.user = get_user_model().objects.create_user(
            username='testUser',
            email='testuser@example.com',
            password='StrongPassword123!',
            country = 'US'
        )
        self.client.force_login(self.user)
        data = {
            'email' : 'testuser@example.com',
            'password' : 'StrongPassword123!'
        }
        response = self.client.post('/login/' , data , format='json')
        self.jwt = response.data['jwt']

        content = {
            "id":278,
            "type":"movie"
        }
        self.watchlist = WatchlistItem.objects.create(user=self.user, content=content)
        
    
    def test_watchlist_add(self):
        data = {
            "id":278,
            "type":"movie"
        }
        headers = {
            'Authorization' : self.jwt,
        }
        response = self.client.post('/watchlist/' ,headers=headers,data=data , format='json')
        self.assertEqual(response.status_code , 200)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['message'] , data)

    
    def test_retrieve_watchlist(self):
        headers = {'Authorization': self.jwt}
        response = self.client.get(f'/watchlist/{self.watchlist.pk}/', headers=headers) 
        self.assertEqual(response.status_code , 200)
        self.assertEqual(response.data['user'] , self.user.pk)
        self.assertEqual(response.data["content"] , self.watchlist.content)

    def test_update_watchlist(self):
        data = {
            'user' : self.user.id,
            'content': {
                'id':252,
                'type' : "tv"
            }
        }
        headers = {'Authorization': self.jwt}
        response = self.client.put(f"/watchlist/{self.watchlist.pk}/" ,headers=headers, data=data , format='json')
        self.watchlist.refresh_from_db()
        self.assertEqual(response.status_code , 200)
        self.assertEqual(response.data['user'] , self.user.pk)
        self.assertEqual(response.data['content'] , self.watchlist.content)


    def test_partial_update_watchlist(self):
        data = {
            'content': {
                'id':278,
                'type' : "movie"
            }
        }
        headers = {'Authorization': self.jwt}
        response = self.client.patch(f"/watchlist/{self.watchlist.pk}/" ,headers=headers, data=data , format='json')
        self.watchlist.refresh_from_db()
        self.assertEqual(response.status_code , 200)
        self.assertEqual(response.data['user'] , self.user.pk)
        self.assertEqual(response.data['content'] , self.watchlist.content)
    
    def test_delete_bookmark(self):
        headers = {'Authorization': self.jwt}
        response = self.client.delete(f"/watchlist/{self.watchlist.pk}/",headers=headers)
        self.assertEqual(response.status_code , 204)
        self.assertRaises(WatchlistItem.DoesNotExist , self.watchlist.refresh_from_db)
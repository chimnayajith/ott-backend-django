import traceback
from django.utils import timezone
from app.settings import base_url
from catalogue import serializers
from catalogue.models import (
    Review, Title, Trending, Source, CastMember, Upcoming, Releases, TopRated, 
    TvAiringToday, TvOnTheAir, TvPopular, TvTopRated, TvTrending 
)
import requests
from catalogue.serializers import StreamingServiceSerializer
from .utils import debug_print
from .config import tmdb_auth, watchmode_auth
from .movie_data import get_releases, get_top_releases, get_trending, get_upcoming
from .tv_data import get_airing_today, get_on_the_air, get_tv_popular, get_tv_top_rated, get_tv_trending
from .watchmode import get_source_logo
from .utils import transform_cert_json

def tmdb_details(type,id):
    debug_print(f"movie id: {id}")
    try:
        # return movie details if already in db
        existing_title = Title.objects.filter(tmdb_id=id, type=type).first()

        # returns model if existing
        if existing_title:
            debug_print("fetching movie from db")
            return existing_title

        debug_print("fetching movie from tmdb")
        movie_url = f"https://api.themoviedb.org/3/{type}/{id}?append_to_response=videos%2Ccredits%2Csimilar&language=en-US"
        sources_url = f"https://api.watchmode.com/v1/title/{type}-{id}/sources/?apiKey={watchmode_auth}"
        certification_url = f"https://api.themoviedb.org/3/movie/{id}/release_dates"
        tv_certification_url = f"https://api.themoviedb.org/3/tv/{id}/content_ratings"
        
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {tmdb_auth}"
        }
        
        debug_print("fetching details from tmdb")
        try:
            title_response = requests.get(movie_url, headers=headers)
            debug_print(title_response)
        except Exception as e:
            traceback.print_exc()
            debug_print(f"error getting tmdb movie details: {str(e)}")
            raise Exception(e)
        
        debug_print("fetching sources from watchmode")
        try:
            sources_response = requests.get(sources_url)
            debug_print(sources_response)
        except Exception as e:
            traceback.print_exc()
            debug_print(f"error getting watchmode source details: {str(e)}")
            raise Exception(e)
        
        debug_print(f"fetching {type} certifications from tmdb")
        try:
            cert_response = requests.get(
                certification_url if type=="movie" else tv_certification_url, 
                headers=headers
                )
            debug_print(cert_response)
            title_cert_data = cert_response.json()
            
            title_cert_data = transform_cert_json(type, title_cert_data)
        except Exception as e:
            traceback.print_exc()
            debug_print(f"error getting tmdb source details: {str(e)}")
            raise Exception(e)

        title_data = title_response.json()
        sources_data = sources_response.json()            
        
        # getting latest trailer
        videos = (title_data.get("videos")['results'])
        trailer = ''
        vid_count = len(videos)
        if vid_count > 0:
            for i in videos:
                if i['site'] == 'YouTube':
                    trailer = f"https://www.youtube.com/watch?v={i['key']}"

        # getting similar titles and extracting required data
        tmdb_similar = title_data.get("similar")["results"]
        similar = [
            {
                "id": result["id"], 
                "title": result["title"] if type=="movie" else result["name"], 
                "poster": f"https://image.tmdb.org/t/p/w342{result['poster_path']}"
            } 
            for result in tmdb_similar
        ]

        # data to be stored
        title_dict = {
            "tmdb_id": title_data.get("id"),
            "poster": f"https://image.tmdb.org/t/p/w780{title_data.get('poster_path')}",
            "title": title_data.get("title") if type=="movie" else title_data.get('name'),
            "plot_overview": title_data.get("overview"),
            "trailer": trailer,
            "user_rating": title_data.get("vote_average"),
            "original_title": title_data.get("original_title"),
            "year": ( int(title_data["release_date"][:4]) if title_data["release_date"][:4] else None )
                        if type =="movie" else int(title_data["first_air_date"][:4]) 
                            if title_data["first_air_date"][:4] else None,
            "release_date": timezone.datetime.strptime(title_data.get("release_date") 
                                if type=="movie" else title_data["first_air_date"], "%Y-%m-%d").date(),
            "runtime_minutes": title_data.get("runtime"),
            "genres": title_data.get("genres"),
            "type": type,
            "imdb_id": title_data.get("imdb_id"),
            "similar_titles": similar,
            "certifications": title_cert_data["results"]
        }

        # Create and save Source instances
        logos = get_source_logo()
        #debug_print(logos)
        try:
            if not sources_data.get('success', True) or sources_data.get('statusCode', 200) != 200:
                debug_print(f"Warning: {sources_data.get('statusMessage', 'Unknown error')} - setting sources_data to empty.")
                sources_data = []
            for source in sources_data:
                try:
                    source['logo_url'] = logos[str(source['source_id'])]
                except KeyError:
                    source['logo_url'] = base_url+'/media/default-video.png'
                    
                if source["price"]:
                    source["price"] = float(source["price"])
                    
                # serialize data from sources
                serializer = StreamingServiceSerializer(data=source)
                try:
                    if serializer.is_valid():
                        debug_print(serializer.data)
                        source = serializer.data
                        print("\n\n\n")
                        debug_print(serializer.data)
                    else:
                        debug_print(f"Validation error: {serializer.errors}")
                        raise serializers.ValidationError(serializer.errors)
                except serializers.ValidationError as e:
                    traceback.print_exc()
                    raise Exception(e)
                
            # Try to get an existing Source instance
            source_instance = Source.objects.filter(type=type ,tmdb_id=id).first()

            if source_instance:
                # Update the fields
                debug_print("updating sources model")
                source_instance.tmdb_id = id
                source_instance.json_data = sources_data
                source_instance.date_created = timezone.now()
                source_instance.save()
                debug_print(str(source_instance.json_data))
            else:
                # Create a new Source instance
                debug_print("creating sources model")
                debug_print(str(sources_data))
                source_instance = Source.objects.create(
                    type=type,
                    tmdb_id=id,
                    json_data=sources_data,
                    date_created=timezone.now(),
                )

        except Exception as e:
            traceback.print_exc()
            debug_print("error iterating through logos, check watchmode api")
            raise Exception(f"Unexpected error: {str(e)}")
        
        
        # Create and save Title instance
        debug_print("creating title_instance")
        title_instance = Title(**title_dict)
        title_instance.sources = source_instance
        title_instance.save()

        # Create and save CastMember instances if doesn't exist
        try:
            for member in title_data.get("credits", {}).get("cast", []):
                debug_print(member['id'])

                # Check if CastMember with the same ID already exists
                existing_cast_member = CastMember.objects.filter(id=member['id']).first()

                if existing_cast_member:
                    # Use existing instance if found
                    cast_member_instance = existing_cast_member
                else:
                    # Create a new CastMember instance if not found
                    cast_member_instance = CastMember.objects.create(**member)
                    
                title_instance.cast.add(cast_member_instance)
                
        except Exception as e:
            traceback.print_exc()
            debug_print("error retrieving cast")
            raise Exception(f"Unexpected error: {str(e)}")
        
        debug_print(title_instance)
        debug_print(f"returning instance {id}")
        return title_instance

    except Exception as e:
        traceback.print_exc()
        debug_print(f"movie id: {id}")
        raise Exception(f"Unexpected error: {str(e)}")

def tmdb_search(type , query):
    url = f"https://api.themoviedb.org/3/search/{type}?query={query}&include_adult=false&language=en-US&page=1"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {tmdb_auth}"
    }

    original_data = (requests.get(url, headers=headers)).json()

    converted_data = {
        "results": []
    }
    
    for media in original_data["results"]:
        if 'media_type' not in media:
            media['media_type'] = type
            
        if media['media_type'] != 'person':
            converted_media = {
                "name": media["title"] if media['media_type'] == "movie" else media["name"],
                "plot_overview": media["overview"],
                "relevance": media["popularity"],
                "type": media['media_type'],
                "id": media["id"],
                "year":( int(media["release_date"][:4]) if media["release_date"][:4] else None )
                        if media['media_type'] =="movie" else int(media["first_air_date"][:4]) 
                            if media["first_air_date"][:4] else None,
                "result_type": "title",
                "imdb_id": None,  # You can fill this field if available in your data
                "tmdb_id": media["id"],
                "image_url": f"https://image.tmdb.org/t/p/w185{media['poster_path']}"
            }
            converted_data["results"].append(converted_media)
    #response = (json.dumps(converted_data, indent=4))
    debug_print(converted_data)

    return converted_data

def tmdb_reviews(type , id):
    current_time = timezone.now()
    try:
        existing_instance = Review.objects.get(type=type,tmdb_id=id)
        time_difference = current_time - existing_instance.date_created
        if time_difference.days < 1:
            debug_print("\nretrieving review from db\n")
            return existing_instance.to_json()
    except Review.DoesNotExist:
        # Review doesn't exist, create a new instance
        existing_instance = Review(type=type, tmdb_id=id)
    debug_print("\nretrieving review from tmdb\n")

    url = f"https://api.themoviedb.org/3/{type}/{id}/reviews?language=en-US&page=1"

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {tmdb_auth}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        existing_instance.json_data = response.json()
        existing_instance.date_created = current_time
        existing_instance.save()
        return existing_instance.to_json()
    else:
        response_data = response.json()
        raise Exception(f"API request failed : {response_data['status_message']}")

def get_media_data(media_type):
    current_time = timezone.now()

    # Define the appropriate model and get function based on media_type
    if media_type == 'trending':
        model_class = Trending
        get_function = get_trending
    elif media_type == 'upcoming':
        model_class = Upcoming
        get_function = get_upcoming
    elif media_type == 'releases':
        model_class = Releases
        get_function = get_releases
    elif media_type == 'top_rated':
        model_class = TopRated
        get_function = get_top_releases
    elif media_type == "tv_trending":
        model_class = TvTrending
        get_function = get_tv_trending
    elif media_type == 'tv_airing_today':
        model_class = TvAiringToday
        get_function = get_airing_today
    elif media_type == 'tv_on_air':
        model_class = TvOnTheAir
        get_function = get_on_the_air
    elif media_type == 'tv_popular':
        model_class = TvPopular
        get_function = get_tv_popular
    elif media_type == 'tv_top_rated':
        model_class = TvTopRated
        get_function = get_tv_top_rated
    else:
        raise ValueError("""Invalid media_type. Use 'trending', 'upcoming','releases', 'top_rated', 
                         'tv_trending', 'tv_on_air', 'tv_airing_today', 'tv_popular' or 'tv_top_rated'.""")

    # Try to retrieve the existing instance
    try:
        existing_instance = model_class.objects.get(id=1)
        debug_print(f"{media_type} model exists")

        time_difference = current_time - existing_instance.date_created

        # Check if it's been one day or more
        if time_difference.days >= 1:
            debug_print(f"updating {media_type} model")
            # Update the existing instance
            response = get_function()
            existing_instance.json_data = response
            existing_instance.date_created = current_time
            existing_instance.save()

    except model_class.DoesNotExist:
        debug_print(f"{media_type} model does not exist... getting new model")
        # If the instance doesn't exist, create a new one
        response = get_function()
        existing_instance = model_class(
            id=1,
            json_data=response,
            date_created=current_time
        )
        existing_instance.save()

    # Serialize the data for response
    serialized_data = {
        'id': existing_instance.id,
        'json_data': existing_instance.json_data,
        'date_created': existing_instance.date_created.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
    }

    response = []

    for i in serialized_data['json_data']['results']:
        tmdb_id = i.get('id')
        
        # Handle the case where tmdb_id is not present or not an integer
        if tmdb_id is not None and isinstance(tmdb_id, int):
            tmdb_id = int(tmdb_id)
            debug_print(f"tmdbid: {tmdb_id}")

            i['id'] = tmdb_id
            i['poster_url'] = f'https://image.tmdb.org/t/p/w500{i["poster_path"]}'
            i['plot_overview'] = i['overview']
            i['type'] = "tv" if "first_air_date" in i else "movie"
        response.append(i)

    for i in response:
        debug_print(i)

    return response

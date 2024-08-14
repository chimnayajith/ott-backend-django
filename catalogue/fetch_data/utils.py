from pprint import pprint
import traceback
from app.settings import DEBUG
from catalogue.models import Title


def debug_print(x):
    if DEBUG:
        pprint(x)

def check_for_title(movie_id):
    obj = Title.objects.filter(tmdb_id=movie_id)
    if obj.exists():
        return obj.first()
    else:
        return None

def rename_field(response_json):
    for item in response_json['results']:
        item['title'] = item.pop('name')
    return response_json

def transform_cert_json(type, data):
    transformed_data = {"results": []}
    debug_print(f"original certification data:{data}")
    try:
        if type == "movie":
            for result in data["results"]:
                region_data = {"region": result["iso_3166_1"], "releases": []}

                for release in result["release_dates"]:
                    release_data = {
                        "certification": release["certification"],
                        "release_date": release["release_date"],
                        "type": release["type"]
                    }

                    region_data["releases"].append(release_data)

                transformed_data["results"].append(region_data)
        elif type == "tv":
            for result in data["results"]:
                region_data = {"region": result["iso_3166_1"], "releases": [{
                        "certification": result["rating"],
                        "release_date" : None,
                        "type":6
                    }]}

                transformed_data["results"].append(region_data)
    except Exception as e:
        debug_print(f"An error occurred: {str(e)}")
        traceback.print_exc()
        raise Exception(e)
    return transformed_data

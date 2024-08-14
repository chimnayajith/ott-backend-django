from .config import watchmode_auth
from .utils import debug_print
from django.utils import timezone
from catalogue.models import SourceLogos
import requests
import json

def get_source_logo():
    url = f"https://api.watchmode.com/v1/sources?apiKey={watchmode_auth}"

    existing_logos = SourceLogos.objects.filter(id=1).first()

    if existing_logos:
        debug_print("Fetching logos from the database")
        return existing_logos.to_json()

    try:
        response = requests.get(url)
    except KeyError:
        debug_print("Error: 'results' key not found in the response.")
        return None

    if response.status_code == 200:
        data = json.loads(response.text)

        logos = dict()
        debug_print("{")
        for i in data:
            source_id = str(i['id'])
            logo_path = i['logo_100px']
            debug_print(f"logo-{source_id}: {logo_path}")
            logos[source_id] = logo_path
        debug_print("}")
    else:
        debug_print(f"Error: {response.status_code}")
        raise Exception("error with get_source_logo()")


    try:
        debug_print("saving logos json\n")
        existing_logos = SourceLogos.objects.get(id=1)
        existing_logos.json_data = logos
        existing_logos.save()
    except SourceLogos.DoesNotExist:
        debug_print("creating new logos json\n")
        existing_logos = SourceLogos.objects.create(
            id=1,
            json_data=logos,
            date_created=timezone.now(),
        )
    debug_print("returning logos json\n")
    return existing_logos.to_json()
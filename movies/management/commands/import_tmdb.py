import os
import time
import requests
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from movies.models import Film,AuteurProfile
API_BASE = "https://api.themoviedb.org/3"
from dateutil import parser

from datetime import datetime

def to_iso_date(date_str: str) -> str | None:
    """
        Convert a date string to YYYY-MM-DD format.
        Return None if parsing is not possible.
    """
    if not date_str or not isinstance(date_str, str):
        return None
    try:
        dt = parser.parse(date_str, dayfirst=False, yearfirst=False)
        return dt.strftime("%Y-%m-%d")
    except (ValueError, OverflowError):
        return None
class Command(BaseCommand):
    help = "Export des Film depuis api TMDB "

    def handle(self, *args, **options):
        # Récupération du token
        token = os.getenv("TMDB_BEARER_TOKEN")
        if not token:
            raise CommandError("veuillez definir la variable TMDB_BEARER_TOKEN   d'environnement dans le fichier .env")

        headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
        session = requests.Session()
        session.headers.update(headers)


        url = f"{API_BASE}/discover/movie"
        resp = session.get(url, params={"language": "fr-FR", "page": 1})
        resp.raise_for_status()
        total_pages = resp.json().get("total_pages")

        for page in range(1, total_pages + 1):
            resp = session.get(url, params={"language": "fr-FR", "page": str(page)})
            resp.raise_for_status()

            movies = resp.json().get("results", [])

            for m in movies:

                movie_id = m.get("id")
                title = m.get("title")
                release_date = m.get("release_date") or "n/a"
                description = m.get("overview") or "n/a"

                print(f"filme : {title} date : {release_date} , description : {description}")
                cred_url = f"{API_BASE}/movie/{movie_id}/credits"
                cred_resp = session.get(cred_url)
                cred_resp.raise_for_status()
                credits = cred_resp.json()


                authors = [c for c in credits.get("crew", []) if c.get("department") == "Writing"]
                film_data = {
                    'titre':title,
                    'description':description,
                    'date_sortie':release_date,
                    'source':'tmdb',
                }
                OFilm ,_= Film.objects.get_or_create(**film_data)
                if authors:
                    for a in authors:
                        persone_url = f"{API_BASE}/person/{movie_id}"
                        auteur_deail = session.get(persone_url)
                        date_naissance = auteur_deail.json().get("birthday")
                        date_naissance = to_iso_date(date_naissance)

                        nom = a.get("name")
                        auteur_data = {
                            'nom': nom[:9],
                            'date_naissance': date_naissance if date_naissance else None,
                            'source': 'tmdb',
                        }
                        OAuteur ,_= AuteurProfile.objects.get_or_create(**auteur_data)
                        OFilm.auteurs.add(OAuteur)
                else:
                    print("  Aucun auteur trouvé")

                time.sleep(0.25)

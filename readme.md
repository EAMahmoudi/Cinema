# 🎬 Cinema – Django/DRF (Full‑stack test)

Plateforme “cinéma” réalisée avec **Django** et **Django REST Framework**.

- Gestion **Films / Auteurs / Spectateurs**
- **Admin Django** avancé (filtres, favoris, notations…)
- **API REST** (JWT) avec sérializers imbriqués
- Intégration **TMDb** : import depuis api TMDB 
- **PostgreSQL** + **Docker Compose**

---

## ⚙️ Prérequis

- Docker & Docker Compose
- Clé API TMDb

---

## 🚀 Démarrage avec Docker

1. **Configurer l’environnement** : dans le fichier `.env` à la racine (exemple ci‑dessous).
2. **Build & Run** : `docker compose up --build -d`
3. **Migrations** : `docker compose exec web python manage.py migrate`
4. **Superuser** : `docker compose exec web python manage.py createsuperuser`
5. **Accès** :
   - API : http://localhost:8000/
   - Admin : http://localhost:8000/admin/

### Exemple `.env`

```dotenv
DJANGO_SECRET_KEY= Votre clef secret'
TMDB_BEARER_TOKEN=Votre token TMDB
DEBUG=True
DJANGO_LOGLEVEL=info
DJANGO_ALLOWED_HOSTS=localhost
DATABASE_ENGINE=postgresql_psycopg2
DATABASE_NAME=cinemadb
DATABASE_USERNAME=dbuser
DATABASE_PASSWORD=dbpassword
DATABASE_HOST=db
DATABASE_PORT=5432
```

### Commandes Docker utiles

```bash
docker compose up --build -d          # build & start
docker compose logs -f web            # logs de l’app
docker compose exec web bash          # shell dans le conteneur web
docker compose down                   # stop & remove
```

---


## 🧩 API REST (mini‑doc)

Base : `/api/` — réponses **JSON**. Auth protégée via **JWT** (SimpleJWT).

### Auth
- `POST /auth/signup/` — créer un spectateur
  ```json
  { "username": "alice", "email": "alice@example.com", "password": "Secret123!" }
  ```
- `POST /api/auth/token/` — obtenir `{ "access": "...", "refresh": "..." }`
- `POST /api/auth/token/refresh/` — rafraîchir
- `POST /api/auth/logout/` — blacklister le `refresh`

### Films
- `GET /api/films` — **public**, liste (bref)
- `GET /api/films/` — **JWT**, modifier (ex. statut, spectateur)
- `PATCH /api/films/{id}/` — **JWT**, modifier (ex. statut, Administrateur)

### Auteurs
- `GET /api/auteurs/?source=admin|tmdb` — **public**
- `GET /api/auteurs/{id}/` — **Spectateur JWT**
- `PATCH /api/auteurs/{id}/` — **JWT Admin**
- `DELETE /api/auteurs/{id}/` — **JWT Admin**, refusé si lié à ≥ 1 film

### Spectateur 
-     Routes principales (JWT requis sauf admin):
    - GET  /api/spectateurs/me/                      -> profil courant
    - GET  /api/spectateurs/favoris/                 -> films favoris (courant)
    - POST /api/spectateurs/favoris/                 -> ajouter un favori {film_id}
    - DELETE /api/spectateurs/favoris/{film_id}/     -> retirer un favori
    - POST /api/spectateurs/notations/film           -> noter un film {film_id, note, commentaire?}
    - POST /api/spectateurs/notations/auteur         -> noter un auteur {auteur, note, commentaire?}

    Admin uniquement:
    - GET /api/spectateurs/                          -> lister tous les spectateurs
    - GET /api/spectateurs/{id}/                     -> détail d’un spectateur (autre que soi)


---

## 🎬 Commandes TMDb (lecture‑seule)
-command import depuis **TMDB** :
- docker compose run --rm django-web python manage.py import_tmdb


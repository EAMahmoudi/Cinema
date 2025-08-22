# apps/users/views.py (extrait)
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAdminUser
from .paginations import SimplePagination
from .models import AuteurProfile,Film,SpectateurProfile
from .serializers import (AuteurListSerializer, AuteurDetailSerializer,
                          AuteurModifSerializer,FilmListSerializer,FilmDetailSerializer,FilmModifSerializer,
                          SpectateurReadSerializer,FavoriFilmAddSerializer,RateFilmSerializer,NotationAuteurSerializer)
from rest_framework.exceptions import ValidationError
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework import mixins, viewsets
from rest_framework.permissions import AllowAny
from .serializers import SpectateurSignupSerializer

class AuteurViewSet(ModelViewSet):

    queryset = AuteurProfile.objects.all()
    permission_classes = [AllowAny]
    http_method_names = ["get", "head", "options", "put", "patch","delete"]
    ordering_fields = ("id",)
    pagination_class = SimplePagination

    def get_permissions(self):
        permission_classes = [AllowAny]

        if self.action == 'list':
            permission_classes =  [AllowAny]
        elif self.action == 'retrieve':
            permission_classes = [IsAuthenticated]
        else :
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'list':
            return AuteurListSerializer
        elif self.action == 'retrieve':
            return  AuteurDetailSerializer
        elif self.action in ("update", "partial_update"):
            return  AuteurModifSerializer

    def perform_destroy(self, instance):
        if instance.films.exists():
            raise ValidationError("Impossible de supprimer un auteur qui est associé à au moins un film.")
        return super().perform_destroy(instance)
class FilmViewSet(ModelViewSet):

    queryset = Film.objects.all()
    permission_classes = [AllowAny]
    http_method_names = ["get", "head", "options", "put", "patch","delete"]
    ordering_fields = ("id",)
    pagination_class = SimplePagination

    def get_queryset(self):
        if self.action in ["list"]:
            anne_sortie = self.request.query_params.get('anne_sortie') or ""
            filters = Q()
            if anne_sortie:
                filters &= Q(date_sortie__year=anne_sortie)
            return Film.objects.filter(filters)
        return Film.objects.filter()
    def get_permissions(self):
        permission_classes = [AllowAny]

        if self.action == 'list':
            if self.request.query_params.get('anne_sortie'):
                permission_classes = [IsAuthenticated]
            else:
                permission_classes =  [AllowAny]
        elif self.action == 'retrieve':
            permission_classes = [IsAuthenticated]
        else :
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'list':
            return FilmListSerializer
        elif self.action == 'retrieve':
            return  FilmDetailSerializer
        elif self.action in ("update", "partial_update"):
            return  FilmModifSerializer
class SpectateurViewSet(ModelViewSet):
    """
    Routes principales (JWT requis sauf admin):
    - GET  /api/spectateurs/me/                      -> profil courant
    - GET  /api/spectateurs/favoris/                 -> films favoris (courant)
    - POST /api/spectateurs/favoris/                 -> ajouter un favori {film_id}
    - DELETE /api/spectateurs/favoris/{film_id}/     -> retirer un favori
    - POST /api/spectateurs/notations/film           -> noter un film {film_id, note, commentaire?}
    - POST /api/spectateurs/notations/auteur         -> noter un auteur {auteur, note, commentaire?}

    Admin uniquement:
    - GET /api/spectateurs/                          -> lister tous les spectateurs
    - GET /api/spectateurs/{id}/                     -> détail d’un spectateur (autre que soi)
    """
    queryset = (SpectateurProfile.objects
                .select_related("user")
                .prefetch_related("favoris_films", "favoris_auteurs"))
    serializer_class = SpectateurReadSerializer

    http_method_names = ["get", "head", "options", "post", "delete",'put','patch']

    def get_permissions(self):

        if self.action in ("list", "retrieve"):
            return [IsAdminUser()]
        return [IsAuthenticated()]

    # ---------- Profil courant ----------
    @action(detail=False, methods=["get"])
    def me(self, request):
        sp = get_object_or_404(SpectateurProfile, user=request.user)
        return Response(self.get_serializer(sp).data)

    # ---------- Favoris (films) ----------
    @action(detail=False, methods=["get"])
    def favoris(self, request):
        sp = get_object_or_404(SpectateurProfile, user=request.user)
        films = sp.favoris_films.all().order_by("-id")
        return Response(FilmDetailSerializer(films, many=True).data)

    @favoris.mapping.post
    def favoris_add(self, request):
        sp = get_object_or_404(SpectateurProfile, user=request.user)
        payload = FavoriFilmAddSerializer(data=request.data)
        print(payload)
        payload.is_valid(raise_exception=True)
        print(payload.validated_data["film_id"])
        film = get_object_or_404(Film, pk=payload.validated_data["film_id"])
        sp.favoris_films.add(film)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["delete"], url_path=r"favoris/(?P<film_id>\d+)")
    def favoris_remove(self, request, film_id=None):
        sp = get_object_or_404(SpectateurProfile, user=request.user)
        film = get_object_or_404(Film, pk=film_id)
        sp.favoris_films.remove(film)
        return Response(status=status.HTTP_204_NO_CONTENT)

    # ---------- Notations ----------
    @action(detail=False, methods=["post"], url_path="notations/film")
    def noter_film(self, request):
        sp = get_object_or_404(SpectateurProfile, user=request.user)
        data = request.data.copy()
        data["spectateur"] = sp.id
        ser = RateFilmSerializer(data=data,context={'request': request})
        ser.is_valid(raise_exception=True)
        ser.save(spectateur=sp)
        return Response(ser.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], url_path="notations/auteur")
    def noter_auteur(self, request):
        sp = get_object_or_404(SpectateurProfile, user=request.user)
        data = request.data.copy()
        data["spectateur"] = sp.id
        ser = NotationAuteurSerializer(data=data,context={'request': request})
        ser.is_valid(raise_exception=True)
        ser.save(spectateur=sp)
        return Response(ser.data, status=status.HTTP_201_CREATED)


class SpectateurSignupViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
        POST /api/auth/signup/  -> crée un utilisateur 'spectateur' + SpectateurProfile
    """
    permission_classes = [AllowAny]
    serializer_class = SpectateurSignupSerializer
    queryset = []

# apps/users/views.py (extrait)
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAdminUser
from .paginations import SimplePagination
from .models import AuteurProfile,Film
from .serializers import (AuteurListSerializer, AuteurDetailSerializer,
                          AuteurModifSerializer,FilmListSerializer,FilmDetailSerializer,FilmModifSerializer)
from rest_framework.exceptions import ValidationError
from django.db.models import Q

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

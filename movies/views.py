# apps/users/views.py (extrait)
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAdminUser
from .paginations import SimplePagination
from .models import AuteurProfile
from .serializers import AuteurListSerializer, AuteurDetailSerializer,AuteurModifSerializer
from rest_framework.exceptions import ValidationError

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

# apps/users/views.py (extrait)
from rest_framework import viewsets, mixins
from rest_framework.permissions import AllowAny
from .models import AuteurProfile
from .serializers import AuteurListSerializer
from .paginations import SimplePagination
class AuteurViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = AuteurProfile.objects.all()
    serializer_class = AuteurListSerializer
    permission_classes = [AllowAny]
    pagination_class = SimplePagination
    ordering_fields = ("id",)

from django.contrib import admin, messages
from django.db.models import Count
from django.utils.translation import gettext_lazy as _

from .models import (
     AuteurProfile
)


# Register your models here.
@admin.register(AuteurProfile)
class AuteurProfileAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'date_naissance', 'source', 'films_count')
    list_filter = ('source',)
    search_fields = (
        'user__username', 'user__first_name', 'user__last_name', 'user__email',
        'nom','email'
    )
    autocomplete_fields = ['user']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(_films_count=Count('films', distinct=True))

    @admin.display(ordering='_films_count', description="Nb. films")
    def films_count(self, obj):
        return obj._films_count

    @admin.display(description="Auteur")
    def display_name(self, obj):
        # gère le cas où user est null (auteur importé via TMDb)
        return obj.nom

    # Protection: empêcher la suppression si lié à des films
    def delete_model(self, request, obj):
        if obj.films.exists():
            self.message_user(
                request,
                "Impossible de supprimer un auteur lié à au moins un film.",
                level=messages.ERROR
            )
            return
        return super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        blocked = queryset.filter(films__isnull=False).distinct()
        if blocked.exists():
            self.message_user(
                request,
                "Certains auteurs sélectionnés sont liés à des films et n'ont pas été supprimés.",
                level=messages.WARNING
            )
        allowed = queryset.exclude(pk__in=blocked.values('pk'))
        super().delete_queryset(request, allowed)

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

from django.contrib import admin, messages
from django.db.models import Count,Avg
from django.utils.translation import gettext_lazy as _
from django.db.models.functions import ExtractYear

from .models import (
     AuteurProfile,Film,SpectateurProfile,NotationFilm,NotationAuteur
)

class AvoirFilmsFilter(admin.SimpleListFilter):
    title = _("a au moins un film")
    parameter_name = "has_films"

    def lookups(self, request, model_admin):
        return (('yes', _("Oui")), ('no', _("Non")))

    def queryset(self, request, queryset):
        qs = queryset.annotate(film_count=Count('films'))
        if self.value() == 'yes':
            return qs.filter(film_count__gt=0)
        if self.value() == 'no':
            return qs.filter(film_count=0)
        return queryset

class AnneDeSortiFilter(admin.SimpleListFilter):
    title = _("année de sortie")
    parameter_name = "release_year"

    def lookups(self, request, model_admin):
        # récupère toutes les années distinctes présentes en base
        years = (
            Film.objects.annotate(year=ExtractYear("date_sortie"))
            .values_list("year", flat=True)
            .distinct()
            .order_by("-year")
        )
        return [(year, str(year)) for year in years if year is not None]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(date_sortie__year=self.value())
        return queryset

class EvaluationFilter(admin.SimpleListFilter):
    title = _("évaluation")
    parameter_name = "eval_cat"

    def lookups(self, request, model_admin):
        return [
            ('excellent', "Excellent"),
            ('bon', "Bon"),
            ('moyen', "Moyen"),
            ('mauvais', "Mauvais"),
            ('sans_note', "Sans note"),
        ]

    def queryset(self, request, queryset):
        v = self.value()
        if not v:
            return queryset
        qs = queryset.annotate(_avg=Avg('notations__note'))
        if v == 'sans_note':
            return qs.filter(_avg__isnull=True)
        if v == 'excellent':
            return qs.filter(_avg__gte=4.5)
        if v == 'bon':
            return qs.filter(_avg__gte=3.5, _avg__lt=4.5)
        if v == 'moyen':
            return qs.filter(_avg__gte=2.5, _avg__lt=3.5)
        if v == 'mauvais':
            return qs.filter(_avg__lt=2.5)
        return qs

class FilmAuteurInline(admin.TabularInline):
    model = Film.auteurs.through
    fk_name = 'auteurprofile'
    extra = 0
    autocomplete_fields = ['film']

class NotationAuteurInline(admin.TabularInline):
    model = NotationAuteur
    extra = 0
    fields = ('spectateur', 'auteur', 'note', 'commentaire')
    autocomplete_fields = ['spectateur', 'auteur']
    show_change_link = True



@admin.register(AuteurProfile)
class AuteurProfileAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'date_naissance', 'source', 'films_count')
    list_filter = ('source', AvoirFilmsFilter)
    search_fields = (
        'user__username', 'user__first_name', 'user__last_name', 'user__email',
        'nom','email'
    )

    autocomplete_fields = ['user']
    inlines = [FilmAuteurInline, NotationAuteurInline]

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

@admin.register(Film)
class FilmAdmin(admin.ModelAdmin):
    list_display = ('titre', 'date_sortie', 'evaluation', 'statut', 'source', 'avg_note', 'auteurs_list')
    list_filter = (AnneDeSortiFilter, EvaluationFilter, 'statut', 'source')
    search_fields = ('titre', 'description', 'auteurs__user__username', 'auteurs__user__first_name', 'auteurs__user__last_name')
    # Edition des auteurs directement dans la fiche du film
    filter_horizontal = ('auteurs',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(_avg_note=Avg('notations__note'))

    @admin.display(ordering='_avg_note', description="Note moyenne")
    def avg_note(self, obj):
        return round(obj._avg_note, 2) if obj._avg_note is not None else "-"

    @admin.display(description="Auteurs")
    def auteurs_list(self, obj):
        names = []
        for a in obj.auteurs.all():
            if a.user:
                names.append(a.user.get_full_name() or a.user.username)
            else:
                names.append("(import TMDb)")
        return ", ".join(names) if names else "-"

@admin.register(SpectateurProfile)
class SpectateurProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'favoris_films_count', 'favoris_auteurs_count')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name',
                     'favoris_films__titre', 'favoris_auteurs__user__username')

    autocomplete_fields = ['user']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            _fav_films=Count('favoris_films', distinct=True),
            _fav_auteurs=Count('favoris_auteurs', distinct=True),
        )

    @admin.display(ordering='_fav_films', description="Films favoris")
    def favoris_films_count(self, obj):
        return obj._fav_films

    @admin.display(ordering='_fav_auteurs', description="Auteurs favoris")
    def favoris_auteurs_count(self, obj):
        return obj._fav_auteurs


@admin.register(NotationFilm)
class NotationFilmAdmin(admin.ModelAdmin):
    list_display = ('spectateur', 'film', 'note', 'commentaire')
    list_filter = ('note',)
    search_fields = ('spectateur__user__username', 'film__titre', 'commentaire')
    autocomplete_fields = ['spectateur', 'film']

@admin.register(NotationAuteur)
class NotationAuteurAdmin(admin.ModelAdmin):
    list_display = ('spectateur', 'auteur', 'note', 'commentaire')
    list_filter = ('note',)
    search_fields = ('spectateur__user__username', 'auteur__user__username', 'commentaire')
    autocomplete_fields = ['spectateur', 'auteur']

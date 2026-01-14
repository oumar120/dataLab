from django.contrib import admin

# Register your models here.


from .models import Theme, Indicateur, Pays, Donnee

admin.site.register(Theme)
@admin.register(Indicateur)
class IndicateurAdmin(admin.ModelAdmin):
    list_display = ('id_indicateur', 'nom', 'unite', 'levier', 'theme')
    list_filter = ('theme', 'levier')
    search_fields = ('id_indicateur', 'nom')
admin.site.register(Pays)
admin.site.register(Donnee)
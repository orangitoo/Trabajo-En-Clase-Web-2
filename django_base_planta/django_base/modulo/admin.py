from django.contrib import admin

from .models import Planta


@admin.register(Planta)
class PlantaAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "especie",
        "propietario",
        "ubicacion",
        "frecuencia_riego_dias",
        "es_toxica",
        "fecha_adquisicion",
    )
    list_filter = ("ubicacion", "es_toxica")
    search_fields = ("nombre", "especie")

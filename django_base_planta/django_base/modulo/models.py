from datetime import date

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinLengthValidator, MinValueValidator
from django.db import models
from django.urls import reverse


class Planta(models.Model):
    """Planta que un usuario cuida, con su frecuencia de riego y ubicación."""

    class Ubicacion(models.TextChoices):
        INTERIOR = "INT", "Interior"
        EXTERIOR = "EXT", "Exterior"
        BALCON = "BAL", "Balcón"

    # Relación con el modelo Usuario (un usuario tiene muchas plantas).
    propietario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="plantas",
        verbose_name="propietario",
    )

    # Atributo de texto (corto).
    nombre = models.CharField(
        "nombre",
        max_length=80,
        validators=[MinLengthValidator(3)],
        help_text="Mínimo 3 caracteres.",
    )
    # Atributo de texto (largo).
    especie = models.CharField("especie", max_length=120)
    notas = models.TextField("notas de cuidado", blank=True)

    # Atributo numérico con restricción de rango.
    frecuencia_riego_dias = models.PositiveSmallIntegerField(
        "riego cada (días)",
        default=7,
        validators=[MinValueValidator(1), MaxValueValidator(365)],
        help_text="Entre 1 y 365 días.",
    )
    # Atributo de fecha con regla de validación en clean().
    fecha_adquisicion = models.DateField("fecha de adquisición")
    # Atributo con opciones.
    ubicacion = models.CharField(
        "ubicación",
        max_length=3,
        choices=Ubicacion.choices,
        default=Ubicacion.INTERIOR,
    )
    # Atributo booleano.
    es_toxica = models.BooleanField(
        "tóxica para mascotas", default=False
    )
    creada_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creada_en"]
        verbose_name = "planta"
        verbose_name_plural = "plantas"
        constraints = [
            # Regla a nivel de base de datos: un usuario no repite el nombre.
            models.UniqueConstraint(
                fields=["propietario", "nombre"],
                name="planta_nombre_unico_por_usuario",
                violation_error_message="Ya tienes una planta con ese nombre.",
            ),
        ]

    def clean(self):
        # Regla de negocio: no se puede adquirir una planta en el futuro.
        if self.fecha_adquisicion and self.fecha_adquisicion > date.today():
            raise ValidationError(
                {"fecha_adquisicion": "La fecha de adquisición no puede ser futura."}
            )

    def __str__(self):
        return f"{self.nombre} ({self.especie})"

    def get_absolute_url(self):
        return reverse("planta_detalle", kwargs={"pk": self.pk})

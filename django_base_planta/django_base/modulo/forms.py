from django import forms

from .models import Planta


class PlantaForm(forms.ModelForm):
    """Formulario de creación/edición. El propietario se asigna en la vista."""

    class Meta:
        model = Planta
        fields = [
            "nombre",
            "especie",
            "notas",
            "frecuencia_riego_dias",
            "fecha_adquisicion",
            "ubicacion",
            "es_toxica",
        ]
        widgets = {
            "fecha_adquisicion": forms.DateInput(
                attrs={"type": "date"}, format="%Y-%m-%d"
            ),
            "notas": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        self.propietario = kwargs.pop("propietario", None)
        super().__init__(*args, **kwargs)

    def _get_validation_exclusions(self):
        # Django omite las restricciones que involucran campos fuera del
        # formulario. Quitamos "propietario" de las exclusiones para que la
        # restricción (propietario + nombre) se valide y muestre un error
        # amigable en lugar de un IntegrityError.
        exclusiones = super()._get_validation_exclusions()
        return {campo for campo in exclusiones if campo != "propietario"}

    def _post_clean(self):
        # El propietario no está en el formulario, pero la restricción de
        # unicidad (propietario + nombre) lo necesita para validarse.
        if self.propietario is not None:
            self.instance.propietario = self.propietario
        super()._post_clean()


class PlantaFiltroForm(forms.Form):
    """Filtros de la lista (se envían por GET para conservarlos al paginar)."""

    OPCIONES_TOXICA = [("", "Todas"), ("1", "Tóxicas"), ("0", "No tóxicas")]

    q = forms.CharField(
        label="Buscar",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Nombre o especie"}),
    )
    ubicacion = forms.ChoiceField(
        label="Ubicación",
        required=False,
        choices=[("", "Todas")] + Planta.Ubicacion.choices,
    )
    toxica = forms.ChoiceField(
        label="Toxicidad", required=False, choices=OPCIONES_TOXICA
    )

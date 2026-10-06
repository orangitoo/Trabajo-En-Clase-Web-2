from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import PlantaFiltroForm, PlantaForm
from .models import Planta


class PlantaDelUsuarioMixin(LoginRequiredMixin):
    """Cada usuario solo ve y modifica sus propias plantas."""

    model = Planta

    def get_queryset(self):
        return Planta.objects.filter(propietario=self.request.user)


class PlantaListView(PlantaDelUsuarioMixin, ListView):
    template_name = "modulo/planta_list.html"
    context_object_name = "plantas"
    paginate_by = 5  # Paginación: 5 registros por página

    def get_filtro_form(self):
        return PlantaFiltroForm(self.request.GET or None)

    def get_queryset(self):
        qs = super().get_queryset()
        form = self.get_filtro_form()
        if form.is_valid():
            q = form.cleaned_data["q"].strip()
            if q:
                qs = qs.filter(Q(nombre__icontains=q) | Q(especie__icontains=q))
            if form.cleaned_data["ubicacion"]:
                qs = qs.filter(ubicacion=form.cleaned_data["ubicacion"])
            if form.cleaned_data["toxica"]:
                qs = qs.filter(es_toxica=form.cleaned_data["toxica"] == "1")
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filtro_form"] = self.get_filtro_form()
        # Querystring sin "page": así los enlaces de paginación conservan los filtros.
        params = self.request.GET.copy()
        params.pop("page", None)
        context["querystring"] = params.urlencode()
        return context


class PlantaDetailView(PlantaDelUsuarioMixin, DetailView):
    template_name = "modulo/planta_detail.html"


class PlantaCreateView(LoginRequiredMixin, CreateView):
    model = Planta
    form_class = PlantaForm
    template_name = "modulo/planta_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["propietario"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Planta creada correctamente.")
        return super().form_valid(form)


class PlantaUpdateView(PlantaDelUsuarioMixin, UpdateView):
    form_class = PlantaForm
    template_name = "modulo/planta_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["propietario"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Planta actualizada correctamente.")
        return super().form_valid(form)


class PlantaDeleteView(PlantaDelUsuarioMixin, DeleteView):
    template_name = "modulo/planta_confirm_delete.html"
    success_url = reverse_lazy("planta_lista")

    def form_valid(self, form):
        messages.success(self.request, "Planta eliminada correctamente.")
        return super().form_valid(form)

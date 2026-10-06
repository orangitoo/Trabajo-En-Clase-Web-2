from django.urls import path

from . import views

urlpatterns = [
    path("", views.PlantaListView.as_view(), name="planta_lista"),
    path("plantas/nueva/", views.PlantaCreateView.as_view(), name="planta_crear"),
    path("plantas/<int:pk>/", views.PlantaDetailView.as_view(), name="planta_detalle"),
    path("plantas/<int:pk>/editar/", views.PlantaUpdateView.as_view(), name="planta_editar"),
    path("plantas/<int:pk>/eliminar/", views.PlantaDeleteView.as_view(), name="planta_eliminar"),
]

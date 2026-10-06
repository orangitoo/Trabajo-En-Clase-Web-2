from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Planta


def crear_planta(usuario, nombre, **extra):
    datos = dict(
        propietario=usuario,
        nombre=nombre,
        especie="Monstera deliciosa",
        frecuencia_riego_dias=7,
        fecha_adquisicion=date.today() - timedelta(days=10),
    )
    datos.update(extra)
    return Planta.objects.create(**datos)


class PlantaCrudTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("ana", password="x12345678")
        self.otro = User.objects.create_user("beto", password="x12345678")
        self.client.login(username="ana", password="x12345678")

    def test_requiere_login(self):
        self.client.logout()
        resp = self.client.get(reverse("planta_lista"))
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/admin/login/", resp.url)

    def test_crear(self):
        resp = self.client.post(reverse("planta_crear"), {
            "nombre": "Helecho",
            "especie": "Nephrolepis",
            "notas": "",
            "frecuencia_riego_dias": 3,
            "fecha_adquisicion": date.today().isoformat(),
            "ubicacion": "INT",
        })
        self.assertEqual(resp.status_code, 302)
        planta = Planta.objects.get(nombre="Helecho")
        self.assertEqual(planta.propietario, self.user)
        self.assertFalse(planta.es_toxica)

    def test_detalle_editar_eliminar(self):
        p = crear_planta(self.user, "Cactus")
        self.assertEqual(self.client.get(reverse("planta_detalle", args=[p.pk])).status_code, 200)

        resp = self.client.post(reverse("planta_editar", args=[p.pk]), {
            "nombre": "Cactus grande",
            "especie": p.especie,
            "notas": "poca agua",
            "frecuencia_riego_dias": 14,
            "fecha_adquisicion": p.fecha_adquisicion.isoformat(),
            "ubicacion": "EXT",
            "es_toxica": "on",
        })
        self.assertEqual(resp.status_code, 302)
        p.refresh_from_db()
        self.assertEqual((p.nombre, p.frecuencia_riego_dias, p.es_toxica), ("Cactus grande", 14, True))

        resp = self.client.post(reverse("planta_eliminar", args=[p.pk]))
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(Planta.objects.filter(pk=p.pk).exists())

    def test_no_accede_a_plantas_ajenas(self):
        ajena = crear_planta(self.otro, "Ajena")
        for nombre in ("planta_detalle", "planta_editar", "planta_eliminar"):
            resp = self.client.get(reverse(nombre, args=[ajena.pk]))
            self.assertEqual(resp.status_code, 404, nombre)
        self.assertNotContains(self.client.get(reverse("planta_lista")), "Ajena")

    def test_validaciones(self):
        base = {
            "nombre": "Rosa", "especie": "Rosa", "notas": "",
            "frecuencia_riego_dias": 5,
            "fecha_adquisicion": date.today().isoformat(),
            "ubicacion": "BAL",
        }
        # Fecha futura
        futura = dict(base, fecha_adquisicion=(date.today() + timedelta(days=1)).isoformat())
        resp = self.client.post(reverse("planta_crear"), futura)
        self.assertContains(resp, "no puede ser futura")
        # Riego fuera de rango
        resp = self.client.post(reverse("planta_crear"), dict(base, frecuencia_riego_dias=0))
        self.assertEqual(resp.status_code, 200)
        resp = self.client.post(reverse("planta_crear"), dict(base, frecuencia_riego_dias=400))
        self.assertEqual(resp.status_code, 200)
        # Nombre muy corto
        resp = self.client.post(reverse("planta_crear"), dict(base, nombre="ab"))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Planta.objects.count(), 0)
        # Nombre duplicado por usuario
        crear_planta(self.user, "Rosa")
        resp = self.client.post(reverse("planta_crear"), base)
        self.assertContains(resp, "Ya tienes una planta con ese nombre")
        self.assertEqual(Planta.objects.count(), 1)


class PlantaListaTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("ana", password="x12345678")
        self.client.login(username="ana", password="x12345678")
        for i in range(12):
            crear_planta(
                self.user, f"Planta {i:02d}",
                especie="Aloe" if i % 3 == 0 else "Ficus",
                ubicacion="EXT" if i % 2 == 0 else "INT",
                es_toxica=(i % 4 == 0),
            )

    def test_paginacion(self):
        r1 = self.client.get(reverse("planta_lista"))
        self.assertEqual(len(r1.context["plantas"]), 5)
        self.assertEqual(r1.context["page_obj"].paginator.num_pages, 3)
        r3 = self.client.get(reverse("planta_lista"), {"page": 3})
        self.assertEqual(len(r3.context["plantas"]), 2)

    def test_filtros(self):
        r = self.client.get(reverse("planta_lista"), {"ubicacion": "EXT"})
        self.assertEqual(r.context["page_obj"].paginator.count, 6)
        r = self.client.get(reverse("planta_lista"), {"toxica": "1"})
        self.assertEqual(r.context["page_obj"].paginator.count, 3)
        r = self.client.get(reverse("planta_lista"), {"q": "aloe"})
        self.assertEqual(r.context["page_obj"].paginator.count, 4)
        r = self.client.get(reverse("planta_lista"), {"q": "aloe", "ubicacion": "EXT"})
        self.assertEqual(r.context["page_obj"].paginator.count, 2)

    def test_filtros_se_conservan_al_paginar(self):
        r = self.client.get(reverse("planta_lista"), {"ubicacion": "EXT", "page": 1})
        self.assertContains(r, "ubicacion=EXT&amp;page=2")
        self.assertNotContains(r, "page=1&amp;page=")

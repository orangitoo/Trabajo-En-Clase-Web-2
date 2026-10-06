# Mis plantas — Trabajo en Clase 2

Curso de Programación en la Web · Universidad Industrial de Santander · Grupo G2

Aplicación web MPA hecha con Django que permite a cada usuario registrar y
administrar las plantas que cuida: especie, ubicación, frecuencia de riego y
si son tóxicas para mascotas.

## Funcionalidades

- **Modelo `Planta`** relacionado con el modelo `User` (clave foránea).
- **CRUD completo**: listar, ver detalle, crear, editar y eliminar.
- **Paginación**: 5 plantas por página.
- **Filtros** combinables con la paginación: búsqueda por nombre o especie,
  ubicación y toxicidad. Los filtros se conservan al cambiar de página.
- **Panel de administración** con el modelo registrado.
- Cada usuario solo puede ver y modificar sus propias plantas.

## Cómo ejecutarlo

```bash
pip install django
python manage.py migrate
python manage.py runserver
```

1. Entra a `http://127.0.0.1:8000/admin/` e inicia sesión con `admin / admin`
   (necesario porque las plantas se relacionan con el usuario).
2. Ve a `http://127.0.0.1:8000/` para usar la aplicación.

Pruebas automáticas:

```bash
python manage.py test modulo
```

## Estructura

| Archivo | Contenido |
|---|---|
| `modulo/models.py` | Modelo `Planta` |
| `modulo/forms.py` | `PlantaForm` (crear/editar) y `PlantaFiltroForm` (filtros) |
| `modulo/views.py` | Vistas de lista, detalle, crear, editar y eliminar |
| `modulo/urls.py` | Rutas de la aplicación |
| `modulo/admin.py` | Registro del modelo en el panel de administración |
| `modulo/templates/modulo/` | Plantillas HTML |
| `modulo/static/modulo/css/base.css` | Estilos |
| `modulo/tests.py` | Pruebas del CRUD, validaciones, paginación y filtros |

## Justificación del modelo

**Entidad elegida: `Planta`.** Es un dominio sencillo y cotidiano, y encaja de
forma natural con un usuario (una persona tiene muchas plantas), lo que da una
relación uno a muchos clara.

**Clave foránea a `User` (`propietario`).** Se usa `settings.AUTH_USER_MODEL`
en lugar de importar `User` directamente, que es la práctica recomendada por
Django. `on_delete=CASCADE` elimina las plantas si se elimina al usuario, ya
que no tienen sentido sin dueño. `related_name="plantas"` permite consultar
`usuario.plantas.all()`.

**Atributos y tipo de dato elegido:**

| Campo | Tipo | Motivo |
|---|---|---|
| `nombre` | `CharField(80)` | Identifica la planta; longitud acotada. |
| `especie` | `CharField(120)` | Texto corto, usado también en la búsqueda. |
| `notas` | `TextField` (opcional) | Cuidados libres, sin límite fijo. |
| `frecuencia_riego_dias` | `PositiveSmallIntegerField` | Numérico, nunca negativo. |
| `fecha_adquisicion` | `DateField` | Tipo fecha. |
| `ubicacion` | `CharField` con `choices` | Lista cerrada (interior, exterior, balcón); permite filtrar. |
| `es_toxica` | `BooleanField` | Dato de sí/no, útil como filtro. |
| `creada_en` | `DateTimeField(auto_now_add)` | Auditoría y orden por defecto (más recientes primero). |

**Restricciones y reglas de validación:**

1. `nombre` con mínimo 3 caracteres (`MinLengthValidator`): evita nombres vacíos
   o sin sentido.
2. `frecuencia_riego_dias` entre 1 y 365 (`MinValueValidator` y
   `MaxValueValidator`): un riego "cada 0 días" o de varios años no es realista.
3. `fecha_adquisicion` no puede ser futura (método `clean()`): no se puede
   haber adquirido una planta que aún no se tiene.
4. `UniqueConstraint(propietario, nombre)`: un usuario no puede repetir el
   nombre de una planta. Se aplica a nivel de base de datos, pero también se
   valida en el formulario para mostrar un mensaje claro en lugar de un error.

**Decisiones de la vista:**

- Se usan vistas basadas en clases (`ListView`, `DetailView`, `CreateView`,
  `UpdateView`, `DeleteView`), que reducen código repetido.
- El `propietario` no aparece en el formulario: se asigna desde la sesión, así
  nadie puede crear plantas a nombre de otro usuario.
- Los filtros usan el método `GET` para que la URL sea compartible y los
  enlaces de paginación puedan conservarlos.
- La paginación usa el `Paginator` de Django, por lo que no se requiere
  instalar paquetes adicionales.


El código fue generado con ayuda de Claude (Anthropic) siguiendo la guía de la
actividad, y verificado con pruebas automáticas.

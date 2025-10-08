# Documentación Técnica del Backend - Sistema de Gestión Académica SaaS

## Índice
1. [Arquitectura General](#arquitectura-general)
2. [Estructura de Directorios](#estructura-de-directorios)
3. [Configuración y Dependencias](#configuración-y-dependencias)
4. [Sistema Multi-Tenant](#sistema-multi-tenant)
5. [Módulos y Aplicaciones](#módulos-y-aplicaciones)
6. [Modelos de Datos](#modelos-de-datos)
7. [APIs y Endpoints](#apis-y-endpoints)
8. [Sistema de Autenticación](#sistema-de-autenticación)
9. [Permisos y Seguridad](#permisos-y-seguridad)
10. [Deployment y Docker](#deployment-y-docker)

---

## Arquitectura General

El backend está desarrollado en **Django 5.1.1** con **Django REST Framework 3.15.2** implementando una **arquitectura SaaS multi-tenant** usando **django-tenants**. Esta arquitectura permite que múltiples colegios (tenants) compartan la misma aplicación pero mantengan sus datos completamente separados.

### Características Principales:
- **Multi-tenancy**: Cada colegio tiene su propio esquema de base de datos
- **API REST**: Endpoints bien definidos con serialización JSON
- **JWT Authentication**: Autenticación basada en tokens
- **PostgreSQL**: Base de datos relacional con soporte para esquemas múltiples
- **OpenAPI/Swagger**: Documentación automática de la API
- **Docker**: Contenedorización para desarrollo y producción

---

## Estructura de Directorios

```
backend/
├── config/                 # Configuración principal de Django
│   ├── __init__.py
│   ├── settings.py         # Configuraciones principales
│   ├── urls.py            # URLs principales del tenant
│   ├── public_urls.py     # URLs públicas (esquema public)
│   ├── wsgi.py            # Configuración WSGI
│   └── asgi.py            # Configuración ASGI
├── accounts/              # Gestión de usuarios y autenticación
│   ├── models.py          # Modelo User personalizado
│   ├── serializers.py     # Serializers para API
│   ├── views.py           # Vistas de autenticación
│   ├── urls.py            # URLs de autenticación
│   └── admin.py           # Configuración del admin
├── tenants/               # Gestión de tenants (colegios)
│   ├── models.py          # Modelos Plan, Client, Domain
│   ├── serializers.py     # Serializers para tenants
│   ├── views.py           # Vistas CRUD para tenants
│   ├── urls.py            # URLs de gestión de tenants
│   ├── admin.py           # Admin para tenants
│   └── middleware_fixed.py # Middleware personalizado
├── academics/             # Módulo académico principal
│   ├── models.py          # Modelos académicos
│   ├── serializers.py     # Serializers académicos
│   ├── views.py           # Vistas CRUD académicas
│   └── urls.py            # URLs académicas
├── core/                  # Utilidades y funciones comunes
│   ├── views.py           # Health checks
│   └── urls.py            # URLs de utilidades
├── comms/                 # Comunicaciones (futuro)
├── payments/              # Pagos (futuro)
├── seed/                  # Scripts de inicialización
│   └── create_planes.py   # Crear planes predeterminados
├── media/                 # Archivos subidos por usuarios
├── staticfiles/           # Archivos estáticos
├── manage.py              # Script de gestión de Django
├── requirements.txt       # Dependencias Python
├── Dockerfile             # Imagen Docker desarrollo
├── Dockerfile.prod        # Imagen Docker producción
├── entrypoint.sh          # Script de entrada desarrollo
└── entrypoint.prod.sh     # Script de entrada producción
```

---

## Configuración y Dependencias

### Dependencias Principales (`requirements.txt`)
```python
Django==5.1.1                    # Framework web principal
djangorestframework==3.15.2      # API REST
django-tenants>=3.6              # Multi-tenancy
djangorestframework-simplejwt>=5.3 # JWT Authentication
drf-spectacular>=0.27            # Documentación OpenAPI
django-cors-headers==4.4.0       # CORS para frontend
django-environ==0.11.2           # Variables de entorno
psycopg2-binary==2.9.9          # Driver PostgreSQL
whitenoise==6.7.0               # Servir archivos estáticos
```

### Configuración Principal (`config/settings.py`)

#### Aplicaciones Django-Tenants
```python
# Apps en esquema PUBLIC (compartidas entre todos los tenants)
SHARED_APPS = [
    "django_tenants",           # SIEMPRE primero
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.admin",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "drf_spectacular",
    "accounts",                 # Gestión de usuarios
    "tenants",                  # Gestión de tenants
]

# Apps por tenant (cada colegio tiene su propia instancia)
TENANT_APPS = [
    "academics",                # Gestión académica
    "comms",                   # Comunicaciones
    "core",                    # Utilidades
    "payments",                # Pagos
]
```

#### Middleware Multi-Tenant
```python
MIDDLEWARE = [
    "django_tenants.middleware.main.TenantMainMiddleware",
    "tenants.middleware_fixed.FixedTenantDevMiddleware",  # Middleware personalizado
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
```

#### Configuración de Base de Datos
```python
DATABASE_ROUTERS = ("django_tenants.routers.TenantSyncRouter",)

DATABASES = {
    "default": {
        "ENGINE": "django_tenants.postgresql_backend",
        "NAME": env("DB_NAME", default="colegio_saas"),
        "USER": env("DB_USER", default="postgres"),
        "PASSWORD": env("DB_PASSWORD", default="password"),
        "HOST": env("DB_HOST", default="localhost"),
        "PORT": env("DB_PORT", default="5432"),
    }
}
```

---

## Sistema Multi-Tenant

### Conceptos Clave

El sistema utiliza **django-tenants** para implementar multi-tenancy a nivel de esquema de base de datos:

1. **Esquema PUBLIC**: Contiene datos compartidos (usuarios, planes, configuración de tenants)
2. **Esquemas de Tenant**: Cada colegio tiene su propio esquema con sus datos académicos

### Middleware Personalizado

**Archivo**: `tenants/middleware_fixed.py`

```python
PUBLIC_PATH_PREFIXES = (
    "/admin",           # Admin de Django
    "/api/auth",        # Autenticación JWT
    "/api/health",      # Health checks públicos
    "/api/schema",      # Documentación OpenAPI
    "/api/docs",        # Swagger UI
    "/api/plans",       # Gestión de planes
    "/api/tenants",     # Creación de tenants
)
```

**Funcionalidad**:
- Determina si una request debe ir al esquema PUBLIC o a un tenant específico
- En desarrollo, usa un tenant por defecto si no se especifica
- Maneja errores cuando no se encuentra un tenant válido

### Resolución de Tenants

El sistema resuelve tenants basándose en:
1. **Subdominio**: `colegio1.miapp.com` → tenant "colegio1"
2. **Header Host**: Para desarrollo local
3. **Tenant por defecto**: En desarrollo, usa un tenant predefinido

---

## Módulos y Aplicaciones

### 1. **accounts** - Gestión de Usuarios

**Propósito**: Manejo de autenticación, autorización y gestión de usuarios.

**Modelos Principales**:
- `User`: Usuario personalizado que usa email como identificador único

**Funcionalidades**:
- Registro de usuarios
- Login/Logout con JWT
- Gestión de perfiles
- Roles de usuario (ADMIN, DOC, EST, PAD)

### 2. **tenants** - Gestión Multi-Tenant

**Propósito**: Administración de colegios (tenants), planes y dominios.

**Modelos Principales**:
- `Plan`: Planes de suscripción
- `Client`: Representa un colegio/tenant
- `Domain`: Dominios asociados a tenants

**Funcionalidades**:
- Creación de nuevos colegios
- Gestión de planes de suscripción
- Configuración de dominios
- Activación/desactivación de tenants

### 3. **academics** - Gestión Académica

**Propósito**: Core del sistema académico, maneja toda la estructura educativa.

**Modelos Principales**:
- `EducationLevel`: Niveles educativos (Inicial, Primaria, Secundaria)
- `AcademicPeriod`: Períodos académicos (años, semestres, trimestres)
- `Grade`: Grados dentro de un nivel (1ro, 2do, 3ro, etc.)
- `Section`: Secciones/paralelos (A, B, C)
- `Subject`: Materias/asignaturas
- `Person`: Datos personales de individuos
- `Student`: Estudiantes vinculados a personas
- `Enrollment`: Matrículas de estudiantes

### 4. **core** - Utilidades Comunes

**Propósito**: Funcionalidades transversales y utilidades.

**Funcionalidades**:
- Health checks del sistema
- Utilidades comunes
- Validadores personalizados

### 5. **comms** - Comunicaciones (Futuro)

**Propósito**: Sistema de mensajería y comunicaciones.

**Estado**: Módulo preparado para desarrollo futuro.

### 6. **payments** - Pagos (Futuro)

**Propósito**: Gestión de pagos y facturación.

**Estado**: Módulo preparado para desarrollo futuro.

---

## Modelos de Datos

### Esquema PUBLIC (Compartido)

#### Usuario (`accounts.User`)
```python
class User(AbstractUser):
    username = None              # Deshabilitado
    name = models.CharField(max_length=150, default="user")
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=8, choices=ROLE_CHOICES, default="ADMIN")
    
    USERNAME_FIELD = "email"     # Login por email
    objects = UserManager()      # Manager personalizado
```

#### Plan (`tenants.Plan`)
```python
class Plan(models.Model):
    name = models.CharField(max_length=50)
    period = models.CharField(max_length=1, choices=[("M", "Mensual"), ("Y", "Anual")])
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=8, default="BOB")
    max_users = models.IntegerField(default=50)
    max_students = models.IntegerField(default=1000)
    features = models.JSONField(default=dict)
```

#### Cliente/Tenant (`tenants.Client`)
```python
class Client(TenantMixin):
    schema_name = models.CharField(max_length=63, unique=True)
    legal_name = models.CharField(max_length=150)
    code = models.CharField(max_length=32, unique=True)
    official_email = models.EmailField()
    plan = models.ForeignKey(Plan, null=True, on_delete=models.SET_NULL)
    is_active = models.BooleanField(default=True)
    auto_create_schema = True    # Crea esquema automáticamente
```

### Esquema de TENANT (Por Colegio)

#### Nivel Educativo (`academics.EducationLevel`)
```python
class EducationLevel(models.Model):
    name = models.CharField(max_length=80, unique=True)
    short_name = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
```

#### Período Académico (`academics.AcademicPeriod`)
```python
class AcademicPeriod(models.Model):
    name = models.CharField(max_length=80, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)
```

#### Grado (`academics.Grade`)
```python
class Grade(models.Model):
    level = models.ForeignKey(EducationLevel, on_delete=models.PROTECT)
    name = models.CharField(max_length=80)
    order = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = [("level", "name")]
```

#### Sección (`academics.Section`)
```python
class Section(models.Model):
    grade = models.ForeignKey(Grade, on_delete=models.PROTECT)
    name = models.CharField(max_length=20)
    capacity = models.PositiveIntegerField(default=30)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = [("grade", "name")]
```

#### Persona (`academics.Person`)
```python
class Person(models.Model):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    doc_type = models.CharField(max_length=10, choices=DOC_TYPE_CHOICES)
    doc_number = models.CharField(max_length=30, unique=True)
    birth_date = models.DateField(null=True, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
```

#### Estudiante (`academics.Student`)
```python
class Student(models.Model):
    person = models.OneToOneField(Person, on_delete=models.CASCADE)
    code = models.CharField(max_length=20, unique=True)
    enrollment_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
```

#### Matrícula (`academics.Enrollment`)
```python
class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.PROTECT)
    period = models.ForeignKey(AcademicPeriod, on_delete=models.PROTECT)
    grade = models.ForeignKey(Grade, on_delete=models.PROTECT)
    section = models.ForeignKey(Section, on_delete=models.PROTECT)
    enrollment_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="ACTIVE")
    
    class Meta:
        unique_together = [("student", "period")]
```

---

## APIs y Endpoints

### Endpoints Públicos (Esquema PUBLIC)

#### Autenticación (`/api/auth/`)
```
POST /api/auth/token/          # Obtener token JWT
POST /api/auth/token/refresh/  # Refrescar token
POST /api/auth/signup/         # Registro de usuario
POST /api/auth/login/          # Login personalizado
GET  /api/auth/user/           # Datos del usuario actual
POST /api/auth/logout/         # Cerrar sesión
```

#### Gestión de Tenants (`/api/`)
```
GET  /api/plans               # Listar planes disponibles
POST /api/plans               # Crear nuevo plan
GET  /api/plans/{id}          # Detalle de plan
PUT  /api/plans/{id}          # Actualizar plan
DELETE /api/plans/{id}        # Eliminar plan

POST /api/tenants             # Crear nuevo tenant/colegio
GET  /api/tenants/{id}        # Detalle de tenant

POST /api/domains             # Crear dominio para tenant
GET  /api/domains/list        # Listar dominios
```

#### Health Checks (`/api/`)
```
GET /api/health               # Health check público
GET /api/tenant/health        # Health check por tenant
```

### Endpoints por Tenant (Esquema del Colegio)

#### Gestión Académica (`/api/`)

**Niveles Educativos**
```
GET  /api/levels              # Listar niveles
POST /api/levels              # Crear nivel
GET  /api/levels/{id}         # Detalle de nivel
PUT  /api/levels/{id}         # Actualizar nivel
DELETE /api/levels/{id}       # Eliminar nivel
```

**Períodos Académicos**
```
GET  /api/periods             # Listar períodos
POST /api/periods             # Crear período
GET  /api/periods/{id}        # Detalle de período
PUT  /api/periods/{id}        # Actualizar período
DELETE /api/periods/{id}      # Eliminar período
```

**Grados**
```
GET  /api/grades              # Listar grados
POST /api/grades              # Crear grado
GET  /api/grades/{id}         # Detalle de grado
PUT  /api/grades/{id}         # Actualizar grado
DELETE /api/grades/{id}       # Eliminar grado

# Filtros disponibles:
# ?level={id}                 # Filtrar por nivel educativo
```

**Secciones**
```
GET  /api/sections            # Listar secciones
POST /api/sections            # Crear sección
GET  /api/sections/{id}       # Detalle de sección
PUT  /api/sections/{id}       # Actualizar sección
DELETE /api/sections/{id}     # Eliminar sección

# Filtros disponibles:
# ?grade={id}                 # Filtrar por grado
# ?level={id}                 # Filtrar por nivel educativo
```

**Materias**
```
GET  /api/subjects            # Listar materias
POST /api/subjects            # Crear materia
GET  /api/subjects/{id}       # Detalle de materia
PUT  /api/subjects/{id}       # Actualizar materia
DELETE /api/subjects/{id}     # Eliminar materia

# Filtros disponibles:
# ?level={id}                 # Filtrar por nivel
# ?q={texto}                  # Búsqueda por nombre
```

**Personas**
```
GET  /api/persons             # Listar personas
POST /api/persons             # Crear persona
GET  /api/persons/{id}        # Detalle de persona
PUT  /api/persons/{id}        # Actualizar persona
DELETE /api/persons/{id}      # Eliminar persona

# Filtros disponibles:
# ?q={texto}                  # Búsqueda en nombre/apellido/doc/email
```

**Estudiantes**
```
GET  /api/students            # Listar estudiantes
POST /api/students            # Crear estudiante
GET  /api/students/{id}       # Detalle de estudiante
PUT  /api/students/{id}       # Actualizar estudiante
DELETE /api/students/{id}     # Eliminar estudiante

# Filtros disponibles:
# ?q={texto}                  # Búsqueda por código o nombre
```

**Matrículas**
```
GET  /api/enrollments         # Listar matrículas
POST /api/enrollments         # Crear matrícula
GET  /api/enrollments/{id}    # Detalle de matrícula
PUT  /api/enrollments/{id}    # Actualizar matrícula
DELETE /api/enrollments/{id}  # Eliminar matrícula

# Filtros disponibles:
# ?student={id}               # Filtrar por estudiante
# ?period={id}                # Filtrar por período
# ?grade={id}                 # Filtrar por grado
# ?section={id}               # Filtrar por sección
# ?status={texto}             # Filtrar por estado
# ?q={texto}                  # Búsqueda general
```

---

## Sistema de Autenticación

### JWT (JSON Web Tokens)

El sistema utiliza **djangorestframework-simplejwt** para autenticación:

#### Configuración
```python
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}
```

#### Flujo de Autenticación
1. **Login**: `POST /api/auth/token/` con email/password
2. **Respuesta**: Access token (1 hora) + Refresh token (7 días)
3. **Uso**: Header `Authorization: Bearer {access_token}`
4. **Refresh**: `POST /api/auth/token/refresh/` con refresh token

#### Vistas Personalizadas
- `SignUpView`: Registro con token personalizado
- `LoginView`: Login con validación personalizada
- `UserView`: Obtener datos del usuario autenticado
- `LogoutView`: Cerrar sesión y limpiar cookies

---

## Permisos y Seguridad

### Sistema de Permisos

#### Permission Classes Personalizadas

**IsStaffUser** (`academics/views.py`):
```python
class IsStaffUser(permissions.BasePermission):
    """Solo staff puede escribir; lectura cualquiera autenticado."""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # GET = solo autenticado
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # POST/PUT/DELETE = solo staff
        return request.user.is_staff
```

#### Aplicación de Permisos por Vista
```python
class EducationLevelListCreateView(generics.ListCreateAPIView):
    queryset = EducationLevel.objects.all()
    serializer_class = EducationLevelSerializer
    permission_classes = [IsStaffUser]  # Personal staff para modificar
```

### Roles de Usuario
```python
ROLE_CHOICES = [
    ("ADMIN", "Admin"),      # Administrador del colegio
    ("DOC", "Docente"),      # Profesor
    ("EST", "Estudiante"),   # Estudiante
    ("PAD", "Padre"),        # Padre de familia
]
```

### Validaciones de Seguridad

#### Validación en Serializers
```python
def validate_capacity(self, value):
    if value < 1:
        raise serializers.ValidationError("capacity debe ser >= 1")
    return value

def validate_name(self, value):
    if len(value.strip()) < 2:
        raise serializers.ValidationError("El nombre debe tener al menos 2 caracteres.")
    return value.strip()
```

#### Validación en Modelos
```python
def clean(self):
    # Validación: fecha fin >= inicio
    if self.end_date < self.start_date:
        raise ValidationError("end_date no puede ser menor que start_date")
```

---

## Deployment y Docker

### Desarrollo (`Dockerfile`)
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

### Producción (`Dockerfile.prod`)
```dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]
```

### Scripts de Entrada

#### Desarrollo (`entrypoint.sh`)
```bash
#!/bin/bash
python manage.py migrate_schemas --shared
python manage.py migrate_schemas
python manage.py runserver 0.0.0.0:8000
```

#### Producción (`entrypoint.prod.sh`)
```bash
#!/bin/bash
python manage.py migrate_schemas --shared
python manage.py migrate_schemas
python manage.py collectstatic --noinput
gunicorn --bind 0.0.0.0:8000 config.wsgi:application
```

### Docker Compose

#### Desarrollo (`docker-compose.yml`)
```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: colegio_saas
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      - DEBUG=True
      - DB_HOST=db
    volumes:
      - ./backend:/app

volumes:
  postgres_data:
```

### Comandos de Gestión

#### Migraciones Multi-Tenant
```bash
# Migrar esquema público
python manage.py migrate_schemas --shared

# Migrar todos los tenants
python manage.py migrate_schemas

# Migrar tenant específico
python manage.py migrate_schemas --tenant=colegio1
```

#### Crear Superusuario
```bash
python manage.py createsuperuser
```

#### Crear Datos Iniciales
```bash
python manage.py shell
exec(open('seed/create_planes.py').read())
```

---

## Documentación API

### OpenAPI/Swagger

La documentación de la API se genera automáticamente usando **drf-spectacular**:

- **Schema**: `GET /api/schema/` (JSON)
- **Swagger UI**: `GET /api/docs/` (Interfaz web interactiva)

### Configuración
```python
SPECTACULAR_SETTINGS = {
    "TITLE": "SGAC SaaS API",
    "VERSION": "0.1",
    "DESCRIPTION": "Sistema de Gestión Académica SaaS Multi-Tenant",
}
```

### Características de la Documentación
- **Esquemas automáticos**: Generados desde los serializers
- **Ejemplos de peticiones**: Con datos de ejemplo
- **Filtros documentados**: Parámetros de consulta disponibles
- **Autenticación**: Documentación del sistema JWT
- **Códigos de respuesta**: Errores y respuestas exitosas

---

## Consideraciones Técnicas

### Performance
- **Select Related**: Uso de `select_related()` para optimizar consultas
- **Índices de Base de Datos**: Índices en campos de búsqueda frecuente
- **Paginación**: Implementada en vistas de listado
- **Caché**: Preparado para implementar caché de consultas

### Escalabilidad
- **Arquitectura Multi-Tenant**: Escalabilidad horizontal por tenant
- **Separación de Datos**: Cada colegio en esquema independiente
- **APIs RESTful**: Diseño stateless para load balancing
- **Docker**: Contenedorización para deployment distribuido

### Mantenibilidad
- **Código Documentado**: Docstrings en clases y métodos importantes
- **Validaciones Centralizadas**: En serializers y modelos
- **Separación de Responsabilidades**: Cada app con propósito específico
- **Configuración por Entorno**: Variables de entorno para diferentes despliegues

---

## Próximas Funcionalidades

### Módulos Planificados
1. **Communications (comms)**: Sistema de mensajería
2. **Payments**: Gestión de pagos y facturación
3. **Reports**: Reportes y analytics
4. **Attendance**: Control de asistencia
5. **Grades**: Sistema de calificaciones
6. **Schedule**: Horarios y calendario académico

### Mejoras Técnicas
1. **Caché Redis**: Para mejorar performance
2. **Celery**: Tareas asíncronas
3. **Websockets**: Notificaciones en tiempo real
4. **Tests Unitarios**: Cobertura completa de tests
5. **CI/CD**: Pipeline de integración continua
6. **Monitoring**: Logs y métricas de sistema

---

*Esta documentación está actualizada al 4 de octubre de 2025 y refleja el estado actual del backend del Sistema de Gestión Académica SaaS.*
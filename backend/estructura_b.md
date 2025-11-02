````markdown
# Estructura del backend (Colegio-SAAS) — Actualizado

Este documento describe la estructura del backend y detalla las nuevas funcionalidades implementadas o planeadas: sistema de asistencia, códigos QR para estudiantes, escaneo (pistola lectora y cámara), logs de escaneo y reportes.

Resumen del árbol principal (carpeta `backend/`):

backend/
├── manage.py                       # Entrypoint Django
├── config/                         # Proyecto Django (settings, urls, asgi/wsgi)
│   ├── __init__.py
│   ├── settings.py                 # Configuración del proyecto (DB, TENANT_APPS, JWT, MEDIA)
│   ├── urls.py                     # Router global y mount de apps (ej. academics.urls)
│   ├── public_urls.py              # URLs para el esquema público (si aplica)
│   └── wsgi.py / asgi.py
├── tenants/                        # Modelos y middleware del sistema multi-tenant
│   ├── models.py                   # Tenant, Domain, Plan (django-tenants)
│   └── middleware_fixed.py         # Middleware para resolución de tenant
├── accounts/                       # Usuarios, autenticación y permisos
│   ├── models.py                   # User personalizado, roles (staff, docente, padre)
│   ├── serializers.py
│   ├── views.py                    # Login, registro, gestión de usuarios
│   └── urls.py
├── academics/                      # Lógica del dominio académico (AQUÍ VA ASISTENCIA)
│   ├── models.py                   # Grade, Section, Subject, Student, Enrollment, Attendance* (recomendado)
│   ├── serializers.py              # Serializers para API REST
│   ├── views.py                    # ViewSets / APIViews (attendance endpoints aquí)
│   ├── urls.py                     # Rutas del app (ej. /api/attendance/)
│   └── admin.py                    # Registro en Django Admin
├── comms/                          # Comunicaciones y notificaciones (opcional)
├── requirements.txt                # Dependencias Python
├── Dockerfile / docker-compose.yml # Contenedores/entorno
└── media/                          # Archivos subidos (QR images, PDFs)

Resumen de nuevas funcionalidades

- Sistema de asistencia por sesión (por materia/fecha/periodo) con estados: PRESENTE, RETRASO, FALTA, FALTA_JUSTIFICADA.
- Registro por estudiante (`AttendanceRecord`) ligado a `AttendanceSession`.
- Generación de códigos QR únicos por estudiante (`StudentQRCode`) con opción de expiración y regeneración.
- Endpoint de escaneo (`QRAttendanceScanView`) pensado para pistola lectora (POST con payload JSON) y también utilizable desde cámara si se implementa frontend.
- Logs de escaneo (`AttendanceScanLog`) que guardan resultado, IP, user-agent, timestamp y usuario que escaneó.
- Endpoints para reportes y estadísticas (por periodo/grado/asignatura/estudiante) y exportación a PDF/CSV.

Modelos y campos recomendados (resumen)

- AttendanceSession
  - grade (FK), section (FK), subject (FK), period (FK)
  - date, start_time, end_time, notes
  - status (OPEN/CLOSED), created_by, created_at

- AttendanceRecord
  - session (FK), student (FK)
  - status (Enum), arrival_time, justification, notes
  - recorded_by, recorded_at

- StudentQRCode
  - student (FK), code (str, único), qr_image (ImageField opcional)
  - code_type (PERMANENT|TEMPORARY), expires_at, active

- AttendanceScanLog
  - student_qr (FK), session (FK, opcional), scanned_by (FK usuario), ip, user_agent
  - result (SUCCESS|NOT_FOUND|EXPIRED|INVALID), message, timestamp

APIs más relevantes (resumen)

- Sessions
  - GET  /api/attendance-sessions/                -> listar
  - POST /api/attendance-sessions/                -> crear
  - POST /api/attendance-sessions/{id}/close/     -> cerrar sesión
  - POST /api/attendance-sessions/{id}/bulk-attendance/ -> registrar masivo

- Records
  - GET  /api/attendance-records/                 -> listar
  - POST /api/attendance-records/                 -> crear individual
  - GET  /api/attendance-records/by-student/?student_id=1&date_from=... -> filtros

- QR Codes
  - POST /api/student-qr-codes/                   -> generar
  - POST /api/student-qr-codes/bulk-generate/     -> generar masivo
  - POST /api/student-qr-codes/{id}/regenerate/   -> regenerar

- Scan
  - POST /api/attendance/qr-scan/                 -> payload: {"qr_code": "...", "session_id": 1}

- Logs y reportes
  - GET /api/attendance/scan-logs/                 -> listar logs
  - GET /api/attendance/stats/?period_id=...      -> estadísticas
  - POST /api/attendance/report/                   -> generar reporte (PDF/CSV)

Dependencias y herramientas (recomendadas)

- Python: qrcode[pil], Pillow, reportlab (si exportas PDFs).
- Repositorio: mantener `requirements.txt` actualizado.

Migraciones y multi-tenant

- Pasos para migraciones (si usas django-tenants):
  1. Agregar modelos en `academics/models.py`.
  2. python manage.py makemigrations academics
  3. python manage.py migrate_schemas --shared
  4. python manage.py migrate_schemas

Permisos y seguridad

- Permisos sugeridos:
  - `IsStaffUser`: CRUD completo en sesiones y QR.
  - `IsAuthenticated`: lectura de reportes restringida.
  - Acceso a logs: solo staff/administración.

Buenas prácticas y validaciones

- Validar que el estudiante esté matriculado en la `section` antes de aceptar un `AttendanceRecord`.
- Requerir `justification` para ausencias justificadas.
- Registrar `recorded_by` y controlar duplicados (no crear 2 registros idénticos para el mismo estudiante y sesión).
- Usar `select_related` para evitar N+1 en consultas de listados y reportes.

Pruebas y verificación (pistola lectora)

- Formato del request desde pistola:
  - POST /api/attendance/qr-scan/
  - Headers: Authorization: Bearer <token>
  - Body JSON: {"qr_code": "COL001_EST123_ABC789", "session_id": 1}

- Comando de ejemplo (curl):
  curl -X POST https://tu-backend/api/attendance/qr-scan/ \
    -H "Authorization: Bearer <jwt>" \
    -H "Content-Type: application/json" \
    -d '{"qr_code": "COL001_EST123_ABC789", "session_id": 1}'

Checklist de integración

1. Modelos en `academics/models.py` añadidos y migraciones creadas.
2. Serializers en `academics/serializers.py` con validaciones (inscripción, horarios).
3. Views en `academics/views.py` usando ViewSets y acciones custom (`bulk-attendance`, `close`).
4. URLs en `academics/urls.py` y registre en `config/urls.py`.
5. Admin: registrar modelos y acciones (regenerar QR, exportar reporte).
6. Tests básicos: creación de sesión, registro individual y escaneo por QR.

Próximos pasos sugeridos

1. Revisar `backend/academics/models.py` y aplicar los cambios (si aceptas, genero el código listo).
2. Generar snippets de `serializers.py`, `views.py`, `urls.py` y `admin.py` para pegar y revisar.
3. Crear pruebas mínimas y ejecutar `python manage.py test` para validar.

---

Si quieres, ahora puedo generar los fragmentos exactos (plantillas) para `academics/models.py`, `academics/serializers.py`, `academics/views.py`, `academics/urls.py` y `academics/admin.py` listos para pegar; dime si prefieres que los coloque directamente en esos archivos o sólo como snippets para revisar primero.
````
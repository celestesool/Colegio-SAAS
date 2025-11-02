# backend/academics/models.py
from django.db import models
from django.core.exceptions import ValidationError
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, datetime, timedelta
from django.utils.crypto import get_random_string
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile


class EducationLevel(models.Model):
    """
    Catálogo por tenant: Nivel educativo (Inicial, Primaria, Secundaria, etc.)
    Vive en el esquema del colegio (TENANT_APPS).
    """

    name = models.CharField(max_length=80, unique=True)  # único por tenant
    short_name = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)

    # housekeeping
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class AcademicPeriod(models.Model):
    """
    Período académico (año lectivo, semestre, trimestre, etc.)
    Vive en el esquema del colegio (TENANT_APPS).
    """

    name = models.CharField(max_length=80, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-start_date", "name"]

    def clean(self):
        # Validación simple: fecha fin >= inicio
        if self.end_date < self.start_date:
            raise ValidationError("end_date no puede ser menor que start_date")

    def __str__(self):
        return self.name


class Grade(models.Model):
    """Grado/Curso dentro de un nivel educativo (1ro, 2do, etc.)."""

    level = models.ForeignKey(
        "academics.EducationLevel", on_delete=models.PROTECT, related_name="grades"
    )
    name = models.CharField(max_length=80)  # "Primero", "Segundo", etc.
    order = models.PositiveIntegerField(default=1)  # para ordenar
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["level__name", "order", "name"]
        unique_together = [("level", "name")]
        indexes = [models.Index(fields=["level", "order"])]

    def __str__(self):
        return f"{self.level.short_name or self.level.name} - {self.name}"


class Section(models.Model):
    """Paralelo/sección de un grado (A, B, C...)."""

    grade = models.ForeignKey(
        "academics.Grade", on_delete=models.PROTECT, related_name="sections"
    )
    name = models.CharField(max_length=20)  # "A", "B", "C"...
    capacity = models.PositiveIntegerField(default=30)  # cupo recomendado
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["grade__level__name", "grade__order", "grade__name", "name"]
        unique_together = [
            ("grade", "name")
        ]  # no repetir "A" dos veces en el mismo grado
        indexes = [
            models.Index(fields=["grade", "name"]),
        ]

    def __str__(self):
        return f"{self.grade} - {self.name}"


class Subject(models.Model):
    """
    Materia/Asignatura. Para Sprint 1 la ligamos al nivel educativo.
    Vive en el esquema del colegio (TENANT_APPS).
    """

    level = models.ForeignKey(
        "academics.EducationLevel", on_delete=models.PROTECT, related_name="subjects"
    )
    name = models.CharField(max_length=120)
    short_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)

    # housekeeping
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["level__name", "name"]
        unique_together = [("level", "name")]  # evita duplicados por nivel
        indexes = [
            models.Index(fields=["level", "name"]),
        ]

    def __str__(self):
        return f"{self.level.short_name or self.level.name} - {self.name}"


class Person(models.Model):
    """
    Datos base de una persona (comunes a estudiante, docente, apoderado).
    Vive en el esquema del colegio (TENANT_APPS).
    """

    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=120)
    doc_type = models.CharField(max_length=20, blank=True)  # CI, PAS, etc.
    doc_number = models.CharField(max_length=40, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.CharField(max_length=255, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["last_name", "first_name"]
        indexes = [
            models.Index(fields=["last_name", "first_name"]),
            models.Index(fields=["doc_number"]),
            models.Index(fields=["email"]),
        ]

    def __str__(self):
        return f"{self.last_name}, {self.first_name}".strip()


class Student(models.Model):
    """
    Rol estudiante: referencia a Person + campos propios.
    Vive en el esquema del colegio (TENANT_APPS).
    """

    person = models.OneToOneField(
        "academics.Person", on_delete=models.PROTECT, related_name="student"
    )
    code = models.CharField(max_length=30, unique=True)  # código interno del alumno
    admission_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["code"]
        indexes = [
            models.Index(fields=["code"]),
        ]

    def __str__(self):
        return f"{self.code} - {self.person}"


class Enrollment(models.Model):
    """
    Matrícula del estudiante en un período, grado y sección.
    Reglas base:
    - Un estudiante no puede tener dos matrículas en el mismo período.
    """

    STATUS_CHOICES = [
        ("ACTIVE", "Activa"),
        ("WITHDRAWN", "Retiro"),
        ("TRANSFERRED", "Transferido"),
        ("FINISHED", "Finalizada"),
    ]

    student = models.ForeignKey(
        "academics.Student", on_delete=models.PROTECT, related_name="enrollments"
    )
    period = models.ForeignKey(
        "academics.AcademicPeriod", on_delete=models.PROTECT, related_name="enrollments"
    )
    grade = models.ForeignKey(
        "academics.Grade", on_delete=models.PROTECT, related_name="enrollments"
    )
    section = models.ForeignKey(
        "academics.Section", on_delete=models.PROTECT, related_name="enrollments"
    )

    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="ACTIVE")
    enroll_date = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = [("student", "period")]  # 1 matrícula por período
        indexes = [
            models.Index(fields=["student", "period"]),
            models.Index(fields=["grade", "section"]),
        ]

    def __str__(self):
        return f"{self.student.code} @ {self.period.name} - {self.grade.name}/{self.section.name}"

# DOCENTES Y ASIGNACIONES
# ------------------------------------------------------

class Teacher(models.Model):
    """
    Docente. Debe tener cuenta User obligatoriamente.
    Extiende Person con datos específicos del docente.
    """
    person = models.OneToOneField(
        "academics.Person",
        on_delete=models.PROTECT,
        related_name="teacher"
    )
    user = models.OneToOneField(
        "accounts.User",
        on_delete=models.PROTECT,
        related_name="teacher",
        help_text="Usuario para acceso al sistema (obligatorio)"
    )
    employee_code = models.CharField(
        max_length=30,
        unique=True,
        help_text="Código de empleado/docente"
    )
    specialization = models.CharField(max_length=150, blank=True)
    hire_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["employee_code"]
        indexes = [
            models.Index(fields=["employee_code"]),
            models.Index(fields=["user"]),
        ]

    def clean(self):
        if self.user and self.user.role != "DOC":
            raise ValidationError("El usuario debe tener rol 'DOC' (Docente)")

    def __str__(self):
        return f"{self.employee_code} - {self.person}"


class TeacherAssignment(models.Model):
    """
    Asignación docente a materia-grado-sección en período académico.
    Permite múltiples asignaciones con validación de choques de horario.
    """
    teacher = models.ForeignKey(
        "academics.Teacher",
        on_delete=models.PROTECT,
        related_name="assignments"
    )
    subject = models.ForeignKey(
        "academics.Subject",
        on_delete=models.PROTECT,
        related_name="assignments"
    )
    grade = models.ForeignKey(
        "academics.Grade",
        on_delete=models.PROTECT,
        related_name="teacher_assignments"
    )
    section = models.ForeignKey(
        "academics.Section",
        on_delete=models.PROTECT,
        related_name="teacher_assignments"
    )
    period = models.ForeignKey(
        "academics.AcademicPeriod",
        on_delete=models.PROTECT,
        related_name="teacher_assignments"
    )
    
    schedule_day = models.CharField(
        max_length=10,
        blank=True,
        choices=[
            ("LUN", "Lunes"),
            ("MAR", "Martes"),
            ("MIE", "Miércoles"),
            ("JUE", "Jueves"),
            ("VIE", "Viernes"),
            ("SAB", "Sábado"),
        ]
    )
    schedule_start = models.TimeField(null=True, blank=True)
    schedule_end = models.TimeField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["period", "grade", "section", "subject"]
        unique_together = [
            ("teacher", "subject", "grade", "section", "period")
        ]
        indexes = [
            models.Index(fields=["teacher", "period"]),
            models.Index(fields=["grade", "section", "period"]),
            models.Index(fields=["subject", "period"]),
        ]

    def clean(self):
        if self.subject and self.grade:
            if self.subject.level_id != self.grade.level_id:
                raise ValidationError(
                    "La materia debe pertenecer al mismo nivel educativo que el grado"
                )
        
        if self.section and self.grade:
            if self.section.grade_id != self.grade.id:
                raise ValidationError(
                    "La sección debe pertenecer al grado seleccionado"
                )
        
        if self.schedule_start and self.schedule_end:
            if self.schedule_end <= self.schedule_start:
                raise ValidationError(
                    "La hora de fin debe ser posterior a la de inicio"
                )
            
            if self.schedule_day:
                conflicting = TeacherAssignment.objects.filter(
                    teacher=self.teacher,
                    period=self.period,
                    schedule_day=self.schedule_day,
                    is_active=True
                ).exclude(pk=self.pk if self.pk else None)
                
                for assignment in conflicting:
                    if assignment.schedule_start and assignment.schedule_end:
                        if (
                            (self.schedule_start < assignment.schedule_end and 
                             self.schedule_end > assignment.schedule_start)
                        ):
                            raise ValidationError(
                                f"Choque de horario con {assignment.subject.name} "
                                f"en {assignment.grade.name}{assignment.section.name} "
                                f"({assignment.schedule_start}-{assignment.schedule_end})"
                            )

    def __str__(self):
        return (
            f"{self.teacher.employee_code} → {self.subject.short_name or self.subject.name} "
            f"({self.grade.name}{self.section.name}) - {self.period.name}"
        )

# FIN DOCENTES


# SISTEMA DE CALIFICACIONES
# ------------------------------------------------------

class GradingDimension(models.Model):
    """
    Dimensiones de evaluación del sistema boliviano.
    Ser, Saber, Hacer, Decidir - con ponderación configurable.
    """
    DIMENSION_CHOICES = [
        ("SER", "Ser"),
        ("SABER", "Saber"),
        ("HACER", "Hacer"),
        ("DECIDIR", "Decidir"),
    ]
    
    name = models.CharField(max_length=20, choices=DIMENSION_CHOICES, unique=True)
    description = models.TextField(blank=True)
    default_weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=25.00,
        help_text="Porcentaje de peso (0-100)"
    )
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def clean(self):
        if self.default_weight < 0 or self.default_weight > 100:
            raise ValidationError("El peso debe estar entre 0 y 100")

    def __str__(self):
        return f"{self.get_name_display()} ({self.default_weight}%)"


class GradingPeriod(models.Model):
    """
    Períodos de evaluación: Trimestre 1, 2, 3 dentro de un período académico.
    """
    PERIOD_CHOICES = [
        ("T1", "Trimestre 1"),
        ("T2", "Trimestre 2"),
        ("T3", "Trimestre 3"),
    ]
    
    academic_period = models.ForeignKey(
        "academics.AcademicPeriod",
        on_delete=models.CASCADE,
        related_name="grading_periods"
    )
    name = models.CharField(max_length=10, choices=PERIOD_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["academic_period", "name"]
        unique_together = [("academic_period", "name")]
        indexes = [
            models.Index(fields=["academic_period", "name"]),
        ]

    def clean(self):
        if self.end_date <= self.start_date:
            raise ValidationError("La fecha fin debe ser posterior a la fecha inicio")
        
        # Validar que esté dentro del período académico
        if self.academic_period:
            if self.start_date < self.academic_period.start_date:
                raise ValidationError(
                    "El trimestre no puede iniciar antes del período académico"
                )
            if self.end_date > self.academic_period.end_date:
                raise ValidationError(
                    "El trimestre no puede finalizar después del período académico"
                )

    def __str__(self):
        return f"{self.get_name_display()} - {self.academic_period.name}"


class DimensionWeight(models.Model):
    """
    Ponderación personalizada de dimensiones por materia y grado.
    Si no existe, usa default_weight de GradingDimension.
    """
    subject = models.ForeignKey(
        "academics.Subject",
        on_delete=models.CASCADE,
        related_name="dimension_weights"
    )
    grade = models.ForeignKey(
        "academics.Grade",
        on_delete=models.CASCADE,
        related_name="dimension_weights"
    )
    dimension = models.ForeignKey(
        "academics.GradingDimension",
        on_delete=models.CASCADE,
        related_name="custom_weights"
    )
    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Porcentaje de peso (0-100)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("subject", "grade", "dimension")]
        indexes = [
            models.Index(fields=["subject", "grade"]),
        ]

    def clean(self):
        if self.weight < 0 or self.weight > 100:
            raise ValidationError("El peso debe estar entre 0 y 100")
        
        # Validar que la suma de pesos no exceda 100
        total = DimensionWeight.objects.filter(
            subject=self.subject,
            grade=self.grade
        ).exclude(pk=self.pk if self.pk else None).aggregate(
            total=models.Sum("weight")
        )["total"] or 0
        
        if total + self.weight > 100:
            raise ValidationError(
                f"La suma de pesos no puede exceder 100%. Actual: {total}%"
            )

    def __str__(self):
        return f"{self.dimension.name} - {self.subject.name} ({self.grade.name}): {self.weight}%"


class StudentGrade(models.Model):
    """
    Calificación individual de un estudiante en una materia.
    Por dimensión, trimestre, materia y período académico.
    """
    enrollment = models.ForeignKey(
        "academics.Enrollment",
        on_delete=models.CASCADE,
        related_name="grades"
    )
    subject = models.ForeignKey(
        "academics.Subject",
        on_delete=models.PROTECT,
        related_name="student_grades"
    )
    dimension = models.ForeignKey(
        "academics.GradingDimension",
        on_delete=models.PROTECT,
        related_name="student_grades"
    )
    grading_period = models.ForeignKey(
        "academics.GradingPeriod",
        on_delete=models.PROTECT,
        related_name="student_grades"
    )
    
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Nota de 1 a 100"
    )
    
    # Auditoría: quién registró y cuándo
    teacher_assignment = models.ForeignKey(
        "academics.TeacherAssignment",
        on_delete=models.PROTECT,
        related_name="registered_grades",
        help_text="Asignación del docente que registró la nota"
    )
    recorded_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.PROTECT,
        related_name="recorded_grades"
    )
    
    notes = models.TextField(blank=True)
    
    recorded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-recorded_at"]
        unique_together = [
            ("enrollment", "subject", "dimension", "grading_period")
        ]
        indexes = [
            models.Index(fields=["enrollment", "subject"]),
            models.Index(fields=["grading_period", "subject"]),
            models.Index(fields=["teacher_assignment"]),
        ]

    def clean(self):
        # Validar rango de nota
        if self.score < 1 or self.score > 100:
            raise ValidationError("La nota debe estar entre 1 y 100")
        
        # Validar que enrollment esté activo
        if self.enrollment and self.enrollment.status != "ACTIVE":
            raise ValidationError("No se puede calificar una matrícula inactiva")
        
        # Validar que subject pertenezca al nivel del enrollment
        if self.subject and self.enrollment:
            if self.subject.level_id != self.enrollment.grade.level_id:
                raise ValidationError(
                    "La materia debe pertenecer al nivel educativo del estudiante"
                )
        
        # Validar que grading_period pertenezca al período académico del enrollment
        if self.grading_period and self.enrollment:
            if self.grading_period.academic_period_id != self.enrollment.period_id:
                raise ValidationError(
                    "El trimestre debe pertenecer al período académico de la matrícula"
                )
        
        # Validar que teacher_assignment sea válido para esta materia/grado/sección
        if self.teacher_assignment and self.enrollment:
            valid = (
                self.teacher_assignment.subject_id == self.subject_id and
                self.teacher_assignment.grade_id == self.enrollment.grade_id and
                self.teacher_assignment.section_id == self.enrollment.section_id and
                self.teacher_assignment.period_id == self.enrollment.period_id and
                self.teacher_assignment.is_active
            )
            if not valid:
                raise ValidationError(
                    "El docente no tiene asignación válida para esta materia/grado/sección"
                )

    def __str__(self):
        return (
            f"{self.enrollment.student.code} - {self.subject.short_name or self.subject.name} "
            f"({self.dimension.name}) - {self.grading_period.name}: {self.score}"
        )

    @property
    def student(self):
        return self.enrollment.student

    @property
    def period(self):
        return self.enrollment.period


class GradeAverage(models.Model):
    """
    Promedios calculados por estudiante-materia-trimestre.
    Se actualiza automáticamente al guardar StudentGrade.
    """
    enrollment = models.ForeignKey(
        "academics.Enrollment",
        on_delete=models.CASCADE,
        related_name="grade_averages"
    )
    subject = models.ForeignKey(
        "academics.Subject",
        on_delete=models.PROTECT,
        related_name="grade_averages"
    )
    grading_period = models.ForeignKey(
        "academics.GradingPeriod",
        on_delete=models.PROTECT,
        related_name="grade_averages"
    )
    
    average = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Promedio ponderado de las 4 dimensiones"
    )
    
    calculated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("enrollment", "subject", "grading_period")]
        indexes = [
            models.Index(fields=["enrollment", "grading_period"]),
        ]

    def __str__(self):
        return (
            f"{self.enrollment.student.code} - {self.subject.short_name or self.subject.name} "
            f"({self.grading_period.name}): {self.average}"
        )

# FIN CALIFICACIONES

#ASISNECIAS
#------------------------------------------------------

class AttendanceSession(models.Model):
    """Sesión de asistencia (una clase específica en una fecha y hora)."""
    grade = models.ForeignKey("academics.Grade", on_delete=models.PROTECT)
    section = models.ForeignKey("academics.Section", on_delete=models.PROTECT)
    subject = models.ForeignKey("academics.Subject", on_delete=models.PROTECT)
    period = models.ForeignKey("academics.AcademicPeriod", on_delete=models.PROTECT)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(null=True, blank=True)
    is_closed = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey("accounts.User", on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-start_time"]
        unique_together = [("grade", "section", "subject", "date", "start_time")]

    def clean(self):
        if self.end_time and self.end_time <= self.start_time:
            raise ValidationError("La hora de fin debe ser posterior al inicio")
        if self.date > date.today():
            raise ValidationError("No se puede crear una sesión futura")

    def __str__(self):
        return f"{self.subject.name} - {self.grade.name}{self.section.name} ({self.date})"

    @property
    def total_students(self):
        from academics.models import Enrollment
        return Enrollment.objects.filter(
            grade=self.grade,
            section=self.section,
            period=self.period,
            status="ACTIVE"
        ).count()


class AttendanceRecord(models.Model):
    """Registro de asistencia de un estudiante en una sesión."""
    STATUS_CHOICES = [
        ("PRESENTE", "Presente"),
        ("AUSENTE", "Ausente"),
        ("RETRASO", "Retraso"),
        ("FALTA_JUSTIFICADA", "Falta justificada"),
    ]

    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE)
    student = models.ForeignKey("academics.Student", on_delete=models.PROTECT)
    status = models.CharField(max_length=18, choices=STATUS_CHOICES, default="PRESENTE")
    arrival_time = models.TimeField(null=True, blank=True)
    justification = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    recorded_by = models.ForeignKey("accounts.User", on_delete=models.PROTECT)
    recorded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-recorded_at"]
        unique_together = [("session", "student")]

    def clean(self):
        from academics.models import Enrollment
        enrolled = Enrollment.objects.filter(
            student=self.student,
            grade=self.session.grade,
            section=self.session.section,
            period=self.session.period,
            status="ACTIVE"
        ).exists()
        if not enrolled:
            raise ValidationError("El estudiante no está matriculado en esta sección")

        if self.status == "RETRASO" and not self.arrival_time:
            raise ValidationError("Debe especificar hora de llegada para retrasos")
        if self.status == "FALTA_JUSTIFICADA" and not self.justification:
            raise ValidationError("Debe justificar una falta justificada")

    def save(self, *args, **kwargs):
        if self.status == "PRESENTE" and not self.arrival_time:
            self.arrival_time = self.session.start_time
        if self.status in ["AUSENTE", "FALTA_JUSTIFICADA"]:
            self.arrival_time = None
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.code} - {self.status} ({self.session.date})"


class StudentQRCode(models.Model):
    """Código QR o de barras asignado a un estudiante."""
    CODE_TYPES = [
        ("PERMANENT", "Permanente"),
        ("TEMPORARY", "Temporal"),
    ]

    student = models.ForeignKey("academics.Student", on_delete=models.CASCADE)
    code = models.CharField(max_length=80, unique=True)
    code_type = models.CharField(max_length=12, choices=CODE_TYPES, default="PERMANENT")
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    qr_image = models.ImageField(upload_to="qr_codes/", null=True, blank=True)
    scan_count = models.PositiveIntegerField(default=0)
    last_scanned = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey("accounts.User", on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = f"{self.student.code}-{get_random_string(6).upper()}"
        if not self.qr_image:
            self._generate_qr_image()
        super().save(*args, **kwargs)

    def _generate_qr_image(self):
        qr = qrcode.QRCode(box_size=8, border=2)
        qr.add_data({"student_id": self.student.id, "code": self.code})
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        self.qr_image.save(f"qr_{self.code}.png", ContentFile(buffer.getvalue()), save=False)

    def record_scan(self):
        self.scan_count += 1
        self.last_scanned = timezone.now()
        self.save(update_fields=["scan_count", "last_scanned"])

    def is_valid(self):
        if not self.is_active:
            return False, "Código inactivo"
        if self.expires_at and timezone.now() > self.expires_at:
            return False, "Código expirado"
        return True, "Válido"

    def __str__(self):
        return f"{self.student.code} - {self.code}"


class AttendanceScanLog(models.Model):
    """Log de escaneos QR."""
    SCAN_STATUS = [
        ("SUCCESS", "Éxito"),
        ("INVALID_CODE", "Código inválido"),
        ("DUPLICATE", "Duplicado"),
        ("NOT_ENROLLED", "No matriculado"),
        ("ERROR", "Error"),
    ]

    scanned_code = models.CharField(max_length=100)
    scan_status = models.CharField(max_length=20, choices=SCAN_STATUS)
    student_qr = models.ForeignKey(StudentQRCode, null=True, blank=True, on_delete=models.SET_NULL)
    attendance_record = models.ForeignKey(AttendanceRecord, null=True, blank=True, on_delete=models.SET_NULL)
    session = models.ForeignKey(AttendanceSession, null=True, blank=True, on_delete=models.SET_NULL)
    scanned_by = models.ForeignKey("accounts.User", on_delete=models.PROTECT)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    message = models.TextField(blank=True)
    scanned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-scanned_at"]

    def __str__(self):
        return f"{self.scanned_code} - {self.scan_status}"
    
#FIN ASISTENCIA _____________________________________

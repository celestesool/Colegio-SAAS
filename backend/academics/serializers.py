# backend/academics/serializers.py
from rest_framework import serializers
from .models import (
    EducationLevel,
    AcademicPeriod,
    Grade,
    Section,
    Subject,
    Person,
    Student,
    Enrollment,
)


class EducationLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationLevel
        fields = ["id", "name", "short_name", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


# ...


class AcademicPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicPeriod
        fields = [
            "id",
            "name",
            "start_date",
            "end_date",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        # Repite la regla de fechas en capa API (además del clean del modelo)
        if (
            attrs.get("end_date")
            and attrs.get("start_date")
            and attrs["end_date"] < attrs["start_date"]
        ):
            raise serializers.ValidationError(
                "end_date no puede ser menor que start_date"
            )
        return attrs


class GradeSerializer(serializers.ModelSerializer):
    level_name = serializers.CharField(source="level.name", read_only=True)

    class Meta:
        model = Grade
        fields = [
            "id",
            "level",
            "level_name",
            "name",
            "order",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_order(self, value):
        if value < 1:
            raise serializers.ValidationError("order debe ser >= 1")
        return value


class SectionSerializer(serializers.ModelSerializer):
    grade_name = serializers.CharField(source="grade.name", read_only=True)
    level_id = serializers.IntegerField(source="grade.level_id", read_only=True)
    level_name = serializers.CharField(source="grade.level.name", read_only=True)

    class Meta:
        model = Section
        fields = [
            "id",
            "grade",
            "grade_name",
            "level_id",
            "level_name",
            "name",
            "capacity",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_capacity(self, value):
        if value < 1:
            raise serializers.ValidationError("capacity debe ser >= 1")
        return value


class SubjectSerializer(serializers.ModelSerializer):
    level_name = serializers.CharField(source="level.name", read_only=True)

    class Meta:
        model = Subject
        fields = [
            "id",
            "level",
            "level_name",
            "name",
            "short_name",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError(
                "El nombre debe tener al menos 2 caracteres."
            )
        return value.strip()


# Actores
class PersonSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Person
        fields = [
            "id",
            "first_name",
            "last_name",
            "full_name",
            "doc_type",
            "doc_number",
            "email",
            "phone",
            "address",
            "birth_date",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

    def validate(self, attrs):
        # Ejemplo simple: si hay email, que no sea muy corto
        email = attrs.get("email")
        if email and len(email) < 6:
            raise serializers.ValidationError({"email": "Email inválido."})
        return attrs


class StudentSerializer(serializers.ModelSerializer):
    # Datos derivados para mostrar en listas
    person_name = serializers.CharField(source="person.__str__", read_only=True)

    class Meta:
        model = Student
        fields = [
            "id",
            "person",
            "person_name",
            "code",
            "admission_date",
            "notes",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_code(self, value):
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError(
                "El código debe tener al menos 3 caracteres."
            )
        return value


class EnrollmentSerializer(serializers.ModelSerializer):
    student_code = serializers.CharField(source="student.code", read_only=True)
    student_name = serializers.CharField(
        source="student.person.__str__", read_only=True
    )
    period_name = serializers.CharField(source="period.name", read_only=True)
    grade_name = serializers.CharField(source="grade.name", read_only=True)
    section_name = serializers.CharField(source="section.name", read_only=True)

    class Meta:
        model = Enrollment
        fields = [
            "id",
            "student",
            "student_code",
            "student_name",
            "period",
            "period_name",
            "grade",
            "grade_name",
            "section",
            "section_name",
            "status",
            "enroll_date",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "enroll_date",
            "created_at",
            "updated_at",
            "student_code",
            "student_name",
            "period_name",
            "grade_name",
            "section_name",
        ]

    def validate(self, attrs):
        # Asegurar coherencia grade/section
        grade = attrs.get("grade") or getattr(self.instance, "grade", None)
        section = attrs.get("section") or getattr(self.instance, "section", None)
        if grade and section and section.grade_id != grade.id:
            raise serializers.ValidationError(
                "La sección seleccionada no pertenece al grado indicado."
            )

        # Evitar duplicar matrícula por (student, period)
        student = attrs.get("student") or getattr(self.instance, "student", None)
        period = attrs.get("period") or getattr(self.instance, "period", None)
        if student and period:
            qs = Enrollment.objects.filter(student=student, period=period)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    "El estudiante ya está matriculado en ese período."
                )

        return attrs


# DOCENTES Y ASIGNACIONES
# ---------------------------------------------------------------

class TeacherSerializer(serializers.ModelSerializer):
    person_name = serializers.CharField(source="person.__str__", read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_role = serializers.CharField(source="user.role", read_only=True)
    
    class Meta:
        model = Teacher
        fields = [
            "id",
            "person",
            "person_name",
            "user",
            "user_email",
            "user_role",
            "employee_code",
            "specialization",
            "hire_date",
            "is_active",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_employee_code(self, value):
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError(
                "El código de empleado debe tener al menos 3 caracteres"
            )
        return value

    def validate_user(self, value):
        if value.role != "DOC":
            raise serializers.ValidationError(
                "El usuario debe tener rol 'DOC' (Docente)"
            )
        # Verificar que el usuario no esté ya asignado a otro docente
        if Teacher.objects.filter(user=value).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise serializers.ValidationError(
                "Este usuario ya está asignado a otro docente"
            )
        return value


class TeacherAssignmentSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source="teacher.person.__str__", read_only=True)
    teacher_code = serializers.CharField(source="teacher.employee_code", read_only=True)
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    grade_name = serializers.CharField(source="grade.name", read_only=True)
    section_name = serializers.CharField(source="section.name", read_only=True)
    period_name = serializers.CharField(source="period.name", read_only=True)
    level_name = serializers.CharField(source="grade.level.name", read_only=True)
    
    class Meta:
        model = TeacherAssignment
        fields = [
            "id",
            "teacher",
            "teacher_name",
            "teacher_code",
            "subject",
            "subject_name",
            "grade",
            "grade_name",
            "section",
            "section_name",
            "period",
            "period_name",
            "level_name",
            "schedule_day",
            "schedule_start",
            "schedule_end",
            "is_active",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        teacher = attrs.get("teacher") or getattr(self.instance, "teacher", None)
        subject = attrs.get("subject") or getattr(self.instance, "subject", None)
        grade = attrs.get("grade") or getattr(self.instance, "grade", None)
        section = attrs.get("section") or getattr(self.instance, "section", None)
        period = attrs.get("period") or getattr(self.instance, "period", None)

        # Validar que la materia pertenezca al mismo nivel que el grado
        if subject and grade:
            if subject.level_id != grade.level_id:
                raise serializers.ValidationError(
                    "La materia debe pertenecer al mismo nivel educativo que el grado"
                )

        # Validar que la sección pertenezca al grado
        if section and grade:
            if section.grade_id != grade.id:
                raise serializers.ValidationError(
                    "La sección debe pertenecer al grado seleccionado"
                )

        # Validar horarios
        schedule_start = attrs.get("schedule_start") or getattr(self.instance, "schedule_start", None)
        schedule_end = attrs.get("schedule_end") or getattr(self.instance, "schedule_end", None)
        schedule_day = attrs.get("schedule_day") or getattr(self.instance, "schedule_day", None)

        if schedule_start and schedule_end:
            if schedule_end <= schedule_start:
                raise serializers.ValidationError(
                    "La hora de fin debe ser posterior a la de inicio"
                )

            # Validar choques de horario
            if schedule_day and teacher and period:
                conflicting = TeacherAssignment.objects.filter(
                    teacher=teacher,
                    period=period,
                    schedule_day=schedule_day,
                    is_active=True
                )
                if self.instance:
                    conflicting = conflicting.exclude(pk=self.instance.pk)

                for assignment in conflicting:
                    if assignment.schedule_start and assignment.schedule_end:
                        if (
                            schedule_start < assignment.schedule_end
                            and schedule_end > assignment.schedule_start
                        ):
                            raise serializers.ValidationError(
                                f"Choque de horario con {assignment.subject.name} "
                                f"en {assignment.grade.name}{assignment.section.name} "
                                f"({assignment.schedule_start}-{assignment.schedule_end})"
                            )

        # Evitar asignación duplicada (mismo teacher, subject, grade, section, period)
        if teacher and subject and grade and section and period:
            qs = TeacherAssignment.objects.filter(
                teacher=teacher,
                subject=subject,
                grade=grade,
                section=section,
                period=period
            )
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    "Ya existe una asignación para este docente con la misma materia, grado y sección en este período"
                )

        return attrs

# FIN DOCENTES


# SISTEMA DE CALIFICACIONES
# ---------------------------------------------------------------

class GradingDimensionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GradingDimension
        fields = [
            "id",
            "name",
            "description",
            "default_weight",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_default_weight(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("El peso debe estar entre 0 y 100")
        return value


class GradingPeriodSerializer(serializers.ModelSerializer):
    academic_period_name = serializers.CharField(
        source="academic_period.name", read_only=True
    )
    
    class Meta:
        model = GradingPeriod
        fields = [
            "id",
            "academic_period",
            "academic_period_name",
            "name",
            "start_date",
            "end_date",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        start_date = attrs.get("start_date") or getattr(self.instance, "start_date", None)
        end_date = attrs.get("end_date") or getattr(self.instance, "end_date", None)
        academic_period = attrs.get("academic_period") or getattr(
            self.instance, "academic_period", None
        )

        if start_date and end_date and end_date <= start_date:
            raise serializers.ValidationError(
                "La fecha fin debe ser posterior a la fecha inicio"
            )

        if academic_period and start_date and end_date:
            if start_date < academic_period.start_date:
                raise serializers.ValidationError(
                    "El trimestre no puede iniciar antes del período académico"
                )
            if end_date > academic_period.end_date:
                raise serializers.ValidationError(
                    "El trimestre no puede finalizar después del período académico"
                )

        return attrs


class DimensionWeightSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    grade_name = serializers.CharField(source="grade.name", read_only=True)
    dimension_name = serializers.CharField(source="dimension.get_name_display", read_only=True)
    
    class Meta:
        model = DimensionWeight
        fields = [
            "id",
            "subject",
            "subject_name",
            "grade",
            "grade_name",
            "dimension",
            "dimension_name",
            "weight",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_weight(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("El peso debe estar entre 0 y 100")
        return value

    def validate(self, attrs):
        subject = attrs.get("subject") or getattr(self.instance, "subject", None)
        grade = attrs.get("grade") or getattr(self.instance, "grade", None)
        dimension = attrs.get("dimension") or getattr(self.instance, "dimension", None)
        weight = attrs.get("weight") or getattr(self.instance, "weight", None)

        if subject and grade and weight:
            total = DimensionWeight.objects.filter(
                subject=subject,
                grade=grade
            ).exclude(pk=self.instance.pk if self.instance else None).aggregate(
                total=models.Sum("weight")
            )["total"] or 0

            if total + weight > 100:
                raise serializers.ValidationError(
                    f"La suma de pesos no puede exceder 100%. Actual: {total}%"
                )

        return attrs


class StudentGradeSerializer(serializers.ModelSerializer):
    student_code = serializers.CharField(source="enrollment.student.code", read_only=True)
    student_name = serializers.CharField(
        source="enrollment.student.person.__str__", read_only=True
    )
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    dimension_name = serializers.CharField(source="dimension.get_name_display", read_only=True)
    grading_period_name = serializers.CharField(
        source="grading_period.get_name_display", read_only=True
    )
    teacher_name = serializers.CharField(
        source="teacher_assignment.teacher.person.__str__", read_only=True
    )
    
    class Meta:
        model = StudentGrade
        fields = [
            "id",
            "enrollment",
            "student_code",
            "student_name",
            "subject",
            "subject_name",
            "dimension",
            "dimension_name",
            "grading_period",
            "grading_period_name",
            "score",
            "teacher_assignment",
            "teacher_name",
            "recorded_by",
            "notes",
            "recorded_at",
            "updated_at",
        ]
        read_only_fields = ["id", "recorded_by", "recorded_at", "updated_at"]

    def validate_score(self, value):
        if value < 1 or value > 100:
            raise serializers.ValidationError("La nota debe estar entre 1 y 100")
        return value

    def validate(self, attrs):
        enrollment = attrs.get("enrollment") or getattr(self.instance, "enrollment", None)
        subject = attrs.get("subject") or getattr(self.instance, "subject", None)
        grading_period = attrs.get("grading_period") or getattr(
            self.instance, "grading_period", None
        )
        teacher_assignment = attrs.get("teacher_assignment") or getattr(
            self.instance, "teacher_assignment", None
        )

        # Validar enrollment activo
        if enrollment and enrollment.status != "ACTIVE":
            raise serializers.ValidationError("No se puede calificar una matrícula inactiva")

        # Validar que subject pertenezca al nivel del enrollment
        if subject and enrollment:
            if subject.level_id != enrollment.grade.level_id:
                raise serializers.ValidationError(
                    "La materia debe pertenecer al nivel educativo del estudiante"
                )

        # Validar que grading_period pertenezca al período académico del enrollment
        if grading_period and enrollment:
            if grading_period.academic_period_id != enrollment.period_id:
                raise serializers.ValidationError(
                    "El trimestre debe pertenecer al período académico de la matrícula"
                )

        # Validar que teacher_assignment sea válido
        if teacher_assignment and enrollment and subject:
            valid = (
                teacher_assignment.subject_id == subject.id
                and teacher_assignment.grade_id == enrollment.grade_id
                and teacher_assignment.section_id == enrollment.section_id
                and teacher_assignment.period_id == enrollment.period_id
                and teacher_assignment.is_active
            )
            if not valid:
                raise serializers.ValidationError(
                    "El docente no tiene asignación válida para esta materia/grado/sección"
                )

        return attrs


class GradeAverageSerializer(serializers.ModelSerializer):
    student_code = serializers.CharField(source="enrollment.student.code", read_only=True)
    student_name = serializers.CharField(
        source="enrollment.student.person.__str__", read_only=True
    )
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    grading_period_name = serializers.CharField(
        source="grading_period.get_name_display", read_only=True
    )
    
    class Meta:
        model = GradeAverage
        fields = [
            "id",
            "enrollment",
            "student_code",
            "student_name",
            "subject",
            "subject_name",
            "grading_period",
            "grading_period_name",
            "average",
            "calculated_at",
        ]
        read_only_fields = ["id", "average", "calculated_at"]

# FIN CALIFICACIONES

 
# ASISTENCIAS
# ---------------------------------------------------------------
from rest_framework import serializers
from academics.models import (
    AttendanceSession,
    AttendanceRecord,
    StudentQRCode,
    AttendanceScanLog,
)


class AttendanceSessionSerializer(serializers.ModelSerializer):
    total_students = serializers.ReadOnlyField()
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    grade_name = serializers.CharField(source="grade.name", read_only=True)
    section_name = serializers.CharField(source="section.name", read_only=True)
    created_by_name = serializers.CharField(source="created_by.username", read_only=True)

    class Meta:
        model = AttendanceSession
        fields = [
            "id", "grade", "section", "subject", "period",
            "date", "start_time", "end_time", "is_closed", "notes",
            "created_by", "created_by_name", "total_students",
            "created_at", "updated_at",
            "subject_name", "grade_name", "section_name",
        ]
        read_only_fields = ["created_by", "created_at", "updated_at"]


class AttendanceRecordSerializer(serializers.ModelSerializer):
    student_code = serializers.CharField(source="student.code", read_only=True)
    student_name = serializers.CharField(source="student.person.__str__", read_only=True)
    session_date = serializers.DateField(source="session.date", read_only=True)

    class Meta:
        model = AttendanceRecord
        fields = [
            "id", "session", "student", "status", "arrival_time",
            "justification", "notes", "recorded_by", "recorded_at",
            "student_code", "student_name", "session_date",
        ]
        read_only_fields = ["recorded_by", "recorded_at"]


class StudentQRCodeSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.person.__str__", read_only=True)
    qr_image_url = serializers.SerializerMethodField()

    class Meta:
        model = StudentQRCode
        fields = [
            "id", "student", "student_name", "code", "code_type",
            "is_active", "expires_at", "qr_image_url",
            "scan_count", "last_scanned", "created_at",
        ]
        read_only_fields = ["code", "scan_count", "last_scanned", "created_at"]

    def get_qr_image_url(self, obj):
        if obj.qr_image and hasattr(obj.qr_image, "url"):
            request = self.context.get("request")
            return request.build_absolute_uri(obj.qr_image.url) if request else obj.qr_image.url
        return None


class AttendanceScanLogSerializer(serializers.ModelSerializer):
    student = serializers.CharField(source="student_qr.student.code", read_only=True)
    session_date = serializers.DateField(source="session.date", read_only=True)


    class Meta:
        model = AttendanceScanLog
        fields = [
            "id", "scanned_code", "scan_status", "student",
            "session_date", "ip_address", "message", "scanned_at",
        ]

    
    # FIN ASISTENCIAAA--------------------------
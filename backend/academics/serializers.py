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
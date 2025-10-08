# backend/academics/views.py
from rest_framework import generics, permissions
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
from .serializers import (
    EducationLevelSerializer,
    AcademicPeriodSerializer,
    GradeSerializer,
    SectionSerializer,
    SubjectSerializer,
    PersonSerializer,
    StudentSerializer,
    EnrollmentSerializer,
)


class IsStaffUser(permissions.BasePermission):
    """Solo staff puede escribir; lectura cualquiera autenticado."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True  # lectura para autenticados
        return bool(request.user.is_staff)  # escritura solo staff


class EducationLevelListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/levels
    POST /api/levels
    """

    queryset = EducationLevel.objects.all()
    serializer_class = EducationLevelSerializer
    permission_classes = [IsStaffUser]


class EducationLevelDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/levels/<id>
    PATCH  /api/levels/<id>
    DELETE /api/levels/<id>
    """

    queryset = EducationLevel.objects.all()
    serializer_class = EducationLevelSerializer
    permission_classes = [IsStaffUser]


class AcademicPeriodListCreateView(generics.ListCreateAPIView):
    queryset = AcademicPeriod.objects.all()
    serializer_class = AcademicPeriodSerializer
    permission_classes = [IsStaffUser]


class AcademicPeriodDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AcademicPeriod.objects.all()
    serializer_class = AcademicPeriodSerializer
    permission_classes = [IsStaffUser]


class GradeListCreateView(generics.ListCreateAPIView):
    queryset = Grade.objects.select_related("level").all()
    serializer_class = GradeSerializer
    permission_classes = [IsStaffUser]

    def get_queryset(self):
        qs = super().get_queryset()
        level_id = self.request.query_params.get("level")
        if level_id:
            qs = qs.filter(level_id=level_id)
        return qs


class GradeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Grade.objects.select_related("level").all()
    serializer_class = GradeSerializer
    permission_classes = [IsStaffUser]


class SectionListCreateView(generics.ListCreateAPIView):
    queryset = Section.objects.select_related("grade", "grade__level").all()
    serializer_class = SectionSerializer
    permission_classes = [IsStaffUser]

    # Filtros opcionales: ?grade=<id>  y/o  ?level=<id>
    def get_queryset(self):
        qs = super().get_queryset()
        grade_id = self.request.query_params.get("grade")
        level_id = self.request.query_params.get("level")
        if grade_id:
            qs = qs.filter(grade_id=grade_id)
        if level_id:
            qs = qs.filter(grade__level_id=level_id)
        return qs


class SectionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Section.objects.select_related("grade", "grade__level").all()
    serializer_class = SectionSerializer
    permission_classes = [IsStaffUser]


class SubjectListCreateView(generics.ListCreateAPIView):
    queryset = Subject.objects.select_related("level").all()
    serializer_class = SubjectSerializer
    permission_classes = [IsStaffUser]

    # Filtros: ?level=<id>  y ?q=<texto>
    def get_queryset(self):
        qs = super().get_queryset()
        level_id = self.request.query_params.get("level")
        q = self.request.query_params.get("q")
        if level_id:
            qs = qs.filter(level_id=level_id)
        if q:
            qs = qs.filter(name__icontains=q.strip())
        return qs


class SubjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Subject.objects.select_related("level").all()
    serializer_class = SubjectSerializer
    permission_classes = [IsStaffUser]


# --- Persons ---
class PersonListCreateView(generics.ListCreateAPIView):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    permission_classes = [IsStaffUser]

    # Filtros básicos: ?q=  (busca en nombre/apellido/doc/email)
    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.query_params.get("q")
        if q:
            q = q.strip()
            qs = qs.filter(
                models.Q(first_name__icontains=q)
                | models.Q(last_name__icontains=q)
                | models.Q(doc_number__icontains=q)
                | models.Q(email__icontains=q)
            )
        return qs


class PersonDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    permission_classes = [IsStaffUser]


# --- Students ---
class StudentListCreateView(generics.ListCreateAPIView):
    queryset = Student.objects.select_related("person").all()
    serializer_class = StudentSerializer
    permission_classes = [IsStaffUser]

    # Filtro: ?q= (por code o por nombre de persona)
    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.query_params.get("q")
        if q:
            q = q.strip()
            qs = qs.filter(
                models.Q(code__icontains=q)
                | models.Q(person__first_name__icontains=q)
                | models.Q(person__last_name__icontains=q)
            )
        return qs


class StudentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Student.objects.select_related("person").all()
    serializer_class = StudentSerializer
    permission_classes = [IsStaffUser]


class EnrollmentListCreateView(generics.ListCreateAPIView):
    queryset = Enrollment.objects.select_related(
        "student", "student__person", "period", "grade", "section"
    ).all()
    serializer_class = EnrollmentSerializer
    permission_classes = [IsStaffUser]

    # Filtros: ?student=<id>  ?period=<id>  ?grade=<id>  ?section=<id>  ?status=<str>  ?q=<texto>
    def get_queryset(self):
        qs = super().get_queryset()
        p = self.request.query_params
        if p.get("student"):
            qs = qs.filter(student_id=p["student"])
        if p.get("period"):
            qs = qs.filter(period_id=p["period"])
        if p.get("grade"):
            qs = qs.filter(grade_id=p["grade"])
        if p.get("section"):
            qs = qs.filter(section_id=p["section"])
        if p.get("status"):
            qs = qs.filter(status=p["status"])
        q = p.get("q")
        if q:
            q = q.strip()
            qs = qs.filter(
                models.Q(student__code__icontains=q)
                | models.Q(student__person__first_name__icontains=q)
                | models.Q(student__person__last_name__icontains=q)
            )
        return qs


class EnrollmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Enrollment.objects.select_related(
        "student", "student__person", "period", "grade", "section"
    ).all()
    serializer_class = EnrollmentSerializer
    permission_classes = [IsStaffUser]


# Asistencia---------------------------------
from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Count
from academics.models import (
    AttendanceSession,
    AttendanceRecord,
    StudentQRCode,
    AttendanceScanLog,
    Enrollment,
)
from academics.serializers import (
    AttendanceSessionSerializer,
    AttendanceRecordSerializer,
    StudentQRCodeSerializer,
    AttendanceScanLogSerializer,
)
from .views import IsStaffUser  # reutiliza permiso existente


class AttendanceSessionViewSet(viewsets.ModelViewSet):
    queryset = AttendanceSession.objects.all().select_related(
        "grade", "section", "subject", "period", "created_by"
    )
    serializer_class = AttendanceSessionSerializer
    permission_classes = [IsStaffUser]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        session = self.get_object()
        session.is_closed = True
        session.save()
        return Response({"message": "Sesión cerrada"})


class AttendanceRecordViewSet(viewsets.ModelViewSet):
    queryset = AttendanceRecord.objects.select_related(
        "student__person", "session__subject"
    )
    serializer_class = AttendanceRecordSerializer
    permission_classes = [IsStaffUser]

    def perform_create(self, serializer):
        serializer.save(recorded_by=self.request.user)


class StudentQRCodeViewSet(viewsets.ModelViewSet):
    queryset = StudentQRCode.objects.select_related("student__person")
    serializer_class = StudentQRCodeSerializer
    permission_classes = [IsStaffUser]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class QRAttendanceScanView(generics.CreateAPIView):
    """Procesar escaneo con lector de código de barras."""
    permission_classes = [IsStaffUser]

    def post(self, request):
        qr_code = request.data.get("code")
        session_id = request.data.get("session_id")

        try:
            student_qr = StudentQRCode.objects.select_related("student").get(code=qr_code)
        except StudentQRCode.DoesNotExist:
            AttendanceScanLog.objects.create(
                scanned_code=qr_code, scan_status="INVALID_CODE",
                scanned_by=request.user, message="Código no encontrado"
            )
            return Response({"error": "Código inválido"}, status=400)

        valid, msg = student_qr.is_valid()
        if not valid:
            AttendanceScanLog.objects.create(
                scanned_code=qr_code, scan_status="ERROR",
                student_qr=student_qr, scanned_by=request.user, message=msg
            )
            return Response({"error": msg}, status=400)

        try:
            session = AttendanceSession.objects.get(pk=session_id)
        except AttendanceSession.DoesNotExist:
            return Response({"error": "Sesión no encontrada"}, status=400)

        exists = AttendanceRecord.objects.filter(session=session, student=student_qr.student).exists()
        if exists:
            AttendanceScanLog.objects.create(
                scanned_code=qr_code, scan_status="DUPLICATE",
                student_qr=student_qr, session=session, scanned_by=request.user,
                message="Ya registrado"
            )
            return Response({"error": "Asistencia ya registrada"}, status=400)

        enrollment_ok = Enrollment.objects.filter(
            student=student_qr.student,
            grade=session.grade,
            section=session.section,
            period=session.period,
            status="ACTIVE"
        ).exists()
        if not enrollment_ok:
            AttendanceScanLog.objects.create(
                scanned_code=qr_code, scan_status="NOT_ENROLLED",
                student_qr=student_qr, session=session, scanned_by=request.user,
                message="No matriculado"
            )
            return Response({"error": "Estudiante no matriculado"}, status=400)

        now = timezone.now()
        delay_limit = (datetime.combine(now.date(), session.start_time)
                       + timedelta(minutes=5)).time()
        status_value = "RETRASO" if now.time() > delay_limit else "PRESENTE"

        record = AttendanceRecord.objects.create(
            session=session,
            student=student_qr.student,
            status=status_value,
            arrival_time=now.time(),
            recorded_by=request.user,
        )
        student_qr.record_scan()

        AttendanceScanLog.objects.create(
            scanned_code=qr_code, scan_status="SUCCESS",
            student_qr=student_qr, attendance_record=record,
            session=session, scanned_by=request.user,
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            message="Registrado correctamente",
        )
        return Response({"success": True, "status": status_value})


class AttendanceScanLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AttendanceScanLog.objects.select_related(
        "student_qr__student", "session"
    )
    serializer_class = AttendanceScanLogSerializer
    permission_classes = [IsStaffUser]

    @action(detail=False, methods=["get"])
    def stats(self, request):
        data = self.get_queryset().values("scan_status").annotate(total=Count("id"))
        return Response({x["scan_status"]: x["total"] for x in data})

#fin asistenciaaa---------------------------------------------
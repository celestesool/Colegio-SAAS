# backend/academics/views.py
from rest_framework import generics, permissions
from django.db import models
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
from .permissions import (
    IsTeacherOfSubject,
    CanManageGrades,
    IsTenantAdmin,
    CanViewOwnData,
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


# DOCENTES Y ASIGNACIONES
# ---------------------------------
from academics.models import Teacher, TeacherAssignment
from academics.serializers import TeacherSerializer, TeacherAssignmentSerializer


class TeacherListCreateView(generics.ListCreateAPIView):
    queryset = Teacher.objects.select_related("person", "user").all()
    serializer_class = TeacherSerializer
    permission_classes = [IsStaffUser]

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.query_params.get("q")
        is_active = self.request.query_params.get("is_active")
        
        if q:
            q = q.strip()
            qs = qs.filter(
                models.Q(employee_code__icontains=q)
                | models.Q(person__first_name__icontains=q)
                | models.Q(person__last_name__icontains=q)
                | models.Q(user__email__icontains=q)
            )
        
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() == "true")
        
        return qs


class TeacherDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Teacher.objects.select_related("person", "user").all()
    serializer_class = TeacherSerializer
    permission_classes = [IsStaffUser]


class TeacherAssignmentListCreateView(generics.ListCreateAPIView):
    queryset = TeacherAssignment.objects.select_related(
        "teacher", "teacher__person", "subject", "grade", 
        "grade__level", "section", "period"
    ).all()
    serializer_class = TeacherAssignmentSerializer
    permission_classes = [IsStaffUser]

    def get_queryset(self):
        qs = super().get_queryset()
        p = self.request.query_params
        
        if p.get("teacher"):
            qs = qs.filter(teacher_id=p["teacher"])
        if p.get("subject"):
            qs = qs.filter(subject_id=p["subject"])
        if p.get("grade"):
            qs = qs.filter(grade_id=p["grade"])
        if p.get("section"):
            qs = qs.filter(section_id=p["section"])
        if p.get("period"):
            qs = qs.filter(period_id=p["period"])
        if p.get("level"):
            qs = qs.filter(grade__level_id=p["level"])
        if p.get("is_active") is not None:
            qs = qs.filter(is_active=p["is_active"].lower() == "true")
        
        return qs


class TeacherAssignmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TeacherAssignment.objects.select_related(
        "teacher", "teacher__person", "subject", "grade",
        "grade__level", "section", "period"
    ).all()
    serializer_class = TeacherAssignmentSerializer
    permission_classes = [IsStaffUser]

# FIN DOCENTES


# SISTEMA DE CALIFICACIONES
# ---------------------------------
from academics.models import (
    GradingDimension,
    GradingPeriod,
    DimensionWeight,
    StudentGrade,
    GradeAverage,
)
from academics.serializers import (
    GradingDimensionSerializer,
    GradingPeriodSerializer,
    DimensionWeightSerializer,
    StudentGradeSerializer,
    GradeAverageSerializer,
)
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Avg, Count


class GradingDimensionListCreateView(generics.ListCreateAPIView):
    queryset = GradingDimension.objects.all()
    serializer_class = GradingDimensionSerializer
    permission_classes = [IsStaffUser]


class GradingDimensionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = GradingDimension.objects.all()
    serializer_class = GradingDimensionSerializer
    permission_classes = [IsStaffUser]


class GradingPeriodListCreateView(generics.ListCreateAPIView):
    queryset = GradingPeriod.objects.select_related("academic_period").all()
    serializer_class = GradingPeriodSerializer
    permission_classes = [IsStaffUser]

    def get_queryset(self):
        qs = super().get_queryset()
        academic_period = self.request.query_params.get("academic_period")
        is_active = self.request.query_params.get("is_active")
        
        if academic_period:
            qs = qs.filter(academic_period_id=academic_period)
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() == "true")
        
        return qs


class GradingPeriodDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = GradingPeriod.objects.select_related("academic_period").all()
    serializer_class = GradingPeriodSerializer
    permission_classes = [IsStaffUser]


class DimensionWeightListCreateView(generics.ListCreateAPIView):
    queryset = DimensionWeight.objects.select_related(
        "subject", "grade", "dimension"
    ).all()
    serializer_class = DimensionWeightSerializer
    permission_classes = [IsStaffUser]

    def get_queryset(self):
        qs = super().get_queryset()
        p = self.request.query_params
        
        if p.get("subject"):
            qs = qs.filter(subject_id=p["subject"])
        if p.get("grade"):
            qs = qs.filter(grade_id=p["grade"])
        if p.get("dimension"):
            qs = qs.filter(dimension_id=p["dimension"])
        
        return qs


class DimensionWeightDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DimensionWeight.objects.select_related(
        "subject", "grade", "dimension"
    ).all()
    serializer_class = DimensionWeightSerializer
    permission_classes = [IsStaffUser]


class StudentGradeListCreateView(generics.ListCreateAPIView):
    queryset = StudentGrade.objects.select_related(
        "enrollment__student__person",
        "subject",
        "dimension",
        "grading_period",
        "teacher_assignment__teacher__person",
        "recorded_by"
    ).all()
    serializer_class = StudentGradeSerializer
    permission_classes = [CanManageGrades]  

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        
        #  Filtrar según rol
        if user.role == "DOC":
            try:
                teacher = user.teacher
                qs = qs.filter(teacher_assignment__teacher=teacher)
            except:
                return qs.none()
        elif user.role == "EST":
            return qs.none()
        elif user.role == "PAD":
            return qs.none()
        
        p = self.request.query_params
        if p.get("enrollment"):
            qs = qs.filter(enrollment_id=p["enrollment"])
        if p.get("student"):
            qs = qs.filter(enrollment__student_id=p["student"])
        if p.get("subject"):
            qs = qs.filter(subject_id=p["subject"])
        if p.get("dimension"):
            qs = qs.filter(dimension_id=p["dimension"])
        if p.get("grading_period"):
            qs = qs.filter(grading_period_id=p["grading_period"])
        if p.get("period"):
            qs = qs.filter(enrollment__period_id=p["period"])
        if p.get("grade"):
            qs = qs.filter(enrollment__grade_id=p["grade"])
        if p.get("section"):
            qs = qs.filter(enrollment__section_id=p["section"])
        if p.get("teacher"):
            qs = qs.filter(teacher_assignment__teacher_id=p["teacher"])
        
        return qs

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == "DOC":
            teacher_assignment = serializer.validated_data.get('teacher_assignment')
            try:
                if teacher_assignment.teacher != user.teacher:
                    from rest_framework.exceptions import PermissionDenied
                    raise PermissionDenied("No puedes registrar notas para esta asignación")
            except:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("Debes tener un perfil de docente")
        
        serializer.save(recorded_by=self.request.user)
        self._recalculate_average(serializer.instance)

    def _recalculate_average(self, grade_instance):
        """Recalcula el promedio de la materia para el estudiante en el trimestre"""
        enrollment = grade_instance.enrollment
        subject = grade_instance.subject
        grading_period = grade_instance.grading_period
        
        # Obtener todas las notas de las 4 dimensiones
        grades = StudentGrade.objects.filter(
            enrollment=enrollment,
            subject=subject,
            grading_period=grading_period
        ).select_related("dimension")
        
        if grades.count() != 4:
            return  # Esperar a tener las 4 dimensiones
        
        # Obtener pesos personalizados o usar default
        weights = {}
        custom_weights = DimensionWeight.objects.filter(
            subject=subject,
            grade=enrollment.grade
        ).select_related("dimension")
        
        for cw in custom_weights:
            weights[cw.dimension.name] = float(cw.weight)
        
        # Si no hay pesos personalizados, usar default
        if not weights:
            dimensions = GradingDimension.objects.filter(is_active=True)
            for dim in dimensions:
                weights[dim.name] = float(dim.default_weight)
        
        # Calcular promedio ponderado
        total = 0
        for grade in grades:
            weight = weights.get(grade.dimension.name, 25.0)
            total += float(grade.score) * (weight / 100)
        
        # Guardar o actualizar promedio
        GradeAverage.objects.update_or_create(
            enrollment=enrollment,
            subject=subject,
            grading_period=grading_period,
            defaults={"average": round(total, 2)}
        )


class StudentGradeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = StudentGrade.objects.select_related(
        "enrollment__student__person",
        "subject",
        "dimension",
        "grading_period",
        "teacher_assignment__teacher__person",
        "recorded_by"
    ).all()
    serializer_class = StudentGradeSerializer
    permission_classes = [CanManageGrades] 

    def get_queryset(self):

        qs = super().get_queryset()
        user = self.request.user
        
        if user.role == "DOC":
            try:
                teacher = user.teacher
                qs = qs.filter(teacher_assignment__teacher=teacher)
            except:
                return qs.none()
        elif user.role in ["EST", "PAD"]:
            return qs.none()
        
        return qs

    def perform_update(self, serializer):
        #  AGREGAR: Validar permisos antes de actualizar
        user = self.request.user
        if user.role == "DOC":
            try:
                if self.get_object().teacher_assignment.teacher != user.teacher:
                    from rest_framework.exceptions import PermissionDenied
                    raise PermissionDenied("No puedes editar esta nota")
            except:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("Debes tener un perfil de docente")
        serializer.save()
        # Recalcular promedio después de actualizar nota
        self._recalculate_average(serializer.instance)

    def _recalculate_average(self, grade_instance):
        """Mismo método que en Create"""
        enrollment = grade_instance.enrollment
        subject = grade_instance.subject
        grading_period = grade_instance.grading_period
        
        grades = StudentGrade.objects.filter(
            enrollment=enrollment,
            subject=subject,
            grading_period=grading_period
        ).select_related("dimension")
        
        if grades.count() != 4:
            return
        
        weights = {}
        custom_weights = DimensionWeight.objects.filter(
            subject=subject,
            grade=enrollment.grade
        ).select_related("dimension")
        
        for cw in custom_weights:
            weights[cw.dimension.name] = float(cw.weight)
        
        if not weights:
            dimensions = GradingDimension.objects.filter(is_active=True)
            for dim in dimensions:
                weights[dim.name] = float(dim.default_weight)
        
        total = 0
        for grade in grades:
            weight = weights.get(grade.dimension.name, 25.0)
            total += float(grade.score) * (weight / 100)
        
        GradeAverage.objects.update_or_create(
            enrollment=enrollment,
            subject=subject,
            grading_period=grading_period,
            defaults={"average": round(total, 2)}
        )


class GradeAverageListView(generics.ListAPIView):
    queryset = GradeAverage.objects.select_related(
        "enrollment__student__person",
        "subject",
        "grading_period"
    ).all()
    serializer_class = GradeAverageSerializer
    permission_classes = [IsStaffUser]

    def get_queryset(self):
        qs = super().get_queryset()
        p = self.request.query_params
        
        if p.get("enrollment"):
            qs = qs.filter(enrollment_id=p["enrollment"])
        if p.get("student"):
            qs = qs.filter(enrollment__student_id=p["student"])
        if p.get("subject"):
            qs = qs.filter(subject_id=p["subject"])
        if p.get("grading_period"):
            qs = qs.filter(grading_period_id=p["grading_period"])
        if p.get("period"):
            qs = qs.filter(enrollment__period_id=p["period"])
        if p.get("grade"):
            qs = qs.filter(enrollment__grade_id=p["grade"])
        if p.get("section"):
            qs = qs.filter(enrollment__section_id=p["section"])
        
        return qs


class GradeAverageDetailView(generics.RetrieveAPIView):
    queryset = GradeAverage.objects.select_related(
        "enrollment__student__person",
        "subject",
        "grading_period"
    ).all()
    serializer_class = GradeAverageSerializer
    permission_classes = [IsStaffUser]


# Vista especial: Planilla de calificaciones
class GradeSheetView(generics.GenericAPIView):
    """
    Vista tipo planilla para registrar/ver notas de toda una sección.
    GET: Ver planilla completa
    POST: Registrar múltiples notas
    """
    permission_classes = [CanManageGrades]  
    
    def get(self, request):
        """
        Obtener planilla de notas.
        Params: ?grade=id&section=id&subject=id&grading_period=id&period=id
        """
        p = request.query_params
        
        if not all([p.get("grade"), p.get("section"), p.get("subject"), 
                    p.get("grading_period"), p.get("period")]):
            return Response(
                {"error": "Faltan parámetros: grade, section, subject, grading_period, period"},
                status=400
            )
        
        #  AGREGAR: Validar permisos del docente
        user = request.user
        if user.role == "DOC":
            from academics.models import TeacherAssignment
            try:
                has_assignment = TeacherAssignment.objects.filter(
                    teacher=user.teacher,
                    subject_id=p["subject"],
                    grade_id=p["grade"],
                    section_id=p["section"],
                    period_id=p["period"],
                    is_active=True
                ).exists()
                
                if not has_assignment:
                    return Response(
                        {"error": "No tienes asignación para esta materia/grado/sección"},
                        status=403
                    )
            except:
                return Response(
                    {"error": "Debes tener un perfil de docente"},
                    status=403
                )
        
        # Obtener matrículas activas
        enrollments = Enrollment.objects.filter(
            grade_id=p["grade"],
            section_id=p["section"],
            period_id=p["period"],
            status="ACTIVE"
        ).select_related("student__person").order_by("student__code")
        
        # Obtener dimensiones activas
        dimensions = GradingDimension.objects.filter(is_active=True).order_by("name")
        
        # Construir planilla
        sheet_data = []
        for enrollment in enrollments:
            student_data = {
                "enrollment_id": enrollment.id,
                "student_code": enrollment.student.code,
                "student_name": str(enrollment.student.person),
                "grades": {}
            }
            
            # Obtener notas existentes
            grades = StudentGrade.objects.filter(
                enrollment=enrollment,
                subject_id=p["subject"],
                grading_period_id=p["grading_period"]
            ).select_related("dimension")
            
            for grade in grades:
                student_data["grades"][grade.dimension.name] = {
                    "id": grade.id,
                    "score": float(grade.score),
                    "notes": grade.notes
                }
            
            # Obtener promedio si existe
            try:
                avg = GradeAverage.objects.get(
                    enrollment=enrollment,
                    subject_id=p["subject"],
                    grading_period_id=p["grading_period"]
                )
                student_data["average"] = float(avg.average)
            except GradeAverage.DoesNotExist:
                student_data["average"] = None
            
            sheet_data.append(student_data)
        
        return Response({
            "dimensions": [dim.name for dim in dimensions],
            "students": sheet_data
        })
    
    def post(self, request):
        """
        Registrar múltiples notas en batch.
        Body: {
            "grades": [
                {
                    "enrollment": id,
                    "subject": id,
                    "dimension": id,
                    "grading_period": id,
                    "score": 85.5,
                    "teacher_assignment": id,
                    "notes": ""
                },
                ...
            ]
        }
        """
        grades_data = request.data.get("grades", [])
        grades_data = request.data.get("grades", [])
        
        # ✅ AGREGAR: Validar que el docente pueda registrar estas notas
        user = request.user
        if user.role == "DOC":
            teacher_assignments = set()
            for grade_data in grades_data:
                ta_id = grade_data.get("teacher_assignment")
                if ta_id:
                    teacher_assignments.add(ta_id)
            
            from academics.models import TeacherAssignment
            try:
                valid_assignments = TeacherAssignment.objects.filter(
                    id__in=teacher_assignments,
                    teacher=user.teacher,
                    is_active=True
                ).count()
                
                if valid_assignments != len(teacher_assignments):
                    return Response(
                        {"error": "Algunas asignaciones no son válidas para tu usuario"},
                        status=403
                    )
            except:
                return Response(
                    {"error": "Debes tener un perfil de docente"},
                    status=403
                )
        if not grades_data:
            return Response({"error": "No se enviaron notas"}, status=400)
        
        created = []
        updated = []
        errors = []
        
        for grade_data in grades_data:
            serializer = StudentGradeSerializer(data=grade_data, context={"request": request})
            
            if serializer.is_valid():
                # Verificar si ya existe
                existing = StudentGrade.objects.filter(
                    enrollment_id=grade_data["enrollment"],
                    subject_id=grade_data["subject"],
                    dimension_id=grade_data["dimension"],
                    grading_period_id=grade_data["grading_period"]
                ).first()
                
                if existing:
                    serializer = StudentGradeSerializer(
                        existing,
                        data=grade_data,
                        partial=True,
                        context={"request": request}
                    )
                    if serializer.is_valid():
                        serializer.save()
                        updated.append(serializer.data)
                    else:
                        errors.append(serializer.errors)
                else:
                    serializer.save(recorded_by=request.user)
                    created.append(serializer.data)
                    
                    # Recalcular promedio
                    self._recalculate_average(serializer.instance)
            else:
                errors.append(serializer.errors)
        
        return Response({
            "created": len(created),
            "updated": len(updated),
            "errors": errors,
            "details": {
                "created": created,
                "updated": updated
            }
        })
    
    def _recalculate_average(self, grade_instance):
        """Recalcula promedio (mismo método que en StudentGradeListCreateView)"""
        enrollment = grade_instance.enrollment
        subject = grade_instance.subject
        grading_period = grade_instance.grading_period
        
        grades = StudentGrade.objects.filter(
            enrollment=enrollment,
            subject=subject,
            grading_period=grading_period
        ).select_related("dimension")
        
        if grades.count() != 4:
            return
        
        weights = {}
        custom_weights = DimensionWeight.objects.filter(
            subject=subject,
            grade=enrollment.grade
        ).select_related("dimension")
        
        for cw in custom_weights:
            weights[cw.dimension.name] = float(cw.weight)
        
        if not weights:
            dimensions = GradingDimension.objects.filter(is_active=True)
            for dim in dimensions:
                weights[dim.name] = float(dim.default_weight)
        
        total = 0
        for grade in grades:
            weight = weights.get(grade.dimension.name, 25.0)
            total += float(grade.score) * (weight / 100)
        
        GradeAverage.objects.update_or_create(
            enrollment=enrollment,
            subject=subject,
            grading_period=grading_period,
            defaults={"average": round(total, 2)}
        )

# FIN CALIFICACIONES

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
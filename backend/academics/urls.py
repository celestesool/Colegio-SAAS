# backend/academics/urls.py
from django.urls import path
from .views import (
    EducationLevelListCreateView,
    EducationLevelDetailView,
    AcademicPeriodListCreateView,
    AcademicPeriodDetailView,
    GradeListCreateView,
    GradeDetailView,
    SectionListCreateView,
    SectionDetailView,
    SubjectListCreateView,
    SubjectDetailView,
    PersonListCreateView,
    PersonDetailView,
    StudentListCreateView,
    StudentDetailView,
    EnrollmentListCreateView,
    EnrollmentDetailView,
)


urlpatterns = [
    # Education Levels
    path("levels", EducationLevelListCreateView.as_view(), name="level_list_create"),
    path("levels/<int:pk>", EducationLevelDetailView.as_view(), name="level_detail"),
    # Academic Periods
    path("periods", AcademicPeriodListCreateView.as_view(), name="period_list_create"),
    path("periods/<int:pk>", AcademicPeriodDetailView.as_view(), name="period_detail"),
    # Grades
    path("grades", GradeListCreateView.as_view()),
    path("grades/<int:pk>", GradeDetailView.as_view()),
    # Sections
    path("sections", SectionListCreateView.as_view()),
    path("sections/<int:pk>", SectionDetailView.as_view()),
    # Subjects
    path("subjects", SubjectListCreateView.as_view()),
    path("subjects/<int:pk>", SubjectDetailView.as_view()),
    # Persons
    path("persons", PersonListCreateView.as_view()),
    path("persons/<int:pk>", PersonDetailView.as_view()),
    # Students
    path("students", StudentListCreateView.as_view()),
    path("students/<int:pk>", StudentDetailView.as_view()),
    # Enrollments
    path("enrollments", EnrollmentListCreateView.as_view()),
    path("enrollments/<int:pk>", EnrollmentDetailView.as_view()),
]

# === DOCENTES ===
from .views import (
    TeacherListCreateView,
    TeacherDetailView,
    TeacherAssignmentListCreateView,
    TeacherAssignmentDetailView,
)

urlpatterns += [
    path("teachers", TeacherListCreateView.as_view(), name="teacher_list_create"),
    path("teachers/<int:pk>", TeacherDetailView.as_view(), name="teacher_detail"),
    path("teacher-assignments", TeacherAssignmentListCreateView.as_view(), name="assignment_list_create"),
    path("teacher-assignments/<int:pk>", TeacherAssignmentDetailView.as_view(), name="assignment_detail"),
]


# === CALIFICACIONES ===
from .views import (
    GradingDimensionListCreateView,
    GradingDimensionDetailView,
    GradingPeriodListCreateView,
    GradingPeriodDetailView,
    DimensionWeightListCreateView,
    DimensionWeightDetailView,
    StudentGradeListCreateView,
    StudentGradeDetailView,
    GradeAverageListView,
    GradeAverageDetailView,
    GradeSheetView,
)

urlpatterns += [
    # Dimensiones
    path("grading-dimensions", GradingDimensionListCreateView.as_view(), name="dimension_list_create"),
    path("grading-dimensions/<int:pk>", GradingDimensionDetailView.as_view(), name="dimension_detail"),
    
    # Períodos de calificación (trimestres)
    path("grading-periods", GradingPeriodListCreateView.as_view(), name="grading_period_list_create"),
    path("grading-periods/<int:pk>", GradingPeriodDetailView.as_view(), name="grading_period_detail"),
    
    # Pesos de dimensiones personalizados
    path("dimension-weights", DimensionWeightListCreateView.as_view(), name="dimension_weight_list_create"),
    path("dimension-weights/<int:pk>", DimensionWeightDetailView.as_view(), name="dimension_weight_detail"),
    
    # Calificaciones individuales
    path("student-grades", StudentGradeListCreateView.as_view(), name="student_grade_list_create"),
    path("student-grades/<int:pk>", StudentGradeDetailView.as_view(), name="student_grade_detail"),
    
    # Promedios
    path("grade-averages", GradeAverageListView.as_view(), name="grade_average_list"),
    path("grade-averages/<int:pk>", GradeAverageDetailView.as_view(), name="grade_average_detail"),
    
    # Planilla de calificaciones
    path("grade-sheet", GradeSheetView.as_view(), name="grade_sheet"),
]

# === ASISTENCIA ===
from .views import (
    AttendanceSessionViewSet,
    AttendanceRecordViewSet,
    StudentQRCodeViewSet,
    QRAttendanceScanView,
    AttendanceScanLogViewSet,
)
from django.urls import include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"attendance-sessions", AttendanceSessionViewSet, basename="attendance-sessions")
router.register(r"attendance-records", AttendanceRecordViewSet, basename="attendance-records")
router.register(r"student-qr-codes", StudentQRCodeViewSet, basename="student-qr-codes")
router.register(r"attendance-scan-logs", AttendanceScanLogViewSet, basename="attendance-scan-logs")

urlpatterns += [
    path("attendance/qr-scan/", QRAttendanceScanView.as_view(), name="attendance-qr-scan"),
    path("", include(router.urls)),
]


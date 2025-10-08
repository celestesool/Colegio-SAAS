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


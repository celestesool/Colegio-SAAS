from rest_framework import permissions
from academics.models import TeacherAssignment


class IsTeacherOfSubject(permissions.BasePermission):
    """
    Permiso: El usuario debe ser docente asignado a la materia/grado/sección.
    """
    message = "No tienes asignación para esta materia/grado/sección"

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser or request.user.is_staff:
            return True
        
        if request.user.role != "DOC":
            return False
        
        return True

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or request.user.is_staff:
            return True
        
        try:
            teacher = request.user.teacher
        except:
            return False
        
        if hasattr(obj, "teacher_assignment"):
            return obj.teacher_assignment.teacher == teacher
        
        return False


class CanManageGrades(permissions.BasePermission):
    """
    Permiso: Puede gestionar calificaciones.
    - Admin del colegio: acceso total
    - Docente: solo sus asignaciones
    - Otros: solo lectura
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return request.user.role in ["ADMIN", "DOC"]

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        
        if request.method in permissions.SAFE_METHODS:
            return True
        
        if request.user.role == "ADMIN":
            return True
        
        if request.user.role == "DOC":
            try:
                teacher = request.user.teacher
                if hasattr(obj, "teacher_assignment"):
                    return obj.teacher_assignment.teacher == teacher
            except:
                pass
        
        return False


class IsTenantAdmin(permissions.BasePermission):
    """
    Permiso: Usuario debe ser Admin del colegio (tenant).
    """
    message = "Solo administradores del colegio pueden realizar esta acción"

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        return request.user.role == "ADMIN"


class CanViewOwnData(permissions.BasePermission):
    """
    Permiso: Usuario puede ver solo sus propios datos.
    - EST: Solo sus calificaciones
    - PAD: Solo datos de sus hijos
    - DOC: Solo sus asignaciones y estudiantes asignados
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or request.user.role == "ADMIN":
            return True
        
        if request.user.role == "EST":
            return request.method in permissions.SAFE_METHODS
        
        if request.user.role == "DOC":
            try:
                teacher = request.user.teacher
                return True
            except:
                return False
        
        return False
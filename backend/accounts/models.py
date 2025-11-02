from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

class UserManager(BaseUserManager):
    """Manager para autenticar por email (sin username)."""

    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("El email es obligatorio")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser debe tener is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser debe tener is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Usuario base del sistema.
    - Autenticación por email (único).
    - Sin 'username'.
    """

    username = None  # deshabilitamos username
    name = models.CharField(max_length=150, default="user")
    email = models.EmailField(unique=True)

    ROLE_CHOICES = [
        ("ADMIN", "Admin"),
        ("DOC", "Docente"),
        ("EST", "Estudiante"),
        ("PAD", "Padre"),
    ]
    role = models.CharField(max_length=8, choices=ROLE_CHOICES, default="ADMIN")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []  # sin campos extra obligatorios

    objects = UserManager()  # <<< Manager personalizado

    def __str__(self) -> str:
        return f"{self.email} ({self.role})"




class UserManager(BaseUserManager):
    """Manager para autenticar por email (sin username)."""
    # ... código existente sin cambios ...


class User(AbstractUser):
    """
    Usuario base del sistema.
    - Autenticación por email (único).
    - Sin 'username'.
    """
    # ... código existente sin cambios ...
    
    # Métodos adicionales para permisos
    
    def assign_role_permissions(self, role_name=None):
        """
        Asigna permisos predeterminados según el rol del usuario.
        Se ejecuta automáticamente al crear/actualizar usuario.
        """
        if role_name is None:
            role_name = self.role
        
        # Limpiar grupos anteriores
        self.groups.clear()
        
        # Crear o obtener grupo según rol
        group, created = Group.objects.get_or_create(name=f"tenant_{role_name}")
        
        # Asignar permisos según rol
        if role_name == "ADMIN":
            self._assign_admin_permissions(group)
        elif role_name == "DOC":
            self._assign_teacher_permissions(group)
        elif role_name == "EST":
            self._assign_student_permissions(group)
        elif role_name == "PAD":
            self._assign_parent_permissions(group)
        
        # Agregar usuario al grupo
        self.groups.add(group)
    
    def _assign_admin_permissions(self, group):
        """Permisos completos para administrador del colegio"""
        # Admin tiene acceso total (validado en views con is_staff o role=ADMIN)
        pass
    
    def _assign_teacher_permissions(self, group):
        """Permisos para docentes"""
        from django.contrib.contenttypes.models import ContentType
        
        # Modelos académicos que el docente puede gestionar
        models_permissions = [
            'studentgrade',      # Ver y editar notas de sus estudiantes
            'gradeaverage',      # Ver promedios
            'attendancesession', # Gestionar asistencia
            'attendancerecord',  # Registrar asistencia
            'enrollment',        # Ver matrículas
            'student',           # Ver estudiantes
        ]
        
        permissions = []
        for model_name in models_permissions:
            try:
                ct = ContentType.objects.get(app_label='academics', model=model_name)
                # Agregar permisos view y change
                permissions.extend(
                    Permission.objects.filter(
                        content_type=ct,
                        codename__in=[f'view_{model_name}', f'change_{model_name}', f'add_{model_name}']
                    )
                )
            except ContentType.DoesNotExist:
                pass
        
        group.permissions.set(permissions)
    
    def _assign_student_permissions(self, group):
        """Permisos para estudiantes (solo lectura de sus datos)"""
        models_permissions = [
            'studentgrade',      # Ver sus propias notas
            'gradeaverage',      # Ver sus promedios
            'attendancerecord',  # Ver su asistencia
            'enrollment',        # Ver su matrícula
        ]
        
        permissions = []
        for model_name in models_permissions:
            try:
                ct = ContentType.objects.get(app_label='academics', model=model_name)
                # Solo view
                perm = Permission.objects.filter(
                    content_type=ct,
                    codename=f'view_{model_name}'
                ).first()
                if perm:
                    permissions.append(perm)
            except ContentType.DoesNotExist:
                pass
        
        group.permissions.set(permissions)
    
    def _assign_parent_permissions(self, group):
        """Permisos para padres (ver datos de sus hijos)"""
        # Mismos permisos que estudiantes por ahora
        self._assign_student_permissions(group)
    
    def has_tenant_permission(self, permission_codename, obj=None):
        """
        Verifica si el usuario tiene un permiso específico.
        Incluye validaciones por rol y asignaciones.
        """
        # Superusuarios siempre tienen permiso
        if self.is_superuser:
            return True
        
        # Admin del colegio tiene acceso total
        if self.role == "ADMIN":
            return True
        
        # Verificar permiso en Django
        if self.has_perm(f'academics.{permission_codename}'):
            # Validación adicional por objeto (para docentes)
            if obj and self.role == "DOC":
                return self._validate_teacher_access(obj)
            return True
        
        return False
    
    def _validate_teacher_access(self, obj):
        """
        Valida que el docente tenga acceso al objeto específico.
        Solo accede a datos de sus asignaciones.
        """
        try:
            teacher = self.teacher
            
            # Para StudentGrade, verificar teacher_assignment
            if hasattr(obj, 'teacher_assignment'):
                return obj.teacher_assignment.teacher == teacher
            
            # Para Enrollment, verificar si tiene asignación en esa sección
            if hasattr(obj, 'section'):
                from academics.models import TeacherAssignment
                return TeacherAssignment.objects.filter(
                    teacher=teacher,
                    grade=obj.grade,
                    section=obj.section,
                    period=obj.period,
                    is_active=True
                ).exists()
            
            return True
        except:
            return False
    
    def get_accessible_assignments(self):
        """
        Obtiene las asignaciones accesibles para el usuario.
        Útil para filtrar datos en el frontend.
        """
        if self.role != "DOC":
            return None
        
        try:
            from academics.models import TeacherAssignment
            return TeacherAssignment.objects.filter(
                teacher=self.teacher,
                is_active=True
            ).select_related('subject', 'grade', 'section', 'period')
        except:
            return TeacherAssignment.objects.none()

    def save(self, *args, **kwargs):
        """
        Override save para asignar permisos automáticamente.
        """
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Asignar permisos después de crear el usuario
        if is_new or 'role' in kwargs.get('update_fields', []):
            self.assign_role_permissions()
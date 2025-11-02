from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .serializers import UserSerializer
from .models import User
import jwt
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from .models import User

import datetime

now = datetime.datetime.now()


class SignUpView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        payload = {
            "id": serializer.data["id"],
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
        }

        token = jwt.encode(payload, "secret", algorithm="HS256")
        response = Response()
        response.set_cookie(key="jwt", value=token, httponly=True)
        response.data = serializer.data
        return response


class LoginView(APIView):
    def post(self, request):
        email = request.data["email"]
        password = request.data["password"]

        user = User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed("User not found!")
        if not user.check_password(password):
            raise AuthenticationFailed("Incorrect password!")

        payload = {
            "id": user.id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
        }

        token = jwt.encode(payload, "secret", algorithm="HS256")
        response = Response()
        response.set_cookie(key="jwt", value=token, httponly=True)
        response.data = {"jwt": token}
        return response


class UserView(APIView):
    def get(self, request):
        token = request.COOKIES.get("jwt")

        if not token:
            raise AuthenticationFailed("Unauthenticated!")

        try:
            payload = jwt.decode(token, "secret", algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Unauthenticated!")

        user = User.objects.filter(id=payload["id"]).first()
        serializer = UserSerializer(user)
        return Response(serializer.data)


class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie("jwt")
        response.data = {"message": "success"}
        return response


class IsTenantAdminPermission(permissions.BasePermission):
    """Solo admin del colegio puede gestionar permisos"""
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            (request.user.is_superuser or request.user.role == "ADMIN")
        )


@api_view(['GET'])
@permission_classes([IsTenantAdminPermission])
def list_available_permissions(request):
    """
    Lista todos los permisos disponibles del sistema académico.
    GET /api/permissions/available
    """
    # Obtener permisos de la app academics
    content_types = ContentType.objects.filter(app_label='academics')
    permissions = Permission.objects.filter(content_type__in=content_types).select_related('content_type')
    
    perms_data = []
    for perm in permissions:
        perms_data.append({
            "id": perm.id,
            "codename": perm.codename,
            "name": perm.name,
            "model": perm.content_type.model,
            "app": perm.content_type.app_label,
        })
    
    return Response({"permissions": perms_data})


@api_view(['GET', 'POST'])
@permission_classes([IsTenantAdminPermission])
def manage_user_permissions(request, user_id):
    """
    Gestiona permisos individuales de un usuario.
    GET /api/users/{id}/permissions - Ver permisos actuales
    POST /api/users/{id}/permissions - Asignar/actualizar permisos
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "Usuario no encontrado"}, status=404)
    
    if request.method == 'GET':
        # Obtener permisos actuales
        user_perms = user.user_permissions.all().values(
            'id', 'codename', 'name', 'content_type__model'
        )
        group_perms = Permission.objects.filter(
            group__user=user
        ).values('id', 'codename', 'name', 'content_type__model')
        
        return Response({
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role,
            },
            "user_permissions": list(user_perms),
            "group_permissions": list(group_perms),
        })
    
    elif request.method == 'POST':
        # Asignar permisos personalizados
        permission_ids = request.data.get('permissions', [])
        
        try:
            permissions = Permission.objects.filter(id__in=permission_ids)
            user.user_permissions.set(permissions)
            
            return Response({
                "message": "Permisos actualizados correctamente",
                "assigned_permissions": list(permissions.values('id', 'codename', 'name'))
            })
        except Exception as e:
            return Response({"error": str(e)}, status=400)


@api_view(['GET'])
@permission_classes([IsTenantAdminPermission])
def list_role_permissions(request, role):
    """
    Lista los permisos predeterminados de un rol.
    GET /api/roles/{role}/permissions
    """
    valid_roles = ['ADMIN', 'DOC', 'EST', 'PAD']
    if role not in valid_roles:
        return Response({"error": "Rol inválido"}, status=400)
    
    try:
        group = Group.objects.get(name=f"tenant_{role}")
        permissions = group.permissions.all().values(
            'id', 'codename', 'name', 'content_type__model'
        )
        
        return Response({
            "role": role,
            "group_name": group.name,
            "permissions": list(permissions)
        })
    except Group.DoesNotExist:
        return Response({
            "role": role,
            "permissions": [],
            "message": "Grupo no existe, se creará al asignar usuario"
        })


@api_view(['POST'])
@permission_classes([IsTenantAdminPermission])
def update_role_permissions(request, role):
    """
    Actualiza los permisos predeterminados de un rol.
    POST /api/roles/{role}/permissions
    Body: {"permissions": [1, 2, 3, ...]}
    """
    valid_roles = ['ADMIN', 'DOC', 'EST', 'PAD']
    if role not in valid_roles:
        return Response({"error": "Rol inválido"}, status=400)
    
    permission_ids = request.data.get('permissions', [])
    
    try:
        group, created = Group.objects.get_or_create(name=f"tenant_{role}")
        permissions = Permission.objects.filter(id__in=permission_ids)
        group.permissions.set(permissions)
        
        return Response({
            "message": f"Permisos del rol {role} actualizados correctamente",
            "assigned_permissions": list(permissions.values('id', 'codename', 'name'))
        })
    except Exception as e:
        return Response({"error": str(e)}, status=400)
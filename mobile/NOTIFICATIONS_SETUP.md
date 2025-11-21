# Guía de Configuración de Notificaciones Push

## Descripción General
Se ha implementado un sistema completo de notificaciones push en tiempo real utilizando Firebase Cloud Messaging (FCM) con soporte para funcionamiento con y sin conexión a internet.

## Características Implementadas

### 1. **Servicios Principales**
- ✅ `FirebaseNotificationService`: Servicio central de notificaciones
- ✅ `DatabaseService`: Almacenamiento local de notificaciones
- ✅ `ConnectivityService`: Detección de conexión a internet

### 2. **Pantallas**
- ✅ `ReceivedNotificationsScreen`: Visualización de notificaciones recibidas
- ✅ `CreateNotificationScreen`: Formulario para crear notificaciones

### 3. **Funcionalidades**
- ✅ Notificaciones push en tiempo real
- ✅ Base de datos local (SQLite) para almacenamiento
- ✅ Sincronización automática cuando se recupera la conexión
- ✅ Marcación de notificaciones como leídas
- ✅ Eliminación de notificaciones
- ✅ Soporte para iOS y Android

## Pasos de Configuración

### Paso 1: Crear Proyecto en Firebase

1. Ir a [Firebase Console](https://console.firebase.google.com/)
2. Crear un nuevo proyecto o usar uno existente
3. Anotar el ID del proyecto

### Paso 2: Configurar Firebase para Android

1. En Firebase Console, selecciona tu proyecto
2. Ve a Configuración del proyecto
3. Descarga el archivo `google-services.json`
4. Coloca el archivo en: `android/app/google-services.json`

### Paso 3: Configurar gradle (build.gradle.kts)

El archivo `android/build.gradle.kts` debe incluir:

```kotlin
dependencies {
    classpath("com.google.gms:google-services:4.3.15")
}
```

El archivo `android/app/build.gradle.kts` debe incluir:

```kotlin
plugins {
    id("com.google.gms.google-services")
}
```

### Paso 4: Instalar Paquetes Flutter

```bash
flutter pub get
```

Los paquetes necesarios ya están en `pubspec.yaml`:
- `firebase_core`: ^2.24.2
- `firebase_messaging`: ^14.6.2
- `flutter_local_notifications`: ^17.0.0
- `connectivity_plus`: ^5.0.0
- `sqflite`: ^2.3.0
- `internet_connection_checker`: ^1.0.0

### Paso 5: Configurar AndroidManifest.xml

Asegúrate de que en `android/app/src/main/AndroidManifest.xml` contenga:

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <!-- Permisos existentes -->
    
    <!-- Permisos para notificaciones -->
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
    
    <application>
        <!-- Tu aplicación -->
    </application>
</manifest>
```

### Paso 6: Obtener Token FCM

El token se obtiene automáticamente en la inicialización. Se imprime en la consola:

```
FCM Token: YOUR_FCM_TOKEN
```

Este token debe enviarse al servidor para registrar el dispositivo.

## Uso

### Para Recibir Notificaciones

1. Las notificaciones llegarán automáticamente a través de Firebase
2. Se mostrarán automáticamente en primer plano y background
3. Se guardarán en la base de datos local

### Para Enviar Notificaciones

1. Ve a la pantalla "Crear Notificación" desde el drawer
2. Completa:
   - Título
   - Contenido
   - Destinatario
3. Haz clic en "Enviar Notificación"

### Para Ver Notificaciones Recibidas

1. Ve a "Notificaciones Recibidas" en el drawer
2. Las notificaciones se muestran ordenadas por fecha
3. Puedes:
   - Marcar como leída
   - Eliminar
   - Ver detalles

## Configuración sin Internet

El sistema funciona automáticamente sin internet:

1. **Notificaciones Pendientes**: Se guardan en la BD local
2. **Sincronización Automática**: Cuando se recupera la conexión, se sincronizan
3. **Almacenamiento Local**: Todas las notificaciones se guardan localmente

## Estructura de Base de Datos

### Tabla: `notifications`
```sql
- id (PRIMARY KEY)
- notification_id (UNIQUE)
- title
- body
- sender
- sent_at
- received_at
- is_read
- data
```

### Tabla: `pending_notifications`
```sql
- id (PRIMARY KEY)
- title
- body
- recipient
- created_at
- status (pending/sent)
- retry_count
```

## Archivos Creados/Modificados

### Servicios
- `lib/core/services/firebase_notification_service.dart`
- `lib/core/services/database_service.dart`
- `lib/core/services/connectivity_service.dart`

### Pantallas
- `lib/features/notifications/screens/received_notifications_screen.dart`
- `lib/features/notifications/screens/create_notification_screen.dart`

### Configuración
- `pubspec.yaml` (actualizado)
- `lib/main.dart` (inicialización de Firebase)
- `lib/routes/app_routes.dart` (rutas de notificaciones)
- `lib/core/widgets/app_drawer.dart` (acceso a notificaciones)
- `android/app/google-services.json` (plantilla)

## Próximos Pasos

1. **Configurar Backend**: Implementar API para envío de notificaciones
2. **Integrar con Base de Datos**: Conectar con el servidor para validar destinatarios
3. **Pruebas**: Probar con Firebase Console antes de usar desde la app
4. **Publicar APK**: Considerar las configuraciones de release

## Pruebas en Firebase Console

1. Ve a Firebase Console → Cloud Messaging
2. Haz clic en "Enviar tu primer mensaje"
3. Completa:
   - Título
   - Contenido
   - Target: Selecciona "FCM Registration token"
   - Pega el token que se imprimió en la consola
4. Haz clic en "Enviar"

## Solución de Problemas

### La app no recibe notificaciones
1. Verifica que el token FCM sea correcto
2. Comprueba los permisos en AndroidManifest.xml
3. Revisa la consola para mensajes de error

### Las notificaciones no aparecen en background
1. Asegúrate de que `_firebaseBackgroundMessageHandler` esté correctamente decorado con `@pragma('vm:entry-point')`
2. Verifica los permisos de notificación

### Sin conexión a internet
1. El sistema guarda automáticamente en BD local
2. Cuando se recupere la conexión, se sincronizarán
3. Verifica la tabla `pending_notifications`

## Contacto y Soporte

Para más información sobre Firebase Messaging:
- [Documentación Oficial](https://firebase.flutter.dev/docs/messaging/overview/)
- [Firebase Cloud Messaging](https://firebase.google.com/docs/cloud-messaging)

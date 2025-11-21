# Guía de Pruebas - Sistema de Notificaciones Push

## Pruebas en Desarrollo

### 1. Verificar Inicialización de Firebase

En `lib/main.dart`, verifica los logs:

```dart
flutter run
```

Deberías ver en la consola:
```
I/firebase: User autorizó notificaciones: AuthorizationStatus.authorized
I/firebase: FCM Token: eF1z...YOUR_TOKEN...
```

Copia el token FCM para las pruebas.

### 2. Prueba de Notificación en Primer Plano

**Pasos:**
1. Ejecuta la app
2. Ve a Firebase Console → Cloud Messaging
3. Haz clic en "Enviar tu primer mensaje"
4. Completa:
   - Título: "Prueba Foreground"
   - Cuerpo: "¿Ves esta notificación?"
5. Selecciona Target: FCM Registration token
6. Pega tu token FCM
7. Haz clic en "Enviar"

**Resultado esperado:**
- Se muestra una notificación local automáticamente
- Se guarda en la BD local
- Aparece en "Notificaciones Recibidas"

### 3. Prueba de Notificación en Background

**Pasos:**
1. Con la app ejecutándose, presiona el botón "Home" (volver a home del dispositivo)
2. La app entra en background pero sigue corriendo
3. Envía notificación desde Firebase Console (igual que paso 2)

**Resultado esperado:**
- Se muestra una notificación del sistema
- Si haces clic, la app se abre
- Aparece en "Notificaciones Recibidas"

### 4. Prueba de Notificación Cerrada (Killed)

**Pasos:**
1. Con la app ejecutándose, presiona "Recent Apps" (botón de tareas)
2. Desliza hacia arriba para cerrar la app completamente
3. Envía notificación desde Firebase Console

**Resultado esperado:**
- Se muestra una notificación del sistema
- Si haces clic, la app se abre
- Aparece en "Notificaciones Recibidas"

### 5. Prueba de Conectividad

#### Sin Conexión:

**Pasos:**
1. Abre la app
2. Desactiva WiFi e internet móvil
3. Ve a "Crear Notificación"
4. Llena el formulario y envía

**Resultado esperado:**
- Se muestra mensaje: "Sin conexión - Las notificaciones se guardarán..."
- Se guarda como "pending" en la BD
- Se muestra snackbar de confirmación

#### Reconectando:

**Pasos:**
1. Desde el estado anterior, activa internet nuevamente
2. Actualiza la pantalla o navega
3. Verifica la BD de pendientes

**Resultado esperado:**
- El estado de conectividad cambia a verde
- Se intenta sincronizar automáticamente

### 6. Prueba de Crear Notificación

**Pasos:**
1. Ve al drawer (menú hamburguesa)
2. Haz clic en "Crear Notificación"
3. Completa:
   - Título: "Notificación de prueba"
   - Contenido: "Esta es una prueba"
   - Destinatario: "usuario123"
4. Haz clic en "Enviar"

**Resultado esperado:**
- Se muestra confirmación
- Se guarda en BD
- Aparece en "Notificaciones Recibidas" (si hay conexión)

### 7. Prueba de Ver Notificaciones

**Pasos:**
1. Ve al drawer
2. Haz clic en "Notificaciones Recibidas"
3. Verifica la lista

**Resultado esperado:**
- Se muestra lista de todas las notificaciones
- Las no leídas tienen fondo azul claro
- Las leídas tienen fondo blanco
- Se puede:
  - Marcar como leída
  - Eliminar
  - Refrescar con swipe down

### 8. Prueba de Marcar como Leída

**Pasos:**
1. En "Notificaciones Recibidas"
2. Presiona una notificación no leída
3. O toca el menú y selecciona "Marcar como leída"

**Resultado esperado:**
- El color de fondo cambia de azul a blanco
- El icono cambia
- No se muestra la opción nuevamente

### 9. Prueba de Eliminar Notificación

**Pasos:**
1. En "Notificaciones Recibidas"
2. Presiona el menú (3 puntos) de una notificación
3. Selecciona "Eliminar"
4. Confirma en el diálogo

**Resultado esperado:**
- Se elimina de la lista
- Se elimina de la BD
- Se muestra confirmación

### 10. Prueba de Sincronización

**Escenario sin conexión → reconexión:**

```
1. Sin internet
   ↓
2. Crear 3 notificaciones pendientes
   ↓
3. Verificar en DB que estén marcadas como "pending"
   ↓
4. Conectar a internet
   ↓
5. Esperar sincronización automática
   ↓
6. Verificar que el estado cambió a "sent"
```

## Pruebas Avanzadas

### 1. Prueba de Estrés (Muchas Notificaciones)

```bash
# Enviar 10 notificaciones de prueba
for i in {1..10}; do
  curl -X POST \
    https://fcm.googleapis.com/fcm/send \
    -H 'Content-Type: application/json' \
    -H "Authorization: key=YOUR_SERVER_API_KEY" \
    -d '{
      "to": "YOUR_FCM_TOKEN",
      "notification": {
        "title": "Prueba '$i'",
        "body": "Notificación número '$i'"
      }
    }'
done
```

**Verificar:**
- La app no se congela
- Todas las notificaciones se guardan
- No hay pérdida de datos

### 2. Prueba de Datos Personalizados

**Desde Firebase Console:**

```json
{
  "to": "YOUR_FCM_TOKEN",
  "notification": {
    "title": "Calificación actualizada",
    "body": "Tienes una nueva nota"
  },
  "data": {
    "type": "grade",
    "student_id": "123",
    "subject": "Matemáticas",
    "grade": "95"
  }
}
```

**Verificar:**
- Los datos se guardan correctamente
- Se pueden recuperar de la BD

### 3. Prueba de Rotación de Pantalla

**Pasos:**
1. Abre "Notificaciones Recibidas"
2. Rota el dispositivo (landscape/portrait)
3. Verifica que:
   - La lista se mantiene
   - No se pierde scroll
   - Los datos persisten

### 4. Prueba de Memoria

**Con Android Studio:**

1. Abre Android Profiler
2. Navega por las pantallas de notificaciones
3. Verifica:
   - Uso de memoria normal
   - No hay memory leaks
   - Garbage collection funciona

## Pruebas en Dispositivos Reales

### Android

```bash
# Conectar dispositivo y ejecutar
flutter run --release

# Ver logs
flutter logs

# Desinstalar y reinstalar
flutter clean
flutter pub get
flutter run --release
```

### Verificaciones:

- [ ] Conexión WiFi funciona
- [ ] Conexión móvil funciona
- [ ] Sin conexión guarda localmente
- [ ] Las notificaciones sonoras funcionan
- [ ] Las vibraciones funcionan
- [ ] Los permisos se solicitan correctamente

## Pruebas de Integración

### Escenario 1: Flujo Completo

```
1. Instalar app
2. Abrir por primera vez
3. Conceder permisos
4. Recibir notificación
5. Ver en lista
6. Marcar como leída
7. Eliminar
8. Crear nueva
9. Cerrar app
10. Recibir mientras cerrada
11. Abrir desde notificación
12. Verificar datos
```

### Escenario 2: Sin Conexión

```
1. Abrir sin conexión
2. Ver estado offline
3. Crear notificación
4. Conectar
5. Verificar sincronización
6. Ver estado online
```

### Escenario 3: Múltiples Usuarios

```
1. Usuario A crea notificación para B
2. Usuario B recibe
3. Usuario B marca como leída
4. Usuario A ve estado
```

## Comandos de Depuración

### Ver Base de Datos Local

```bash
# Desde Android Studio
# Device File Explorer → data/data/com.example.colegio_app/databases/colegio_app.db
```

### Ver Token FCM

En `lib/main.dart`:
```dart
String? token = await FirebaseMessaging.instance.getToken();
print('FCM Token: $token');
```

### Verificar Permisos

```bash
adb shell dumpsys package com.example.colegio_app | grep android.permission
```

### Ver Logs de Firebase

```bash
adb logcat | grep firebase
```

## Checklist de Pruebas

### Básicas
- [ ] App se abre sin errores
- [ ] Firebase se inicializa
- [ ] Se obtiene FCM token
- [ ] Permisos se solicitan

### Notificaciones
- [ ] Se reciben en foreground
- [ ] Se reciben en background
- [ ] Se reciben cuando app está cerrada
- [ ] Se guardan en BD

### UI
- [ ] Se muestra lista de notificaciones
- [ ] Se pueden marcar como leídas
- [ ] Se pueden eliminar
- [ ] Se puede crear notificación

### Conectividad
- [ ] Sin internet guarda localmente
- [ ] Con internet envía inmediatamente
- [ ] Se sincroniza al recuperar conexión
- [ ] El indicador de estado funciona

### Persistencia
- [ ] Los datos se guardan en BD
- [ ] Se recuperan después de cerrar app
- [ ] No hay duplicados
- [ ] No hay datos corruptos

## Reportar Errores

Al encontrar un error, proporciona:

1. **Descripción**: ¿Qué intentaste hacer?
2. **Pasos**: ¿Cómo reproducirlo?
3. **Logs**: Consola de Flutter
4. **Dispositivo**: Modelo, versión de Android
5. **Estado**: ¿Hay conexión?
6. **Screenshots**: Pantallazos si es posible

Ejemplo:
```
Título: Las notificaciones no se guardan sin conexión

Pasos para reproducir:
1. Desactivar internet
2. Crear notificación
3. Verificar BD

Resultado esperado:
Se guarda como "pending"

Resultado actual:
Muestra error "Sin conexión"

Logs:
[ERROR] DatabaseException: ...

Dispositivo: Pixel 4a, Android 12
```


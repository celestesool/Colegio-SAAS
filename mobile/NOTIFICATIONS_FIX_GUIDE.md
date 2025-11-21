# Guía de Corrección de Notificaciones Push - Flutter Local Notifications

## 🎯 Problema Resuelto

Las notificaciones solo hacían vibrar el dispositivo pero no aparecían como:
- Ventana emergente en la parte superior del celular
- Banner de notificación
- Notificación en el centro de notificaciones

## ✅ Cambios Realizados

### 1. **Actualización: `connectivity_service.dart`**

Se modificó el método `_showNotification()` con los siguientes cambios:

#### Cambios principales:
- ✅ Cambió `Importance.high` → `Importance.max` (máxima importancia)
- ✅ Cambió `Priority.high` → `Priority.max` (máxima prioridad)
- ✅ Agregó `enableVibration: vibrationEnabled` (vibración explícita)
- ✅ Agregó `vibrationPattern: [0, 500, 200, 500]` (patrón de vibración)
- ✅ Agregó `fullScreenIntent: true` (mostrar como emergente)
- ✅ Removió llamada manual a `Vibration.vibrate()` (ahora es manejada por el sistema)

```dart
final androidDetails = AndroidNotificationDetails(
  'notificaciones_channel',
  'Notificaciones',
  channelDescription: 'Canal de notificaciones de la app',
  importance: Importance.max,  // ← MAX en lugar de HIGH
  priority: Priority.max,      // ← MAX en lugar de HIGH
  showWhen: true,
  sound: soundEnabled ? RawResourceAndroidNotificationSound('notification_sound') : null,
  playSound: soundEnabled,
  enableVibration: vibrationEnabled,  // ← Explícito
  vibrationPattern: vibrationEnabled ? [0, 500, 200, 500] : null,  // ← Patrón
  fullScreenIntent: true,  // ← Emergente en pantalla
);
```

### 2. **Configuración: `MainActivity.kt`**

Se agregó configuración nativa de canales de notificación en Kotlin:

```kotlin
package com.example.colegio_app

import io.flutter.embedding.android.FlutterActivity
import android.app.NotificationChannel
import android.app.NotificationManager
import android.os.Build

class MainActivity : FlutterActivity() {
    override fun onCreate(savedInstanceState: android.os.Bundle?) {
        super.onCreate(savedInstanceState)
        createNotificationChannels()
    }

    private fun createNotificationChannels() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val notificationManager = getSystemService(NotificationManager::class.java)
            
            // Canal de notificaciones con máxima importancia
            val channel = NotificationChannel(
                "notificaciones_channel",
                "Notificaciones",
                NotificationManager.IMPORTANCE_MAX
            ).apply {
                description = "Canal de notificaciones de la app"
                enableVibration(true)
                enableLights(true)
                setShowBadge(true)
            }
            
            notificationManager?.createNotificationChannel(channel)
        }
    }
}
```

#### ¿Por qué es importante?
- Crea el canal con `IMPORTANCE_MAX` (máxima importancia)
- Habilita vibración a nivel de canal
- Activa indicadores visuales (luces)
- Activa el badge en el ícono de la app

### 3. **Permisos: `AndroidManifest.xml`**

Se agregaron permisos necesarios:

```xml
<uses-permission android:name="android.permission.VIBRATE" />
<uses-permission android:name="android.permission.USE_FULL_SCREEN_INTENT" />
```

## 🚀 Cómo Probar

### Opción 1: Usando la App (Manual)

1. **Compila y ejecuta la app:**
   ```bash
   flutter clean
   flutter pub get
   flutter run
   ```

2. **En el drawer de la app, selecciona "Crear Notificación"**

3. **Completa los campos:**
   - Título: "Prueba de Notificación"
   - Contenido: "Esta es una notificación de prueba"
   - Destinatario: (si aplica)

4. **Haz clic en "Enviar Notificación"**

5. **Verifica que:**
   - ✅ Aparezca un banner en la parte superior del celular
   - ✅ El celular vibre
   - ✅ En el centro de notificaciones (bajando la barra) aparezca la notificación
   - ✅ La notificación persista en el centro

### Opción 2: Usando Firebase Console (Si tienes Firebase configurado)

1. Ve a [Firebase Console](https://console.firebase.google.com/)
2. Selecciona tu proyecto
3. Ve a **Cloud Messaging** → **Enviar tu primer mensaje**
4. Completa:
   - Título: "Prueba Firebase"
   - Contenido: "Notificación de prueba"
   - Target: Token FCM
5. Envía y verifica

### Opción 3: Usando Backend API (Si tienes backend)

```bash
curl -X POST https://tu-backend.com/api/notificacion/crear/ \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "Notificación de Prueba",
    "mensaje": "Esto es una prueba"
  }'
```

## 📋 Requisitos Previos Verificados

✅ `pubspec.yaml` contiene:
- `flutter_local_notifications: ^19.5.0`
- `vibration: ^3.1.4`
- `connectivity_plus: ^5.0.0`

✅ Permisos en `AndroidManifest.xml`:
- `POST_NOTIFICATIONS`
- `INTERNET`
- `ACCESS_NETWORK_STATE`
- `VIBRATE` (nuevo)
- `USE_FULL_SCREEN_INTENT` (nuevo)

✅ Min SDK de Flutter: ^3.9.2

## 🔧 Troubleshooting

### Las notificaciones aún no aparecen como banner

**Solución:**
1. Limpia la compilación: `flutter clean`
2. Reconstruye: `flutter pub get`
3. Ejecuta nuevamente: `flutter run`
4. En algunos dispositivos Samsung, revisa "Notificaciones activas" en Configuración

### El vibration patrón no funciona

**Solución:**
- Algunos dispositivos no soportan patrones de vibración
- Verifica en "Configuración → Sonido y vibración" que esté habilitada

### La app en background no recibe notificaciones

**Nota:** Este sistema usa polling cada 30 segundos cuando la app está en background
- Para notificaciones en tiempo real en background, usa Firebase Messaging
- El polling es más eficiente en conexiones metered

### El sonido no suena

**Verificaciones:**
1. En la app, ve a Configuración y asegúrate que "Sonido en notificaciones" esté habilitado
2. El dispositivo no está en modo silencioso
3. Comprueba que exista el archivo `notification_sound` en res/raw

## 📊 Explicación Técnica

### Importancia vs Prioridad

| Nivel | Importancia | Prioridad | Comportamiento |
|-------|-------------|-----------|---|
| **MAX** | Muestra banner | Urgente | ✅ Aparece como ventana emergente |
| **HIGH** | No siempre aparece | Alta | ⚠️ Solo con Head-up |
| **DEFAULT** | Silenciosa | Normal | ❌ Solo en bandeja |
| **LOW** | Silenciosa | Baja | ❌ Sin sonido |

### Por qué `Importance.max` es necesario

- **Android 8.0+**: Las notificaciones usan el sistema de Canales
- **Importance.max** garantiza que la notificación sea urgente
- Hace que aparezca como "head-up notification" (ventana flotante)
- Se acompaña de sonido y vibración por defecto

### fullScreenIntent para pantalla bloqueada

- Permite mostrar notificaciones incluso con pantalla bloqueada
- Requiere permiso `USE_FULL_SCREEN_INTENT`
- Ideal para notificaciones críticas

## 🎨 Customización Adicional (Opcional)

Si quieres más control, puedes modificar los colores y estilo:

```dart
final androidDetails = AndroidNotificationDetails(
  'notificaciones_channel',
  'Notificaciones',
  channelDescription: 'Canal de notificaciones de la app',
  importance: Importance.max,
  priority: Priority.max,
  color: const Color.fromARGB(255, 255, 0, 0), // Color rojo
  largeIcon: const DrawableResolution(name: 'app_icon'),
  styleInformation: BigTextStyleInformation(
    mensaje,
    htmlFormatBigText: true,
    contentTitle: titulo,
  ),
);
```

## 📱 Configuración por Dispositivo

### Samsung
- Configuración → Notificaciones → Permitir notificaciones
- Configuración → Notificaciones Activas

### Xiaomi
- Configuración → Aplicaciones → Permisos
- Asegurar "Mostrar en la parte superior" está habilitado

### Pixel/Stock Android
- Configuración → Aplicaciones → Permisos → Notificaciones
- Permitir notificaciones

## ✨ Resumen Final

Con estos cambios, tus notificaciones ahora:
- ✅ Aparecen como banner en la parte superior
- ✅ Vibran con un patrón personalizado
- ✅ Aparecen en el centro de notificaciones
- ✅ Persisten hasta que se descartan
- ✅ Muestran título y contenido claramente

## 📞 Contacto

Si aún hay problemas, verifica:
1. Que el dispositivo esté actualizado a Android 8.0+
2. Los permisos estén otorgados a la app
3. El estado de la batería no esté en modo muy ahorro

---

**Última actualización:** Noviembre 21, 2025

# Sistema de Notificaciones Push - Resumen Técnico

## Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    APLICACIÓN FLUTTER                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │        CAPA DE PRESENTACIÓN (UI)                    │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │ • ReceivedNotificationsScreen                      │   │
│  │ • CreateNotificationScreen                         │   │
│  │ • AppDrawer (con acceso a notificaciones)          │   │
│  └─────────────────────────────────────────────────────┘   │
│                           ↓                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │     CAPA DE SERVICIOS (Business Logic)             │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │ • FirebaseNotificationService                      │   │
│  │   - Maneja FCM                                      │   │
│  │   - Gestiona notificaciones locales                │   │
│  │   - Sincroniza con backend                         │   │
│  │                                                     │   │
│  │ • ConnectivityService                              │   │
│  │   - Detecta conexión a internet                    │   │
│  │   - Monitorea cambios de red                       │   │
│  │                                                     │   │
│  │ • DatabaseService                                  │   │
│  │   - Gestiona SQLite local                          │   │
│  │   - Almacena notificaciones                        │   │
│  └─────────────────────────────────────────────────────┘   │
│                           ↓                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │    CAPA DE PERSISTENCIA (Data Storage)             │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │ • SQLite Database                                   │   │
│  │   - Tabla: notifications                            │   │
│  │   - Tabla: pending_notifications                   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
         ↓                                    ↓
    ┌────────────────┐            ┌──────────────────────┐
    │  FIREBASE FCM  │            │ SERVIDOR BACKEND     │
    │  (Push Alerts) │            │ (API REST)           │
    └────────────────┘            └──────────────────────┘
```

## Flujo de Notificaciones

### Recepción de Notificaciones:

```
Firebase Cloud Messaging
    ↓
┌─────────────────────────────────────┐
│ ¿App en Primer Plano?               │
└─────────────────────────────────────┘
    ↙                               ↘
   SÍ                               NO
    ↓                               ↓
Mostrar            FirebaseMessaging.onMessageOpenedApp
Notificación          ↓
Local            Background Handler
    ↓                  ↓
Guardar en DB      Guardar en DB
    ↓                  ↓
Actualizar         Esperar a que
UI                 el usuario
                   abra la app
```

### Envío de Notificaciones:

```
Usuario crea notificación
    ↓
┌──────────────────────────┐
│ ¿Hay conexión?           │
└──────────────────────────┘
    ↙                   ↘
   SÍ                  NO
    ↓                  ↓
Enviar a           Guardar como
Servidor           "pending"
    ↓                  ↓
    └──────┬───────────┘
           ↓
    Guardar en BD Local
           ↓
    Notificar al Usuario
```

## Estructura de Bases de Datos

### Tabla: notifications
```
┌────────────────────────────────────────┐
│ notifications                          │
├────────────────────────────────────────┤
│ id (PK)            INTEGER             │
│ notification_id    TEXT (UNIQUE)       │
│ title              TEXT                │
│ body               TEXT                │
│ sender             TEXT                │
│ sent_at            TEXT (ISO8601)      │
│ received_at        TEXT (ISO8601)      │
│ is_read            INTEGER (0/1)       │
│ data               TEXT                │
└────────────────────────────────────────┘
```

### Tabla: pending_notifications
```
┌────────────────────────────────────────┐
│ pending_notifications                  │
├────────────────────────────────────────┤
│ id (PK)            INTEGER             │
│ title              TEXT                │
│ body               TEXT                │
│ recipient          TEXT                │
│ created_at         TEXT (ISO8601)      │
│ status             TEXT (enum)         │
│ retry_count        INTEGER             │
└────────────────────────────────────────┘
```

## Paquetes Instalados

| Paquete | Versión | Propósito |
|---------|---------|----------|
| firebase_core | ^2.24.2 | Inicialización de Firebase |
| firebase_messaging | ^14.6.2 | Recepción de notificaciones FCM |
| flutter_local_notifications | ^17.0.0 | Notificaciones locales |
| connectivity_plus | ^5.0.0 | Detección de conectividad |
| sqflite | ^2.3.0 | Base de datos SQLite |
| internet_connection_checker | ^1.0.0 | Verificación de internet |
| get_it | ^7.6.0 | Inyección de dependencias (opcional) |

## Flujo de Inicialización

```
main()
  ↓
WidgetsFlutterBinding.ensureInitialized()
  ↓
FirebaseNotificationService.initialize()
  ├─ await Firebase.initializeApp()
  ├─ Solicitar permisos
  ├─ _initializeLocalNotifications()
  ├─ _setupMessageHandlers()
  │  ├─ FirebaseMessaging.onMessage
  │  ├─ FirebaseMessaging.onMessageOpenedApp
  │  └─ FirebaseMessaging.onBackgroundMessage
  ├─ Obtener FCM Token
  └─ Registrar en servidor (TODO)
  ↓
runApp(MyApp())
```

## Ciclo de Vida de una Notificación

### Recibida:
```
1. Llega FCM
2. Sistema detecta origen
3. Si está en foreground → Mostrar local notification
4. Si está en background → Manejador background
5. Guardar en DB
6. Notificar UI
7. Usuario puede marcar como leída
8. Usuario puede eliminar
```

### Enviada:
```
1. Usuario completa formulario
2. Sistema verifica conexión
3. Si hay conexión:
   - Envía a API del servidor
   - Marca como "sent"
4. Si NO hay conexión:
   - Guarda como "pending"
   - Espera reconexión
   - Reintenta automáticamente
```

## Configuración por Plataforma

### Android
- ✅ Notificaciones en foreground
- ✅ Notificaciones en background
- ✅ Manejador de clics
- ✅ Canales de notificación

### iOS
- ✅ Notificaciones en foreground
- ✅ Notificaciones en background (con certificados)
- ✅ Manejador de clics
- ✅ Sonidos personalizados

## Estados de Conectividad

```
┌──────────────────────┐
│  CON CONEXIÓN        │
└──────────────────────┘
    ↓
• Envía notificaciones inmediatamente
• Sincroniza datos del servidor
• Actualiza en tiempo real

┌──────────────────────┐
│  SIN CONEXIÓN        │
└──────────────────────┘
    ↓
• Guarda localmente
• No envía notificaciones
• Marca como pending
• Reintenta al recuperar conexión

┌──────────────────────┐
│  RECONECTANDO        │
└──────────────────────┘
    ↓
• Sincroniza pendientes
• Actualiza BD
• Notifica al usuario
```

## Errores Comunes y Soluciones

| Error | Causa | Solución |
|-------|-------|----------|
| No llegan notificaciones | Token inválido | Verificar FCM token |
| App se cierra | Permiso faltante | Agregar POST_NOTIFICATIONS |
| BD no se crea | Permiso de escritura | Verificar permisos de almacenamiento |
| Reconexión lenta | Timeout largo | Aumentar timeout en ConnectivityService |

## Próximos Pasos Recomendados

1. **Backend Integration**
   - [ ] Crear endpoint para registrar FCM tokens
   - [ ] Crear endpoint para enviar notificaciones
   - [ ] Implementar validación de destinatarios

2. **Seguridad**
   - [ ] Agregar autenticación en API
   - [ ] Encriptar datos sensibles
   - [ ] Implementar rate limiting

3. **Optimización**
   - [ ] Implementar paginación en lista de notificaciones
   - [ ] Agregar filtros por tipo
   - [ ] Implementar búsqueda

4. **Testing**
   - [ ] Unit tests para servicios
   - [ ] Integration tests
   - [ ] Tests de conectividad

5. **Analytics**
   - [ ] Rastrear entrega de notificaciones
   - [ ] Rastrear interacción del usuario
   - [ ] Medir tasas de apertura

## Comandos Útiles

```bash
# Obtener información del dispositivo
flutter devices

# Ejecutar en modo release
flutter run --release

# Ver logs de Firebase
flutter logs

# Generar APK
flutter build apk --release

# Generar Bundle
flutter build appbundle --release

# Limpiar caché
flutter clean

# Obtener dependencias
flutter pub get
```

## Recursos Útiles

- [Firebase Messaging Documentation](https://firebase.flutter.dev/docs/messaging/overview/)
- [Flutter Notifications](https://docs.flutter.dev/development/ui/notifications)
- [SQLite en Flutter](https://docs.flutter.dev/development/data-and-backend/sqlite)
- [Connectivity Plus](https://pub.dev/packages/connectivity_plus)


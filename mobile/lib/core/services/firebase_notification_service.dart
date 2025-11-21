import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'database_service.dart';
import 'connectivity_service.dart';

class FirebaseNotificationService {
  static final FirebaseNotificationService _instance =
      FirebaseNotificationService._internal();
  final FirebaseMessaging _firebaseMessaging = FirebaseMessaging.instance;
  final FlutterLocalNotificationsPlugin _localNotifications =
      FlutterLocalNotificationsPlugin();
  final DatabaseService _databaseService = DatabaseService();
  final ConnectivityService _connectivityService = ConnectivityService();

  FirebaseNotificationService._internal();

  factory FirebaseNotificationService() {
    return _instance;
  }

  Future<void> initialize() async {
    try {
      // Inicializar Firebase
      await Firebase.initializeApp();

      // Solicitar permisos
      NotificationSettings settings = await _firebaseMessaging.requestPermission(
        alert: true,
        announcement: false,
        badge: true,
        carPlay: false,
        criticalAlert: false,
        provisional: false,
        sound: true,
      );

      print('Usuario autorizó notificaciones: ${settings.authorizationStatus}');

      // Inicializar notificaciones locales
      await _initializeLocalNotifications();

      // Configurar manejadores de mensajes
      _setupMessageHandlers();

      // Obtener token FCM
      String? token = await _firebaseMessaging.getToken();
      print('FCM Token: $token');

      // Guardar token en preferencias
      // TODO: Enviar este token al servidor para registrar el dispositivo
    } catch (e) {
      print('Error inicializando Firebase: $e');
    }
  }

  Future<void> _initializeLocalNotifications() async {
    const AndroidInitializationSettings androidInitializationSettings =
        AndroidInitializationSettings('@mipmap/ic_launcher');

    final DarwinInitializationSettings iOSInitializationSettings =
        DarwinInitializationSettings(
      onDidReceiveLocalNotification: (id, title, body, payload) {},
    );

    final InitializationSettings initializationSettings = InitializationSettings(
      android: androidInitializationSettings,
      iOS: iOSInitializationSettings,
    );

    await _localNotifications.initialize(
      initializationSettings,
      onDidReceiveNotificationResponse: (NotificationResponse response) {
        _handleNotificationTap(response.payload);
      },
    );
  }

  void _setupMessageHandlers() {
    // Mensaje cuando la app está en primer plano
    FirebaseMessaging.onMessage.listen((RemoteMessage message) {
      print('Mensaje recibido en primer plano: ${message.notification?.title}');
      _handleMessage(message);
      _showLocalNotification(message);
    });

    // Mensaje cuando el usuario toca la notificación
    FirebaseMessaging.onMessageOpenedApp.listen((RemoteMessage message) {
      print('Notificación abierta: ${message.notification?.title}');
      _handleMessage(message);
    });

    // Manejador de background (top-level)
    FirebaseMessaging.onBackgroundMessage(_firebaseBackgroundMessageHandler);
  }

  Future<void> _handleMessage(RemoteMessage message) async {
    try {
      final notification = {
        'notification_id': message.messageId ?? 'unknown',
        'title': message.notification?.title ?? 'Sin título',
        'body': message.notification?.body ?? 'Sin contenido',
        'sender': message.data['sender'] ?? 'Sistema',
        'sent_at': message.sentTime?.toIso8601String() ?? DateTime.now().toIso8601String(),
        'received_at': DateTime.now().toIso8601String(),
        'is_read': 0,
        'data': message.data.toString(),
      };

      // Guardar en base de datos
      await _databaseService.insertNotification(notification);

      // Si no hay internet, guardar como pendiente si es necesario
      bool hasInternet = await _connectivityService.hasInternetConnection();
      if (!hasInternet) {
        print('Sin internet, notificación guardada localmente');
      }
    } catch (e) {
      print('Error manejando mensaje: $e');
    }
  }

  Future<void> _showLocalNotification(RemoteMessage message) async {
    try {
      await _localNotifications.show(
        message.hashCode,
        message.notification?.title,
        message.notification?.body,
        const NotificationDetails(
          android: AndroidNotificationDetails(
            'colegio_app_channel',
            'Notificaciones de Colegio',
            channelDescription: 'Canal para notificaciones del colegio',
            importance: Importance.max,
            priority: Priority.high,
          ),
          iOS: DarwinNotificationDetails(
            presentAlert: true,
            presentBadge: true,
            presentSound: true,
          ),
        ),
        payload: message.data.toString(),
      );
    } catch (e) {
      print('Error mostrando notificación local: $e');
    }
  }

  void _handleNotificationTap(String? payload) {
    print('Notificación tocada con payload: $payload');
    // TODO: Navegar a la pantalla correspondiente según el payload
  }

  Future<void> sendNotification({
    required String title,
    required String body,
    required String recipientId,
    Map<String, String>? data,
  }) async {
    try {
      bool hasInternet = await _connectivityService.hasInternetConnection();

      if (hasInternet) {
        // Enviar a través de API del servidor
        // TODO: Implementar llamada a API
        print('Enviando notificación a través de API');

        // Por ahora, guardar en base de datos de pendientes
        await _databaseService.insertPendingNotification({
          'title': title,
          'body': body,
          'recipient': recipientId,
          'created_at': DateTime.now().toIso8601String(),
          'status': 'sent',
        });
      } else {
        // Guardar como pendiente si no hay internet
        await _databaseService.insertPendingNotification({
          'title': title,
          'body': body,
          'recipient': recipientId,
          'created_at': DateTime.now().toIso8601String(),
          'status': 'pending',
        });

        print('Sin internet, notificación guardada como pendiente');
      }
    } catch (e) {
      print('Error enviando notificación: $e');
    }
  }

  Future<List<Map<String, dynamic>>> getAllNotifications() async {
    return await _databaseService.getAllNotifications();
  }

  Future<List<Map<String, dynamic>>> getUnreadNotifications() async {
    return await _databaseService.getUnreadNotifications();
  }

  Future<void> markNotificationAsRead(int id) async {
    await _databaseService.markNotificationAsRead(id);
  }

  Future<void> deleteNotification(int id) async {
    await _databaseService.deleteNotification(id);
  }
}

@pragma('vm:entry-point')
Future<void> _firebaseBackgroundMessageHandler(RemoteMessage message) async {
  print('Manejando mensaje en background: ${message.notification?.title}');
  
  final databaseService = DatabaseService();
  final notification = {
    'notification_id': message.messageId ?? 'unknown',
    'title': message.notification?.title ?? 'Sin título',
    'body': message.notification?.body ?? 'Sin contenido',
    'sender': message.data['sender'] ?? 'Sistema',
    'sent_at': message.sentTime?.toIso8601String() ?? DateTime.now().toIso8601String(),
    'received_at': DateTime.now().toIso8601String(),
    'is_read': 0,
    'data': message.data.toString(),
  };

  await databaseService.insertNotification(notification);
}

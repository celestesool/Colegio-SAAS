import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:vibration/vibration.dart';
import 'notification_settings_service.dart';
import 'dart:convert';
import 'dart:async';
import 'dart:typed_data';

// Detectar si es web de forma segura
bool get kIsWeb {
  try {
    return identical(0, 0.0);
  } catch (e) {
    return false;
  }
}

class ConnectivityService {
  static final ConnectivityService _instance = ConnectivityService._internal();
  final Connectivity _connectivity = Connectivity();
  final NotificationSettingsService _settingsService = NotificationSettingsService();
  static const String _baseUrl = 'https://colegiologica.onrender.com/api';
  
  Timer? _pollingTimer;
  final StreamController<List<Map<String, dynamic>>> _notificationsController =
      StreamController<List<Map<String, dynamic>>>.broadcast();
  
  List<Map<String, dynamic>> _lastNotifications = [];
  
  // Local notifications
  late FlutterLocalNotificationsPlugin _flutterLocalNotificationsPlugin;

  ConnectivityService._internal() {
    _initializeLocalNotifications();
  }

  factory ConnectivityService() {
    return _instance;
  }

  void _initializeLocalNotifications() {
    // Solo inicializar en plataformas que lo soportan (no web)
    if (!kIsWeb) {
      _flutterLocalNotificationsPlugin = FlutterLocalNotificationsPlugin();
      
      const androidSettings =
          AndroidInitializationSettings('@mipmap/ic_launcher');
      const iosSettings = DarwinInitializationSettings();
      
      const initSettings = InitializationSettings(
        android: androidSettings,
        iOS: iosSettings,
      );
      
      _flutterLocalNotificationsPlugin.initialize(initSettings);
    }
  }

  Future<void> _showNotification(String titulo, String mensaje) async {
    // No mostrar notificaciones en web
    if (kIsWeb) return;
    
    try {
      // Verificar configuraciones del usuario
      final soundEnabled = await _settingsService.isSoundEnabled();
      final vibrationEnabled = await _settingsService.isVibrationEnabled();
      
      final androidDetails = AndroidNotificationDetails(
        'notificaciones_channel',
        'Notificaciones',
        channelDescription: 'Canal de notificaciones de la app',
        importance: Importance.max,  // Máxima importancia para que aparezca como banner
        priority: Priority.max,  // Máxima prioridad
        showWhen: true,
        sound: soundEnabled ? RawResourceAndroidNotificationSound('notification_sound') : null,
        playSound: soundEnabled,
        enableVibration: vibrationEnabled,  // Habilitar vibración explícitamente
        vibrationPattern: vibrationEnabled ? Int64List.fromList([0, 500, 200, 500]) : null,  // Patrón de vibración
        fullScreenIntent: true,  // Mostrar como emergente en pantalla completa
      );
      
      const iosDetails = DarwinNotificationDetails(
        presentAlert: true,
        presentBadge: true,
        presentSound: true,
      );
      
      final notificationDetails = NotificationDetails(
        android: androidDetails,
        iOS: iosDetails,
      );
      
      await _flutterLocalNotificationsPlugin.show(
        DateTime.now().millisecond,
        titulo,
        mensaje,
        notificationDetails,
      );
    } catch (e) {
      print('Error mostrando notificación: $e');
    }
  }

  Stream<bool> get internetConnectionStream {
    return _connectivity.onConnectivityChanged.map((result) {
      return result != ConnectivityResult.none;
    });
  }

  Future<bool> hasInternetConnection() async {
    final result = await _connectivity.checkConnectivity();
    return result != ConnectivityResult.none;
  }

  Future<ConnectivityResult> getConnectivityResult() async {
    return await _connectivity.checkConnectivity();
  }

  Stream<ConnectivityResult> get connectivityStream {
    return _connectivity.onConnectivityChanged;
  }

  // Stream de notificaciones nuevas
  Stream<List<Map<String, dynamic>>> get notificationsStream {
    return _notificationsController.stream;
  }

  // Iniciar polling automático
  void startPolling({Duration interval = const Duration(seconds: 30)}) {
    // Evitar múltiples timers
    if (_pollingTimer != null) return;

    _pollingTimer = Timer.periodic(interval, (_) async {
      try {
        final notifications = await getNotificationsFromBackend();
        
        // Detectar notificaciones nuevas
        _detectNewNotifications(notifications);
        
        _notificationsController.add(notifications);
      } catch (e) {
        print('Error en polling: $e');
      }
    });

    // Hacer la primera consulta inmediatamente
    _fetchNotificationsInitial();
  }

  void _detectNewNotifications(List<Map<String, dynamic>> notifications) {
    // Comparar con las últimas notificaciones
    final newNotifications = notifications
        .where((notif) => !_lastNotifications
            .any((last) => last['id'] == notif['id']))
        .toList();
    
    // Mostrar cada notificación nueva
    for (var notif in newNotifications) {
      _showNotification(
        notif['titulo'] ?? 'Nueva notificación',
        notif['mensaje'] ?? '',
      );
    }
    
    _lastNotifications = notifications;
  }

  // Detener polling
  void stopPolling() {
    _pollingTimer?.cancel();
    _pollingTimer = null;
  }

  void _fetchNotificationsInitial() async {
    try {
      final notifications = await getNotificationsFromBackend();
      _lastNotifications = notifications;
      _notificationsController.add(notifications);
    } catch (e) {
      print('Error en primera consulta: $e');
    }
  }

  // Obtener notificaciones del backend
  Future<List<Map<String, dynamic>>> getNotificationsFromBackend() async {
    try {
      final url = '$_baseUrl/notificacion/listar/';
      final response = await http.get(Uri.parse(url)).timeout(
        const Duration(seconds: 10),
      );
      
      if (response.statusCode == 200) {
        final List<dynamic> jsonData = jsonDecode(response.body);
        return jsonData.cast<Map<String, dynamic>>();
      } else {
        throw Exception('Error: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error de conexión: $e');
    }
  }

  // Crear notificación en el backend
  Future<Map<String, dynamic>> createNotificationInBackend({
    required String titulo,
    required String mensaje,
  }) async {
    try {
      final url = '$_baseUrl/notificacion/crear/';
      final body = jsonEncode({
        'titulo': titulo,
        'mensaje': mensaje,
      });

      final response = await http
          .post(
            Uri.parse(url),
            headers: {'Content-Type': 'application/json'},
            body: body,
          )
          .timeout(const Duration(seconds: 10));

      if (response.statusCode == 200 || response.statusCode == 201) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Error: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error: $e');
    }
  }

  void dispose() {
    stopPolling();
    _notificationsController.close();
  }
}

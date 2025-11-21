import 'package:shared_preferences/shared_preferences.dart';

class NotificationSettingsService {
  static final NotificationSettingsService _instance =
      NotificationSettingsService._internal();
  static const String _soundEnabledKey = 'notification_sound_enabled';
  static const String _vibrationEnabledKey = 'notification_vibration_enabled';

  NotificationSettingsService._internal();

  factory NotificationSettingsService() {
    return _instance;
  }

  // Obtener si el sonido está habilitado
  Future<bool> isSoundEnabled() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getBool(_soundEnabledKey) ?? true;
  }

  // Obtener si la vibración está habilitada
  Future<bool> isVibrationEnabled() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getBool(_vibrationEnabledKey) ?? true;
  }

  // Cambiar estado de sonido
  Future<void> setSoundEnabled(bool enabled) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_soundEnabledKey, enabled);
  }

  // Cambiar estado de vibración
  Future<void> setVibrationEnabled(bool enabled) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_vibrationEnabledKey, enabled);
  }
}

/// Configuración de la aplicación por entorno
class AppConfig {
  // URLs por entorno
  static const String _prodBaseUrl = "https://tu-dominio-backend.com/api/";
  static const String _devBaseUrl = "http://54.196.207.31:8000/api/";
  static const String _localBaseUrl = "http://10.0.2.2:8000/api/"; // Para emulador Android
  
  /// URL base según el entorno
  static String get baseUrl {
    const bool isProduction = bool.fromEnvironment('dart.vm.product');
    const String? customUrl = String.fromEnvironment('BACKEND_URL');
    
    if (customUrl != null && customUrl.isNotEmpty) {
      return customUrl;
    }
    
    return isProduction ? _prodBaseUrl : _devBaseUrl;
  }
  
  /// Configuración de timeouts
  static const int timeoutDuration = 30; // segundos
  static const int connectTimeout = 10; // segundos
  
  /// Configuración de la aplicación
  static const String appName = "Colegio App";
  static const String apiVersion = "v1";
  
  /// Configuración de debug
  static const bool enableLogging = true;
  
  /// Headers por defecto
  static Map<String, String> get defaultHeaders => {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "X-App-Version": apiVersion,
  };
  
  /// Configuración para desarrollo local
  static bool get isLocalDevelopment {
    return baseUrl.contains('10.0.2.2') || baseUrl.contains('localhost');
  }
  
  /// Configuración para producción
  static bool get isProduction {
    return baseUrl.startsWith('https://');
  }
}
import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../config/app_config.dart';

class ApiClient {
  static final http.Client _client = http.Client();
  
  /// Obtiene el token de acceso almacenado
  static Future<String?> _getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString("access_token");
  }

  /// Genera headers con autenticación opcional
  static Map<String, String> _getHeaders([String? token]) {
    final headers = Map<String, String>.from(AppConfig.defaultHeaders);
    
    if (token != null) {
      headers["Authorization"] = "Bearer $token";
    }
    
    return headers;
  }

  /// Realiza petición GET
  static Future<dynamic> get(String endpoint) async {
    try {
      final token = await _getToken();
      final uri = Uri.parse("${AppConfig.baseUrl}$endpoint");
      
      if (AppConfig.enableLogging) {
        print("🔗 GET: $uri");
      }
      
      final response = await _client
          .get(uri, headers: _getHeaders(token))
          .timeout(Duration(seconds: AppConfig.timeoutDuration));
      
      return _handleResponse(response, endpoint);
    } on SocketException {
      throw Exception("No hay conexión a internet. Verifica tu red.");
    } on HttpException {
      throw Exception("Error de conexión con el servidor.");
    } on FormatException {
      throw Exception("Error en el formato de respuesta del servidor.");
    } catch (e) {
      if (AppConfig.enableLogging) {
        print("❌ Error GET $endpoint: $e");
      }
      throw Exception("Error inesperado: $e");
    }
  }

  /// Realiza petición POST
  static Future<dynamic> post(String endpoint, Map<String, dynamic> body) async {
    try {
      final token = await _getToken();
      final uri = Uri.parse("${AppConfig.baseUrl}$endpoint");
      
      if (AppConfig.enableLogging) {
        print("🔗 POST: $uri");
        print("📦 Body: ${jsonEncode(body)}");
      }
      
      final response = await _client
          .post(
            uri,
            headers: _getHeaders(token),
            body: jsonEncode(body),
          )
          .timeout(Duration(seconds: AppConfig.timeoutDuration));
      
      return _handleResponse(response, endpoint);
    } on SocketException {
      throw Exception("No hay conexión a internet. Verifica tu red.");
    } on HttpException {
      throw Exception("Error de conexión con el servidor.");
    } on FormatException {
      throw Exception("Error en el formato de respuesta del servidor.");
    } catch (e) {
      if (AppConfig.enableLogging) {
        print("❌ Error POST $endpoint: $e");
      }
      throw Exception("Error inesperado: $e");
    }
  }

  /// Realiza petición PUT
  static Future<dynamic> put(String endpoint, Map<String, dynamic> body) async {
    try {
      final token = await _getToken();
      final uri = Uri.parse("${AppConfig.baseUrl}$endpoint");
      
      if (AppConfig.enableLogging) {
        print("🔗 PUT: $uri");
      }
      
      final response = await _client
          .put(
            uri,
            headers: _getHeaders(token),
            body: jsonEncode(body),
          )
          .timeout(Duration(seconds: AppConfig.timeoutDuration));
      
      return _handleResponse(response, endpoint);
    } catch (e) {
      if (AppConfig.enableLogging) {
        print("❌ Error PUT $endpoint: $e");
      }
      rethrow;
    }
  }

  /// Realiza petición DELETE
  static Future<dynamic> delete(String endpoint) async {
    try {
      final token = await _getToken();
      final uri = Uri.parse("${AppConfig.baseUrl}$endpoint");
      
      if (AppConfig.enableLogging) {
        print("🔗 DELETE: $uri");
      }
      
      final response = await _client
          .delete(uri, headers: _getHeaders(token))
          .timeout(Duration(seconds: AppConfig.timeoutDuration));
      
      return _handleResponse(response, endpoint);
    } catch (e) {
      if (AppConfig.enableLogging) {
        print("❌ Error DELETE $endpoint: $e");
      }
      rethrow;
    }
  }

  /// Maneja la respuesta HTTP
  static dynamic _handleResponse(http.Response response, String endpoint) {
    if (AppConfig.enableLogging) {
      print("📡 Response ${response.statusCode}: $endpoint");
    }
    
    switch (response.statusCode) {
      case 200:
      case 201:
        if (response.body.isEmpty) return {};
        return jsonDecode(response.body);
      case 204:
        return {}; // No content
      case 400:
        throw Exception("Datos inválidos. Verifica la información enviada.");
      case 401:
        throw Exception("Sesión expirada. Inicia sesión nuevamente.");
      case 403:
        throw Exception("No tienes permisos para realizar esta acción.");
      case 404:
        throw Exception("El recurso solicitado no existe.");
      case 422:
        throw Exception("Error de validación en los datos enviados.");
      case 500:
        throw Exception("Error interno del servidor. Intenta más tarde.");
      case 502:
      case 503:
        throw Exception("Servidor no disponible. Intenta más tarde.");
      default:
        final errorBody = response.body.isNotEmpty ? response.body : "Error desconocido";
        throw Exception("Error ${response.statusCode}: $errorBody");
    }
  }

  /// Verifica la conectividad con el servidor
  static Future<bool> checkConnectivity() async {
    try {
      final uri = Uri.parse("${AppConfig.baseUrl}health");
      final response = await _client
          .get(uri)
          .timeout(Duration(seconds: 5));
      
      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }

  /// Limpia recursos
  static void dispose() {
    _client.close();
  }
}

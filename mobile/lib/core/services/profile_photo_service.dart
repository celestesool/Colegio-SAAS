import 'package:image_picker/image_picker.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:io';
import 'package:path_provider/path_provider.dart';
import 'package:path/path.dart' as path;

// Detectar si es web
bool get kIsWeb {
  try {
    return identical(0, 0.0);
  } catch (e) {
    return false;
  }
}

class ProfilePhotoService {
  static final ProfilePhotoService _instance = ProfilePhotoService._internal();
  final ImagePicker _imagePicker = ImagePicker();
  static const String _photoPathKey = 'profile_photo_path';

  ProfilePhotoService._internal();

  factory ProfilePhotoService() {
    return _instance;
  }

  // Obtener foto de perfil guardada
  Future<File?> getProfilePhoto() async {
    if (kIsWeb) return null;
    
    try {
      final prefs = await SharedPreferences.getInstance();
      final photoPath = prefs.getString(_photoPathKey);
      
      if (photoPath != null && File(photoPath).existsSync()) {
        return File(photoPath);
      }
    } catch (e) {
      print('Error obteniendo foto: $e');
    }
    return null;
  }

  // Tomar foto con cámara
  Future<File?> takePhotoWithCamera() async {
    if (kIsWeb) {
      throw Exception('Esta función solo está disponible en la aplicación móvil');
    }
    
    try {
      final XFile? photo = await _imagePicker.pickImage(
        source: ImageSource.camera,
        imageQuality: 85,
      );

      if (photo != null) {
        return await _saveProfilePhoto(File(photo.path));
      }
    } catch (e) {
      print('Error tomando foto: $e');
      rethrow;
    }
    return null;
  }

  // Seleccionar foto de galería
  Future<File?> pickPhotoFromGallery() async {
    if (kIsWeb) {
      throw Exception('Esta función solo está disponible en la aplicación móvil');
    }
    
    try {
      final XFile? photo = await _imagePicker.pickImage(
        source: ImageSource.gallery,
        imageQuality: 85,
      );

      if (photo != null) {
        return await _saveProfilePhoto(File(photo.path));
      }
    } catch (e) {
      print('Error seleccionando foto: $e');
      rethrow;
    }
    return null;
  }

  // Guardar foto de perfil en almacenamiento local
  Future<File> _saveProfilePhoto(File imageFile) async {
    if (kIsWeb) {
      throw Exception('Almacenamiento no disponible en web');
    }
    
    try {
      // Obtener directorio de documentos
      final Directory appDocDir = await getApplicationDocumentsDirectory();
      final String appDocPath = appDocDir.path;
      
      // Crear carpeta de perfiles si no existe
      final Directory profileDir = Directory('$appDocPath/profiles');
      if (!profileDir.existsSync()) {
        profileDir.createSync(recursive: true);
      }

      // Guardar foto con nombre único
      final String fileName = 'profile_photo_${DateTime.now().millisecondsSinceEpoch}.jpg';
      final File savedImage = await imageFile.copy('${profileDir.path}/$fileName');

      // Guardar ruta en SharedPreferences
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_photoPathKey, savedImage.path);

      return savedImage;
    } catch (e) {
      print('Error guardando foto: $e');
      rethrow;
    }
  }

  // Eliminar foto de perfil
  Future<void> deleteProfilePhoto() async {
    if (kIsWeb) return;
    
    try {
      final prefs = await SharedPreferences.getInstance();
      final photoPath = prefs.getString(_photoPathKey);
      
      if (photoPath != null) {
        final file = File(photoPath);
        if (file.existsSync()) {
          await file.delete();
        }
        await prefs.remove(_photoPathKey);
      }
    } catch (e) {
      print('Error eliminando foto: $e');
    }
  }
}

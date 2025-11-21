# Configuración Avanzada para APK y Generación de Release

## 1. Configuración de Gradle para Release Optimization

### Archivo: `android/app/build.gradle.kts`

Asegúrate de que contenga:

```kotlin
android {
    compileSdk = 34
    
    defaultConfig {
        applicationId = "com.tu_empresa.colegio_app"
        minSdk = 21
        targetSdk = 34
        versionCode = 1
        versionName = "1.0.0"
        multiDexEnabled = true
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
            signingConfig = signingConfigs.getByName("release")
        }
        debug {
            isMinifyEnabled = false
        }
    }
}
```

## 2. Configuración de ProGuard

### Archivo: `android/app/proguard-rules.pro`

Crea este archivo con las siguientes reglas:

```proguard
# Firebase
-keep class com.google.firebase.** { *; }
-keep class com.google.android.gms.** { *; }
-dontwarn com.google.firebase.**
-dontwarn com.google.android.gms.**

# SQLite
-keep class android.database.sqlite.** { *; }

# HTTP Client
-keep class okhttp3.** { *; }
-keep class retrofit2.** { *; }
-dontwarn okhttp3.**
-dontwarn retrofit2.**

# Flutter
-keep class io.flutter.** { *; }
-dontwarn io.flutter.**

# Keep native methods
-keepclasseswithmembernames class * {
    native <methods>;
}

# Keep enums
-keepclassmembers enum * {
    public static **[] values();
    public static ** valueOf(java.lang.String);
}

# Keep parcelable classes
-keep class * implements android.os.Parcelable {
    public static final android.os.Parcelable$Creator *;
}
```

## 3. Archivo: `android/app/src/main/AndroidManifest.xml`

Asegúrate de que contenga todas estas configuraciones:

```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <!-- Permisos de Internet y Conectividad -->
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.CHANGE_NETWORK_STATE" />
    
    <!-- Permisos de Notificaciones (Android 13+) -->
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
    
    <!-- Permisos de Almacenamiento -->
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
    
    <!-- Permisos de Vibración -->
    <uses-permission android:name="android.permission.VIBRATE" />

    <application
        android:label="Colegio App"
        android:icon="@mipmap/ic_launcher"
        android:requestLegacyExternalStorage="true">

        <!-- Activity Principal -->
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:launchMode="singleTop"
            android:theme="@style/LaunchTheme"
            android:configChanges="orientation|keyboardHidden|keyboard|screenSize|smallestScreenSize|locale|layoutDirection|fontScale|screenLayout|density|uiMode">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <!-- Configuración de Notificaciones -->
        <service
            android:name="com.google.firebase.messaging.FirebaseMessagingService"
            android:exported="false">
            <intent-filter>
                <action android:name="com.google.firebase.MESSAGING_EVENT" />
            </intent-filter>
        </service>

        <!-- Meta-data para FCM -->
        <meta-data
            android:name="com.google.firebase.messaging.default_notification_channel_id"
            android:value="colegio_app_channel" />

        <!-- Channel para notificaciones -->
        <meta-data
            android:name="com.google.firebase.messaging.notification_channel"
            android:resource="@xml/notification_channels" />

    </application>

</manifest>
```

## 4. Archivo: `android/app/src/main/res/xml/notification_channels.xml`

Crea este archivo:

```xml
<?xml version="1.0" encoding="utf-8"?>
<notification-channels xmlns:android="http://schemas.android.com/apk/res/android">
    <notification-channel
        android:id="colegio_app_channel"
        android:name="Notificaciones de Colegio"
        android:description="Canal para notificaciones del colegio"
        android:importance="high"
        android:enableLights="true"
        android:lightColor="#2196F3"
        android:enableVibration="true"
        android:vibrationPattern="[0, 250, 250, 250]"
        android:soundPath="@android:raw/notification"
        android:defaultVibrationPattern="true" />
</notification-channels>
```

## 5. Archivo: `android/app/src/main/res/values/styles.xml`

Asegúrate de que contenga:

```xml
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <!-- LaunchTheme applied to AppBarActivity -->
    <style name="LaunchTheme" parent="@android:style/Theme.Light.NoTitleBar">
        <item name="android:windowActionBar">false</item>
        <item name="android:windowFullscreen">false</item>
        <item name="android:windowDrawsSystemBarBackgrounds">false</item>
    </style>
</resources>
```

## 6. Obtención de Certificado de Firma (Keystore)

### Generar un keystore nuevo:

```bash
keytool -genkey -v -keystore ~/colegio_app.jks ^
  -keyalg RSA -keysize 2048 -validity 10000 ^
  -alias colegio_app
```

### En macOS/Linux:

```bash
keytool -genkey -v -keystore ~/colegio_app.jks \
  -keyalg RSA -keysize 2048 -validity 10000 \
  -alias colegio_app
```

## 7. Configuración de Firma (build.gradle.kts)

```kotlin
android {
    signingConfigs {
        create("release") {
            storeFile = file(System.getenv("KEYSTORE_PATH") ?: "colegio_app.jks")
            storePassword = System.getenv("KEYSTORE_PASSWORD")
            keyAlias = System.getenv("KEY_ALIAS") ?: "colegio_app"
            keyPassword = System.getenv("KEY_PASSWORD")
        }
    }

    buildTypes {
        release {
            signingConfig = signingConfigs.getByName("release")
        }
    }
}
```

## 8. Generación del APK

### Para desarrollo:

```bash
flutter build apk --debug
```

### Para release (optimizado):

```bash
flutter build apk --release
```

### Para generar Bundle para Play Store:

```bash
flutter build appbundle --release
```

## 9. Variables de Entorno (Windows PowerShell)

```powershell
# Establecer variables antes de compilar
$env:KEYSTORE_PATH = "C:\ruta\al\colegio_app.jks"
$env:KEYSTORE_PASSWORD = "tu_password"
$env:KEY_ALIAS = "colegio_app"
$env:KEY_PASSWORD = "tu_password"

# Compilar release
flutter build apk --release
```

## 10. Optimizaciones para Mejor Rendimiento

### Archivo: `flutter_optimization.dart` (Recomendado)

Agregar a `lib/core/config/` si es necesario:

```dart
import 'dart:async';
import 'package:flutter/material.dart';

class FlutterOptimization {
  // Implementar caché de imágenes
  static void setupImageCache() {
    imageCache.maximumSize = 100;
    imageCache.maximumSizeBytes = 250 * 1024 * 1024; // 250MB
  }

  // Liberar memoria
  static void releaseMemory() {
    Future.delayed(Duration(seconds: 30), () {
      imageCache.clear();
      imageCache.clearLiveImages();
    });
  }
}
```

## 11. Pruebas Antes de Release

1. **Prueba en dispositivo físico**
   ```bash
   flutter run --release
   ```

2. **Verificar permisos**
   - Notificaciones
   - Internet
   - Almacenamiento

3. **Verificar conectividad**
   - Con WiFi
   - Con datos móviles
   - Sin conexión

4. **Pruebas de notificaciones**
   - Crear notificaciones
   - Recibir notificaciones
   - Sincronización offline

## 12. Verificación del APK

### Ver información del APK:

```bash
aapt dump badging app-release.apk
```

### Ver permisos:

```bash
aapt dump permissions app-release.apk
```

## 13. Publicación en Play Store

1. Crear cuenta de desarrollador en Google Play
2. Crear aplicación
3. Subir APK o Bundle
4. Configurar descripciones y screenshots
5. Publicar en beta/producción

## 14. Configuración de Android Studio (build.gradle)

Versiones recomendadas:

```gradle
classpath 'com.android.tools.build:gradle:8.0.0'
classpath 'com.google.gms:google-services:4.3.15'
classpath 'org.jetbrains.kotlin:kotlin-gradle-plugin:1.9.0'
```

## 15. Solución de Problemas comunes

### Error: "Could not find com.google.gms:google-services"
- Verificar que el classpath esté correcto en `build.gradle.kts`

### Error: "Notification permission not granted"
- Agregar `POST_NOTIFICATIONS` en AndroidManifest.xml

### El APK es muy grande
- Habilitar ProGuard/R8
- Usar `--split-per-abi`

### Firebase no se inicializa
- Verificar que `google-services.json` esté en la ubicación correcta
- Verificar que el plugin esté en `build.gradle.kts`

## Checklist Final

- [ ] `google-services.json` en `android/app/`
- [ ] Plugin de Google Services en `build.gradle.kts`
- [ ] Permisos en `AndroidManifest.xml`
- [ ] `notification_channels.xml` creado
- [ ] `proguard-rules.pro` configurado
- [ ] Keystore generado y configurado
- [ ] Pruebas en dispositivo real
- [ ] APK compilado sin errores
- [ ] Verificación de tamaño del APK
- [ ] Publicación en Play Store


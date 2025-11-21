plugins {
    id("com.android.application")
    id("kotlin-android")
    // El plugin de Flutter debe ir después de Android y Kotlin
    id("dev.flutter.flutter-gradle-plugin")
    // Google Services (Firebase)
    id("com.google.gms.google-services")
}
android {
    namespace = "com.example.colegio_app"
    compileSdk = 36
    ndkVersion = flutter.ndkVersion

    defaultConfig {
    applicationId = "colegio.flutter"
    minSdk = flutter.minSdkVersion
    targetSdk = flutter.targetSdkVersion
    versionCode = flutter.versionCode
    versionName = flutter.versionName
}

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
        isCoreLibraryDesugaringEnabled = true
    }

    kotlinOptions {
        jvmTarget = JavaVersion.VERSION_11.toString()
    }

    buildTypes {
        release {
            signingConfig = signingConfigs.getByName("debug")
        }
    }
}

dependencies {
    // Firebase BoM
    implementation(platform("com.google.firebase:firebase-bom:34.6.0"))

    // Kotlin estándar
    implementation("org.jetbrains.kotlin:kotlin-stdlib-jdk8:1.9.24")

    // Desugaring actualizado
    coreLibraryDesugaring("com.android.tools:desugar_jdk_libs:2.1.4")

    // Firebase Analytics
    implementation("com.google.firebase:firebase-analytics")
}

flutter {
    source = "../.."
}
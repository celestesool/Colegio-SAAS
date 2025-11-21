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

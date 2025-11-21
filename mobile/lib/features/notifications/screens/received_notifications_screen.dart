import 'package:flutter/material.dart';
// import '../../../core/services/firebase_notification_service.dart';
import '../../../core/services/connectivity_service.dart';

class ReceivedNotificationsScreen extends StatefulWidget {
  const ReceivedNotificationsScreen({super.key});

  @override
  State<ReceivedNotificationsScreen> createState() =>
      _ReceivedNotificationsScreenState();
}

class _ReceivedNotificationsScreenState
    extends State<ReceivedNotificationsScreen> {
  // final FirebaseNotificationService _notificationService =
  //     FirebaseNotificationService();
  final ConnectivityService _connectivityService = ConnectivityService();
  late Future<List<Map<String, dynamic>>> _notificationsFuture;

  @override
  void initState() {
    super.initState();
    _loadNotifications();
  }

  void _loadNotifications() {
    setState(() {
      _notificationsFuture = _connectivityService.getNotificationsFromBackend();
    });
  }

  @override
  void dispose() {
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Notificaciones Recibidas'),
      ),
      body: FutureBuilder<List<Map<String, dynamic>>>(
        future: _notificationsFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(
              child: CircularProgressIndicator(),
            );
          }

          if (snapshot.hasError) {
            return Center(
              child: Text('Error: ${snapshot.error}'),
            );
          }

          final notifications = snapshot.data ?? [];

          if (notifications.isEmpty) {
            return const Center(
              child: Text(
                'No hay notificaciones',
                style: TextStyle(fontSize: 16, color: Colors.grey),
              ),
            );
          }

          return RefreshIndicator(
            onRefresh: () async {
              _loadNotifications();
            },
            child: ListView.builder(
              itemCount: notifications.length,
              itemBuilder: (context, index) {
                final notification = notifications[index];

                return Card(
                  margin: const EdgeInsets.symmetric(
                    horizontal: 8.0,
                    vertical: 4.0,
                  ),
                  child: ListTile(
                    leading: const Icon(
                      Icons.notifications_active,
                      color: Colors.blue,
                    ),
                    title: Text(
                      notification['titulo'] ?? 'Sin título',
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                    subtitle: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const SizedBox(height: 4),
                        Text(
                          notification['mensaje'] ?? 'Sin contenido',
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                        ),
                        const SizedBox(height: 4),
                        Row(
                          children: [
                            Text(
                              '${notification['fechaCreada'] ?? ''} ${notification['horaCreada'] ?? ''}',
                              style: const TextStyle(
                                fontSize: 12,
                                color: Colors.grey,
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
          );
        },
      ),
    );
  }

  void _markAsRead(int id) {}

  void _deleteNotification(int id) {}

  String _formatDate(String? dateString) {
    if (dateString == null) return 'Desconocido';

    try {
      final date = DateTime.parse(dateString);
      final now = DateTime.now();
      final difference = now.difference(date);

      if (difference.inSeconds < 60) {
        return 'Ahora';
      } else if (difference.inMinutes < 60) {
        return 'hace ${difference.inMinutes} min';
      } else if (difference.inHours < 24) {
        return 'hace ${difference.inHours} h';
      } else {
        return '${date.day}/${date.month}/${date.year}';
      }
    } catch (e) {
      return 'Desconocido';
    }
  }
}

import 'package:flutter/material.dart';
import '../../../core/services/notification_settings_service.dart';

class NotificationSettingsScreen extends StatefulWidget {
  const NotificationSettingsScreen({super.key});

  @override
  State<NotificationSettingsScreen> createState() =>
      _NotificationSettingsScreenState();
}

class _NotificationSettingsScreenState extends State<NotificationSettingsScreen> {
  final NotificationSettingsService _settingsService =
      NotificationSettingsService();
  bool _soundEnabled = true;
  bool _vibrationEnabled = true;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  void _loadSettings() async {
    final sound = await _settingsService.isSoundEnabled();
    final vibration = await _settingsService.isVibrationEnabled();

    setState(() {
      _soundEnabled = sound;
      _vibrationEnabled = vibration;
      _isLoading = false;
    });
  }

  void _toggleSound(bool value) async {
    setState(() {
      _soundEnabled = value;
    });
    await _settingsService.setSoundEnabled(value);
  }

  void _toggleVibration(bool value) async {
    setState(() {
      _vibrationEnabled = value;
    });
    await _settingsService.setVibrationEnabled(value);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Configuración de Notificaciones'),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : ListView(
              children: [
                const SizedBox(height: 16),
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Sonido y Vibración',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 16),
                      Container(
                        decoration: BoxDecoration(
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: Colors.grey.shade300),
                        ),
                        child: ListTile(
                          leading: const Icon(Icons.volume_up),
                          title: const Text('Sonido'),
                          subtitle:
                              Text(_soundEnabled ? 'Activado' : 'Desactivado'),
                          trailing: Switch(
                            value: _soundEnabled,
                            onChanged: _toggleSound,
                          ),
                        ),
                      ),
                      const SizedBox(height: 12),
                      Container(
                        decoration: BoxDecoration(
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: Colors.grey.shade300),
                        ),
                        child: ListTile(
                          leading: const Icon(Icons.vibration),
                          title: const Text('Vibración'),
                          subtitle: Text(
                              _vibrationEnabled ? 'Activada' : 'Desactivada'),
                          trailing: Switch(
                            value: _vibrationEnabled,
                            onChanged: _toggleVibration,
                          ),
                        ),
                      ),
                      const SizedBox(height: 24),
                      Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: Colors.blue.shade50,
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: Colors.blue),
                        ),
                        child: const Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Información:',
                              style: TextStyle(
                                fontWeight: FontWeight.bold,
                                color: Colors.blue,
                              ),
                            ),
                            SizedBox(height: 8),
                            Text(
                              '• Desactiva el sonido si prefieres solo vibración',
                              style: TextStyle(fontSize: 12),
                            ),
                            SizedBox(height: 4),
                            Text(
                              '• Desactiva la vibración para recibir solo notificaciones silenciosas',
                              style: TextStyle(fontSize: 12),
                            ),
                            SizedBox(height: 4),
                            Text(
                              '• Los cambios se guardan automáticamente',
                              style: TextStyle(fontSize: 12),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
    );
  }
}

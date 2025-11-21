import 'package:flutter/material.dart';
import 'dart:io';
import '../services/profile_photo_service.dart';

// Detectar si es web
bool get kIsWeb {
  try {
    return identical(0, 0.0);
  } catch (e) {
    return false;
  }
}

class AppDrawer extends StatefulWidget {
  final List<DrawerItem> items;
  final String? userTitle;

  const AppDrawer({
    super.key,
    required this.items,
    this.userTitle,
  });

  @override
  State<AppDrawer> createState() => _AppDrawerState();
}

class _AppDrawerState extends State<AppDrawer> {
  final ProfilePhotoService _photoService = ProfilePhotoService();
  File? _profilePhoto;
  bool _profileExpanded = false;

  @override
  void initState() {
    super.initState();
    if (!kIsWeb) {
      _loadProfilePhoto();
    }
  }

  void _loadProfilePhoto() async {
    final photo = await _photoService.getProfilePhoto();
    setState(() {
      _profilePhoto = photo;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Drawer(
      child: Column(
        children: [
          // Header del Drawer con foto de perfil
          DrawerHeader(
            decoration: BoxDecoration(
              color: Theme.of(context).primaryColor,
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Row(
                  children: [
                    // Avatar circular con foto
                    Container(
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        border: Border.all(
                          color: Colors.white,
                          width: 2,
                        ),
                      ),
                      child: CircleAvatar(
                        radius: 32,
                        backgroundColor: Colors.white,
                        backgroundImage: _profilePhoto != null
                            ? FileImage(_profilePhoto!)
                            : null,
                        child: _profilePhoto == null
                            ? const Icon(
                                Icons.person,
                                size: 32,
                                color: Colors.blue,
                              )
                            : null,
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          if (widget.userTitle != null)
                            Text(
                              widget.userTitle!,
                              style: const TextStyle(
                                color: Colors.white,
                                fontSize: 14,
                                fontWeight: FontWeight.w500,
                              ),
                              overflow: TextOverflow.ellipsis,
                            ),
                          const SizedBox(height: 4),
                          const Text(
                            'Mi Perfil',
                            style: TextStyle(
                              color: Colors.white70,
                              fontSize: 12,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),

          // Menú principal con perfil expandible
          Expanded(
            child: ListView(
              children: [
                // Mi Perfil expandible
                ExpansionTile(
                  leading: const Icon(Icons.person),
                  title: const Text('Mi Perfil'),
                  onExpansionChanged: (expanded) {
                    setState(() {
                      _profileExpanded = expanded;
                    });
                  },
                  children: [
                    Padding(
                      padding: const EdgeInsets.only(left: 16.0),
                      child: Column(
                        children: [
                          ListTile(
                            leading: const Icon(Icons.volume_up),
                            title: const Text('Sonido/Vibración'),
                            onTap: () {
                              Navigator.pop(context);
                              Navigator.pushNamed(
                                context,
                                "/notificationSettings",
                              );
                            },
                          ),
                          ListTile(
                            leading: const Icon(Icons.camera_alt),
                            title: const Text('Foto de Perfil'),
                            onTap: () {
                              Navigator.pop(context);
                              Navigator.pushNamed(
                                context,
                                "/editProfilePhoto",
                              );
                            },
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
                const Divider(),
                // Notificaciones
                ListTile(
                  leading: const Icon(Icons.notifications),
                  title: const Text('Notificaciones Recibidas'),
                  onTap: () {
                    Navigator.pop(context);
                    Navigator.pushNamed(context, "/receivedNotifications");
                  },
                ),
                ListTile(
                  leading: const Icon(Icons.send),
                  title: const Text('Crear Notificación'),
                  onTap: () {
                    Navigator.pop(context);
                    Navigator.pushNamed(context, "/createNotification");
                  },
                ),
                // Items del menú original
                const Divider(),
                ...widget.items.map((item) {
                  return ListTile(
                    leading: Icon(item.icon),
                    title: Text(item.label),
                    onTap: item.onTap != null
                        ? () {
                            Navigator.pop(context);
                            item.onTap!();
                          }
                        : null,
                    enabled: item.onTap != null,
                  );
                }).toList(),
              ],
            ),
          ),

          // Logout button en la parte inferior
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: () {
                  Navigator.pop(context);
                  Navigator.pushReplacementNamed(context, "/signIn");
                },
                icon: const Icon(Icons.logout),
                label: const Text("Cerrar Sesión"),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.red,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 12),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class DrawerItem {
  final IconData icon;
  final String label;
  final VoidCallback? onTap;

  DrawerItem({
    required this.icon,
    required this.label,
    this.onTap,
  });
}

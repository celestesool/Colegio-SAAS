import 'package:flutter/material.dart';
import 'routes/app_routes.dart';
import 'core/services/connectivity_service.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Iniciar polling de notificaciones
  ConnectivityService().startPolling(
    interval: const Duration(seconds: 30),
  );
  
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: "Jesvaw EduSoft",
      theme: ThemeData(
        primarySwatch: Colors.blue,
        visualDensity: VisualDensity.adaptivePlatformDensity,
      ),
      initialRoute: AppRoutes.signIn,
      routes: AppRoutes.routes,
    );
  }
}

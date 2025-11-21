import 'package:flutter/material.dart';

// Auth
import '../features/auth/screens/sign_in_page.dart';

// Student
import '../features/student/screens/student_dashboard.dart';
import '../features/student/screens/notas_screen.dart';
import '../features/student/screens/asistencia_screen.dart';
import '../features/student/screens/agenda_screen.dart';

// Parent
import '../features/parent/screens/parent_dashboard.dart';
import '../features/parent/screens/parent_notas_screen.dart';
import '../features/parent/screens/parent_asistencia_screen.dart';
import '../features/parent/screens/select_child_screen.dart'; 
import '../features/parent/screens/parent_agenda_screen.dart';

// Announcements
import '../features/announcements/screens/announcements_screen.dart';

// Teacher
import '../features/teacher/screens/teacher_dashboard.dart';

// Horario
import '../features/horario/screens/horario_screen.dart';

// Notifications
import '../features/notifications/screens/received_notifications_screen.dart';
import '../features/notifications/screens/create_notification_screen.dart';

// Profile
import '../features/profile/screens/profile_photo_screen.dart';
import '../features/profile/screens/edit_profile_photo_screen.dart';
import '../features/profile/screens/notification_settings_screen.dart';



class AppRoutes {
  static const String signIn = "/signIn";

  // Student
  static const String studentDashboard = "/studentDashboard";
  static const String notas = "/notas";
  static const String asistencia = "/asistencia";
  static const String agenda = "/agenda";

  // Parent
  static const String parentDashboard = "/parentDashboard";
  static const String parentNotas = "/parentNotas";
  static const String parentAsistencia = "/parentAsistencia";
  static const String selectChild = "/selectChild"; 
  static const String parentAgenda = "/parentAgenda";

  // Teacher
  static const String teacherDashboard = "/teacherDashboard";
  
  // Shared
  static const String announcements = "/announcements";
  static const String horario = "/horario";
  
  // Notifications
  static const String receivedNotifications = "/receivedNotifications";
  static const String createNotification = "/createNotification";
  
  // Profile
  static const String profilePhoto = "/profilePhoto";
  static const String editProfilePhoto = "/editProfilePhoto";
  static const String notificationSettings = "/notificationSettings";

  static Map<String, WidgetBuilder> routes = {
    // Auth
    signIn: (context) => const SignInPage(),

    // Student
    studentDashboard: (context) => const StudentDashboard(),
    notas: (context) => const NotasEstudianteScreen(studentId: 1),
    asistencia: (context) => const AsistenciaEstudianteScreen(studentId: 1),
    agenda: (context) => const AgendaEstudianteScreen(studentId: 1),

    // Parent
    selectChild: (context) => const SelectChildScreen(), 
    parentDashboard: (context) => const ParentDashboard(),
    parentNotas: (context) => const ParentNotasScreen(),
    parentAsistencia: (context) => const ParentAsistenciaScreen(),
    parentAgenda: (context) => const ParentAgendaScreen(),

    // Teacher
    teacherDashboard: (context) => const TeacherDashboard(),
    
    // Shared
    announcements: (context) => const AnnouncementsScreen(),
    horario: (context) => const HorarioScreen(),

    // Notifications
    receivedNotifications: (context) => const ReceivedNotificationsScreen(),
    createNotification: (context) => const CreateNotificationScreen(),
    
    // Profile
    profilePhoto: (context) => const ProfilePhotoScreen(),
    editProfilePhoto: (context) => const EditProfilePhotoScreen(),
    notificationSettings: (context) => const NotificationSettingsScreen(),
  };
}

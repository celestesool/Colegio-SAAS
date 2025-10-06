class ApiEndpoints {
 // Auth
 static const String login = "auth/token/";
 static const String refresh = "auth/token/refresh/";

 // Estudiantes - endpoints que SÍ existen en el backend
 static const String students = "students";
 static const String persons = "persons";
 static const String enrollments = "enrollments";
 
 // Gestión Académica - endpoints disponibles
 static const String levels = "levels";
 static const String periods = "periods";
 static const String grades = "grades";
 static const String sections = "sections";
 static const String subjects = "subjects";

 // TODO: Estos endpoints NO EXISTEN en el backend actual
 // Necesitan ser implementados en Django antes de usarlos
 static String studentGrades(int id) => "students/$id/grades/";
 static String studentAttendance(int id) => "students/$id/attendance/";
 static String studentTasks(int id) => "students/$id/tasks/";

 // Padres - endpoints NO implementados en backend
 static String parentChildren(int id) => "parents/$id/children/";
 static String parentGrades(int id) => "parents/$id/grades/";
 static String parentAttendance(int id) => "parents/$id/attendance/";

 // Anuncios - módulo NO implementado en backend
 static const String announcements = "announcements/";
 static const String lastAnnouncement = "announcements/last/";
}

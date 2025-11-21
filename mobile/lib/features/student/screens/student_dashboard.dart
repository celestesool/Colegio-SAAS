import 'package:flutter/material.dart';
import 'package:table_calendar/table_calendar.dart';
import '../../../routes/app_routes.dart';
import '../../../core/widgets/app_drawer.dart';

class StudentDashboard extends StatefulWidget {
  const StudentDashboard({super.key});

  @override
  State<StudentDashboard> createState() => _StudentDashboardState();
}

class _StudentDashboardState extends State<StudentDashboard> {
  DateTime _focusedDay = DateTime.now();
  DateTime? _selectedDay;

  final Map<DateTime, List<String>> _events = {
    DateTime.utc(2025, 9, 2): ["Marcado de notas"],
    DateTime.utc(2025, 9, 4): ["Examen de Matemáticas"],
    DateTime.utc(2025, 9, 5): ["Entrega de tarea"],
    DateTime.utc(2025, 9, 11): ["Exposición de Lenguaje"],
    DateTime.utc(2025, 9, 18): ["Entrega Proyecto", "Reunión padres"],
  };

  List<String> _getEventsForDay(DateTime day) {
    return _events[DateTime.utc(day.year, day.month, day.day)] ?? [];
  }

  @override
  Widget build(BuildContext context) {
    final drawerItems = [
      DrawerItem(
        icon: Icons.school,
        label: "Notas",
        onTap: () => Navigator.pushNamed(context, AppRoutes.notas),
      ),
      DrawerItem(
        icon: Icons.check_circle_outline,
        label: "Asistencia",
        onTap: () => Navigator.pushNamed(context, AppRoutes.asistencia),
      ),
      DrawerItem(
        icon: Icons.event_note,
        label: "Agenda",
        onTap: () => Navigator.pushNamed(context, AppRoutes.agenda),
      ),
      DrawerItem(
        icon: Icons.campaign_outlined,
        label: "Anuncios",
        onTap: () => Navigator.pushNamed(context, AppRoutes.announcements),
      ),
      DrawerItem(
        icon: Icons.schedule,
        label: "Horario",
        onTap: () => Navigator.pushNamed(context, AppRoutes.horario),
      ),
    ];

    return Scaffold(
      appBar: AppBar(
        title: const Text("Dashboard Estudiante"),
      ),
      drawer: AppDrawer(
        items: drawerItems,
        userTitle: "Opciones",
      ),
      body: Column(
        children: [
          //  Calendario principal
          TableCalendar(
            firstDay: DateTime.utc(DateTime.now().year, 1, 1),
            lastDay: DateTime.utc(DateTime.now().year, 12, 31),
            focusedDay: _focusedDay,
            selectedDayPredicate: (day) => isSameDay(_selectedDay, day),
            eventLoader: _getEventsForDay,
            startingDayOfWeek: StartingDayOfWeek.monday,
            calendarFormat: CalendarFormat.month,
            headerStyle:  HeaderStyle(
              formatButtonVisible: false,
              titleCentered: true,
              leftChevronIcon: Icon(Icons.chevron_left),
              rightChevronIcon: Icon(Icons.chevron_right),
            ),
            onDaySelected: (selectedDay, focusedDay) {
              setState(() {
                _selectedDay = selectedDay;
                _focusedDay = focusedDay;
              });
            },
            onPageChanged: (focusedDay) {
              setState(() {
                _focusedDay = focusedDay;
              });
            },
          ),
          const SizedBox(height: 8),
          //  Eventos del día seleccionado
          Expanded(
            child: ListView(
              children: _getEventsForDay(_selectedDay ?? _focusedDay)
                  .map((event) => ListTile(
                        leading: const Icon(Icons.event),
                        title: Text(event),
                      ))
                  .toList(),
            ),
          ),
        ],
      ),
    );
  }
}

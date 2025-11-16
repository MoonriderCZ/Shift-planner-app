import 'package:flutter/material.dart';
import 'package:shift_planner_flutter/models/shift_logic.dart';
import 'package:shift_planner_flutter/services/settings_service.dart';

// Import obrazovky ScheduleScreen — uprav cestu podle struktury projektu
import 'package:shift_planner_flutter/screens/schedule_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const ShiftPlannerApp());
}

class ShiftPlannerApp extends StatelessWidget {
  const ShiftPlannerApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Shift Planner',
      theme: ThemeData(primarySwatch: Colors.indigo),
      home: const ScheduleScreen(),
    );
  }
}

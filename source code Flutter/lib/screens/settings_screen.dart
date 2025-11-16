import 'package:flutter/material.dart';
import 'package:shift_planner_flutter/models/shift_logic.dart';

class ScheduleScreen extends StatefulWidget {
  final Map<String, dynamic> settings;
  const ScheduleScreen(this.settings, {super.key});

  @override
  State<ScheduleScreen> createState() => _ScheduleScreenState();
}

class _ScheduleScreenState extends State<ScheduleScreen> {
  List<Map<String, String>>? _schedule;
  late String _targetMonthYear;

  @override
  void initState() {
    super.initState();
    _loadSchedule();
  }

  Future<void> _loadSchedule() async {
    final settings = widget.settings;
    final year = settings['year'] ?? 2025;
    final month = settings['month'] ?? 12;
    final result = generateSchedule(settings, year, month);

    setState(() {
      _schedule = result;
      _targetMonthYear = '$year/$month';
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Směny – Plán')),
      body: _schedule == null
          ? const Center(child: CircularProgressIndicator())
          : ListView.builder(
              itemCount: _schedule!.length,
              itemBuilder: (context, index) {
                final day = _schedule![index];
                final date = day['date'] ?? '';
                return Padding(
                  padding:
                      const EdgeInsets.symmetric(vertical: 4, horizontal: 8),
                  child: Card(
                    child: Padding(
                      padding: const EdgeInsets.all(8),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Expanded(
                              child: Text(_extractDay(date),
                                  textAlign: TextAlign.center)),
                          Expanded(
                              child: Text(_extractMonth(date),
                                  textAlign: TextAlign.center)),
                          Expanded(
                              child: Text(_extractYear(date),
                                  textAlign: TextAlign.center)),
                          Expanded(
                              child: Text(_targetMonthYear,
                                  textAlign: TextAlign.center)),
                        ],
                      ),
                    ),
                  ),
                );
              },
            ),
    );
  }

  String _extractDay(String date) => DateTime.parse(date).day.toString();
  String _extractMonth(String date) => DateTime.parse(date).month.toString();
  String _extractYear(String date) => DateTime.parse(date).year.toString();
}

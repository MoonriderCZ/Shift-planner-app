import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';

// #1 Import knihoven a definice cesty k nastavení
const String settingsFile = 'settings.json';

// #2 Práce s nastavením

// #2.1 Načtení nastavení ze souboru nebo vytvoření výchozího
Future<Map<String, dynamic>> loadSettings() async {
  final file = File(settingsFile);
  if (await file.exists()) {
    final content = await file.readAsString();
    return jsonDecode(content);
  } else {
    final defaultSettings = {"start_day": 1, "start_shift": "N"};
    await file.writeAsString(jsonEncode(defaultSettings));
    return defaultSettings;
  }
}

// #2.2 Uložení nastavení do souboru
Future<void> saveSettings(Map<String, dynamic> settings) async {
  final file = File(settingsFile);
  await file.writeAsString(jsonEncode(settings));
}

// #3 Výpočet opěrného data (anchor), od kterého se plán odvíjí
DateTime resolveAnchorDate(Map<String, dynamic> settings, int year, int month) {
  final startDateStr = settings['start_date'];
  if (startDateStr != null) {
    try {
      return DateTime.parse(startDateStr);
    } catch (_) {}
  }

  int startDay = int.tryParse(settings['start_day'].toString()) ?? 1;
  int y = year;
  int m = month;

  for (int i = 0; i < 12; i++) {
    int lastDay = DateUtils.getDaysInMonth(y, m);
    int d = startDay.clamp(1, lastDay);
    try {
      return DateTime(y, m, d);
    } catch (_) {}
    m -= 1;
    if (m < 1) {
      m = 12;
      y -= 1;
    }
  }

  return DateTime(year, month, 1);
}

// #4 Generování rozvrhu směn pro daný měsíc
List<Map<String, String>> generateSchedule(
    Map<String, dynamic> settings, int year, int month) {
  String startShift = (settings['start_shift'] ?? 'N').toUpperCase();

  List<bool> longWeek = [true, true, false, false, true, true, true];
  List<bool> shortWeek = [false, false, true, true, false, false, false];

  DateTime anchor = resolveAnchorDate(settings, year, month);
  int anchorWeekday = anchor.weekday - 1; // 0 = pondělí, 6 = neděle
  DateTime anchorMonday = anchor.subtract(Duration(days: anchorWeekday));
  String anchorWeekType = longWeek[anchorWeekday] ? 'long' : 'short';
  String currentShift = startShift;

  int daysInMonth = DateUtils.getDaysInMonth(year, month);
  List<Map<String, String>> output = [];

  String? previousLabel;

  for (int d = 1; d <= daysInMonth; d++) {
    DateTime current = DateTime(year, month, d);
    int curWeekday = current.weekday - 1; // 0 = pondělí, 6 = neděle
    DateTime curMonday = current.subtract(Duration(days: curWeekday));

    int weekDiff = curMonday.difference(anchorMonday).inDays ~/ 7;
    String curWeekType = (weekDiff % 2 == 0)
        ? anchorWeekType
        : (anchorWeekType == 'long' ? 'short' : 'long');

    List<bool> pattern = (curWeekType == 'long') ? longWeek : shortWeek;
    bool isWorkday = pattern[curWeekday];

    if (isWorkday && previousLabel == 'Volno') {
      currentShift = (currentShift == 'D') ? 'N' : 'D';
    }

    String label = isWorkday
        ? (currentShift == 'D' ? 'Ranní směna' : 'Noční směna')
        : 'Volno';

    output.add({
      'date':
          '${current.year.toString().padLeft(4, '0')}-${current.month.toString().padLeft(2, '0')}-${current.day.toString().padLeft(2, '0')}',
      'label': label
    });

    previousLabel = label;
  }

  return output;
}

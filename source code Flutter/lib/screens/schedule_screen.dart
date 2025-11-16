// 📦 Importy
import 'package:flutter/material.dart';
import 'package:shift_planner_flutter/models/shift_logic.dart';

// 🧩 Hlavní widget obrazovky
class ScheduleScreen extends StatefulWidget {
  const ScheduleScreen({super.key});

  @override
  State<ScheduleScreen> createState() => _ScheduleScreenState();
}

// 🔧 Stavová třída
class _ScheduleScreenState extends State<ScheduleScreen> {
  // 📅 Řídicí prvky pro vstup
  final _yearController = TextEditingController(text: '2025');
  final _monthController = TextEditingController(text: '12');
  final _dayController = TextEditingController(text: '1');

  String _startShift = 'N'; // 🌙 Výchozí směna
  List<Map<String, String>>? _schedule; // 📋 Výsledný plán
  late String _targetMonthYear; // 🏷️ Zobrazení měsíce/roku

  // 🧮 Generování rozvrhu
  void _generateSchedule() {
    final year = int.tryParse(_yearController.text) ?? 2025;
    final month = int.tryParse(_monthController.text) ?? 12;
    final startDay = int.tryParse(_dayController.text) ?? 1;

    final settings = {
      'year': year,
      'month': month,
      'start_day': startDay,
      'start_shift': _startShift,
    };

    final result = generateSchedule(settings, year, month);

    setState(() {
      _schedule = result;
      _targetMonthYear = '$year/$month';
    });
  }

  // 🖼️ UI
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      // ⬅️ 1. Začátek Scaffold
      appBar: AppBar(title: const Text('Směny – Plán')),

      body: Padding(
        // ⬅️ 2. Padding kolem celého obsahu
        padding: const EdgeInsets.all(12),
        child: Column(
          // ⬅️ 3. Sloupec s ovládacími prvky a seznamem
          children: [
            // 🔢 Vstupní řádek
            Row(children: [
              Expanded(
                child: TextField(
                  controller: _yearController,
                  decoration: const InputDecoration(labelText: 'Rok'),
                ),
              ),
              Expanded(
                child: TextField(
                  controller: _monthController,
                  decoration: const InputDecoration(labelText: 'Měsíc'),
                ),
              ),
              Expanded(
                child: TextField(
                  controller: _dayController,
                  decoration: const InputDecoration(labelText: 'Kotva – den'),
                ),
              ),
              Expanded(
                child: DropdownButton<String>(
                  value: _startShift,
                  items: ['D', 'N']
                      .map((s) => DropdownMenuItem(value: s, child: Text(s)))
                      .toList(),
                  onChanged: (val) => setState(() => _startShift = val!),
                ),
              ),
              ElevatedButton(
                onPressed: _generateSchedule,
                child: const Text('Vygenerovat'),
              ),
            ]), // ⬅️ konec Row

            const SizedBox(height: 12),

            if (_schedule != null)
              Text(
                'Plán směn pro: $_targetMonthYear',
                style:
                    const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),

            const SizedBox(height: 8),

            Expanded(
              // ⬅️ 4. Roztažitelný blok pro seznam
              child: _schedule == null
                  ? const Center(
                      child: Text('Zadej parametry a klikni na Vygenerovat'),
                    )
                  : ListView.builder(
                      // ⬅️ 5. Seznam směn
                      itemCount: _schedule!.length,
                      itemBuilder: (context, index) {
                        final day = _schedule![index];
                        final date = day['date'] ?? '';
                        final label = day['label'] ?? '';
                        final isShift = label != 'Volno';

                        return Card(
                          // ⬅️ 6. Rámeček pro každý den
                          color: isShift ? Colors.green[100] : null,
                          child: ListTile(
                            title: Text(
                              date,
                              style: TextStyle(
                                fontWeight: isShift
                                    ? FontWeight.bold
                                    : FontWeight.normal,
                              ),
                            ),
                            subtitle: Text(
                              label,
                              style: TextStyle(
                                color:
                                    isShift ? Colors.green[900] : Colors.black,
                              ),
                            ),
                          ),
                        ); // ⬅️ konec Card
                      }, // ⬅️ konec itemBuilder
                    ), // ⬅️ konec ListView.builder
            ), // ⬅️ konec Expanded
          ],
        ), // ⬅️ konec Column
      ), // ⬅️ konec Padding
    ); // ⬅️ konec Scaffold
  } // ⬅️ konec build()
} // ⬅️ konec _ScheduleScreenState

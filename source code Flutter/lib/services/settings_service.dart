class SettingsService {
  Map<String, dynamic> _settings = {
    "start_date": "2025-12-04",
    "start_shift": "N"
  };

  Future<void> load() async {
    // V budoucnu může načítat z SharedPreferences
  }

  Future<void> save() async {
    // V budoucnu může ukládat do SharedPreferences
  }

  String getString(String key) => _settings[key]?.toString() ?? '';
  Map<String, dynamic> get all => _settings;

  void set(String key, dynamic value) {
    _settings[key] = value;
  }
}

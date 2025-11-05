# 1. Import knihoven a definice cesty k nastavení
import json, os
from datetime import datetime, timedelta
import calendar

SETTINGS_FILE = 'settings.json'

# 2. Práce s nastavením

# 2.1 Načtení nastavení ze souboru nebo vytvoření výchozího
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    else:
        default = {
            "start_day": 1,
            "start_shift": "N"
        }
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(default, f)
        return default

# 2.2 Uložení nastavení do souboru
def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f)

# 3. Výpočet opěrného data (anchor), od kterého se plán odvíjí
def _resolve_anchor_date(settings, query_year, query_month):
    # 3.1 Pokud existuje přesné start_date, použijeme jej
    start_date_str = settings.get('start_date')
    if start_date_str:
        try:
            return datetime.strptime(start_date_str, '%Y-%m-%d')
        except Exception:
            pass

    # 3.2 Pokud máme pouze start_day, najdeme nejbližší odpovídající datum
    start_day = int(settings.get('start_day', 1))
    y = query_year
    m = query_month
    for _ in range(12):
        last = calendar.monthrange(y, m)[1]
        d = min(start_day, last)
        try:
            candidate = datetime(y, m, d)
            return candidate
        except Exception:
            pass
        m -= 1
        if m < 1:
            m = 12
            y -= 1

    # 3.3 Fallback: první den dotazovaného měsíce
    return datetime(query_year, query_month, 1)

# 4. Generování rozvrhu směn pro daný měsíc
def generate_schedule(settings, year, month):
    """
    Vygeneruje celý měsíc podle pravidel:
    - long_week = Po,Út práce; St,Čt volno; Pá,So,Ne práce
    - short_week = Po,Út volno; St,Čt práce; Pá,So,Ne volno
    - směna (D/N) se mění až po volnu, tedy při nástupu do nového pracovního setu
    - opěrný bod (anchor) je settings['start_date'] pokud existuje, jinak se použije start_day
    """
    # 4.1 Načtení výchozí směny
    start_shift = settings.get('start_shift', 'N').upper()

    # 4.2 Definice pracovních vzorců pro dlouhý a krátký týden
    long_week = [True, True, False, False, True, True, True]   # Po..Ne (True = práce)
    short_week = [False, False, True, True, False, False, False]

    # 4.3 Výpočet opěrného týdne a směny
    anchor = _resolve_anchor_date(settings, year, month)
    anchor_weekday = anchor.weekday()
    anchor_monday = anchor - timedelta(days=anchor_weekday)
    anchor_week_type = 'long' if long_week[anchor_weekday] else 'short'
    current_shift = start_shift

    # 4.4 Inicializace výstupu a iterace přes dny v měsíci
    first_day = datetime(year, month, 1)
    days_in_month = calendar.monthrange(year, month)[1]
    output = []

    previous_label = None
    for d in range(1, days_in_month + 1):
        current = datetime(year, month, d)
        cur_weekday = current.weekday()
        cur_monday = current - timedelta(days=cur_weekday)

        # 4.5 Výpočet rozdílu v týdnech od opěrného bodu
        week_diff = (cur_monday - anchor_monday).days // 7

        # 4.6 Určení typu týdne (long/short)
        cur_week_type = anchor_week_type if week_diff % 2 == 0 else ('short' if anchor_week_type == 'long' else 'long')
        pattern = long_week if cur_week_type == 'long' else short_week
        is_workday = pattern[cur_weekday]

        # 4.7 Změna směny pouze při nástupu do nového pracovního bloku (po volnu)
        if is_workday and previous_label == 'Volno':
            current_shift = 'N' if current_shift == 'D' else 'D'

        # 4.8 Určení popisku dne
        if is_workday:
            label = 'Ranní směna' if current_shift == 'D' else 'Noční směna'
        else:
            label = 'Volno'

        output.append((current.strftime('%Y-%m-%d'), label))
        previous_label = label

    # 5.0 Vrácení výsledného rozvrhu
    return output

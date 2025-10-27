import json, os
from datetime import datetime, timedelta
import calendar

SETTINGS_FILE = 'settings.json'

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

def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f)

def _resolve_anchor_date(settings, query_year, query_month):
    # 1) pokud existuje přesné start_date, použijeme jej
    start_date_str = settings.get('start_date')
    if start_date_str:
        try:
            return datetime.strptime(start_date_str, '%Y-%m-%d')
        except Exception:
            pass

    # 2) pokud máme pouze start_day, najdeme nejbližší odpovídající datum (occurrence)
    start_day = int(settings.get('start_day', 1))
    # Hledáme nejbližší occurrence start_day, která je <= poslední den query měsíce.
    y = query_year
    m = query_month
    # zkusíme v rámci posledních 12 měsíců najít první candidate od query měsíce dozadu
    for _ in range(12):
        last = calendar.monthrange(y, m)[1]
        d = min(start_day, last)
        try:
            candidate = datetime(y, m, d)
            return candidate
        except Exception:
            pass
        # posun zpět o měsíc
        m -= 1
        if m < 1:
            m = 12
            y -= 1
    # fallback: první den query měsíce
    return datetime(query_year, query_month, 1)

def generate_schedule(settings, year, month):
    """
    Vygeneruje celý měsíc podle pravidel:
    - long_week = Po,Út práce; St,Čt volno; Pá,So,Ne práce
    - short_week = Po,Út volno; St,Čt práce; Pá,So,Ne volno
    - každý týden má jednotnou směnu (D nebo N) a směna se střídá každý týden
    - opěrný bod (anchor) je settings['start_date'] pokud existuje, jinak se použije start_day
      přizpůsobený k dotazovanému měsíci (viz _resolve_anchor_date)
    """
    start_shift = settings.get('start_shift', 'N').upper()

    long_week = [True, True, False, False, True, True, True]   # Po..Ne (True = práce)
    short_week = [False, False, True, True, False, False, False]

    # anchor datum (konkrétní opěrný bod)
    anchor = _resolve_anchor_date(settings, year, month)
    anchor_weekday = anchor.weekday()  # 0=Po
    anchor_monday = anchor - timedelta(days=anchor_weekday)
    anchor_week_type = 'long' if long_week[anchor_weekday] else 'short'
    anchor_shift = start_shift

    first_day = datetime(year, month, 1)
    days_in_month = calendar.monthrange(year, month)[1]
    output = []

    for d in range(1, days_in_month + 1):
        current = datetime(year, month, d)
        cur_weekday = current.weekday()
        cur_monday = current - timedelta(days=cur_weekday)

        # rozdíl v týdnech (může být záporný)
        week_diff = (cur_monday - anchor_monday).days // 7

        if week_diff % 2 == 0:
            cur_week_type = anchor_week_type
            cur_shift = anchor_shift
        else:
            cur_week_type = 'short' if anchor_week_type == 'long' else 'long'
            cur_shift = 'N' if anchor_shift == 'D' else 'D'

        pattern = long_week if cur_week_type == 'long' else short_week
        if pattern[cur_weekday]:
            label = 'Ranní směna' if cur_shift == 'D' else 'Noční směna'
        else:
            label = 'Volno'

        output.append((current.strftime('%Y-%m-%d'), label))

    return output

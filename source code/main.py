from core import load_settings, save_settings, generate_schedule

def main():
    settings = load_settings()
    while True:
        print("\n1. Zobrazit směny pro měsíc")
        print("2. Změnit výchozí směnu")
        print("3. Ukončit")
        choice = input("Vyber možnost: ")
        if choice == '1':
            y = int(input("Zadej rok: "))
            m = int(input("Zadej měsíc (1–12): "))
            generate_schedule(settings, y, m)
        elif choice == '2':
            new_date = input("Nové datum (YYYY-MM-DD): ")
            new_shift = input("Směna (D/N): ")
            new_week = input("Typ týdne (short/long): ")
            settings['start_date'] = new_date
            settings['start_shift'] = new_shift
            settings['week_type'] = new_week
            save_settings(settings)
            print("Nastavení uloženo.")
        elif choice == '3':
            break

if __name__ == "__main__":
    main()

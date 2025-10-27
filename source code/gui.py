import tkinter as tk
from tkinter import ttk, filedialog
from datetime import datetime
import csv
from core import load_settings, save_settings, generate_schedule

def launch_gui():
    root = tk.Tk()
    root.title("Směnový plánovač")
    root.geometry("520x520")

    input_frame = tk.Frame(root)
    input_frame.pack(padx=10, pady=8, fill='x')

    # Výchozí směna
    tk.Label(input_frame, text="Výchozí směna (D/N):").grid(row=0, column=0, sticky='w', padx=4, pady=2)
    shift_var = tk.StringVar()
    tk.Entry(input_frame, textvariable=shift_var, width=6).grid(row=0, column=1, sticky='w', padx=4, pady=2)

    # Start den
    tk.Label(input_frame, text="Start den (DD):").grid(row=1, column=0, sticky='w', padx=4, pady=2)
    day_var = tk.StringVar()
    tk.Entry(input_frame, textvariable=day_var, width=6).grid(row=1, column=1, sticky='w', padx=4, pady=2)

    # Start měsíc
    tk.Label(input_frame, text="Start měsíc (MM):").grid(row=2, column=0, sticky='w', padx=4, pady=2)
    month_var = tk.StringVar(value=str(datetime.now().month).zfill(2))
    tk.Entry(input_frame, textvariable=month_var, width=6).grid(row=2, column=1, sticky='w', padx=4, pady=2)

    # Start rok
    tk.Label(input_frame, text="Start rok (YYYY):").grid(row=3, column=0, sticky='w', padx=4, pady=2)
    year_var = tk.StringVar(value=str(datetime.now().year))
    tk.Entry(input_frame, textvariable=year_var, width=8).grid(row=3, column=1, sticky='w', padx=4, pady=2)

    # Cílový měsíc
    tk.Label(input_frame, text="Cílový měsíc (MM):").grid(row=0, column=2, sticky='w', padx=12, pady=2)
    target_month_var = tk.StringVar(value=str(datetime.now().month).zfill(2))
    tk.Entry(input_frame, textvariable=target_month_var, width=6).grid(row=0, column=3, sticky='w', padx=4, pady=2)

    # Cílový rok
    tk.Label(input_frame, text="Cílový rok (YYYY):").grid(row=1, column=2, sticky='w', padx=12, pady=2)
    target_year_var = tk.StringVar(value=str(datetime.now().year))
    tk.Entry(input_frame, textvariable=target_year_var, width=8).grid(row=1, column=3, sticky='w', padx=4, pady=2)

    # Tlačítka
    btn_frame = tk.Frame(root)
    btn_frame.pack(fill='x', padx=10, pady=(0, 6))
    def build_settings_from_inputs():
        s = {}
        # parse start year/month/day with fallbacks
        try:
            y = int(year_var.get())
        except Exception:
            y = datetime.now().year
        try:
            m = int(month_var.get())
            if m < 1 or m > 12:
                m = datetime.now().month
        except Exception:
            m = datetime.now().month
        # day: clamp to month's last day
        try:
            d = int(day_var.get())
        except Exception:
            d = 1
        import calendar as _cal
        last = _cal.monthrange(y, m)[1]
        d = max(1, min(d, last))
        # build ISO start_date
        start_date = datetime(y, m, d).strftime('%Y-%m-%d')
        s['start_date'] = start_date

        # shift
        shift = shift_var.get().strip().upper()
        s['start_shift'] = 'D' if shift == 'D' else 'N'
        return s

    def on_play():
        settings = build_settings_from_inputs()
        save_settings(settings)

        for row in tree.get_children():
            tree.delete(row)

        try:
            ty = int(target_year_var.get())
            tm = int(target_month_var.get())
            schedule = generate_schedule(settings, ty, tm)
            for datum, smena in schedule:
                tag = 'volno'
                if 'Ranní' in smena:
                    tag = 'd'
                elif 'Noční' in smena:
                    tag = 'n'
                tree.insert("", "end", values=(datum, smena), tags=(tag,))
        except Exception as e:
            tree.insert("", "end", values=("Chyba", str(e)), tags=('volno',))

    def on_export_csv():
        items = tree.get_children()
        if not items:
            return
        file = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV','*.csv')])
        if not file:
            return
        with open(file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Datum','Směna'])
            for it in items:
                writer.writerow(tree.item(it)['values'])

    tk.Button(btn_frame, text="Play", command=on_play).pack(side='left', padx=6)
    tk.Button(btn_frame, text="Export CSV", command=on_export_csv).pack(side='left', padx=6)

    # Výstupní tabulka
    table_frame = tk.Frame(root)
    table_frame.pack(padx=10, pady=4, fill='both', expand=True)

    columns = ("Datum", "Směna")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=18)
    tree.heading("Datum", text="Datum")
    tree.heading("Směna", text="Směna")
    tree.pack(side='left', fill='both', expand=True)

    vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    vsb.pack(side='right', fill='y')

    # Tagy pro barvy
    tree.tag_configure('d', background='#dff0d8')    # světle zelená - ranní
    tree.tag_configure('n', background='#d9ecff')    # světle modrá - noční
    tree.tag_configure('volno', background='#f0f0f0')# šedá - volno

    # Naplnit vstupy z ulozenych nastaveni pokud existuji
    try:
        existing = load_settings()
        if 'start_date' in existing:
            dt = datetime.strptime(existing['start_date'], '%Y-%m-%d')
            day_var.set(str(dt.day).zfill(2))
            month_var.set(str(dt.month).zfill(2))
            year_var.set(str(dt.year))
        elif 'start_day' in existing:
            day_var.set(str(existing['start_day']).zfill(2))
        if 'start_shift' in existing:
            shift_var.set(existing['start_shift'])
    except Exception:
        pass

    root.mainloop()

if __name__ == '__main__':
    launch_gui()

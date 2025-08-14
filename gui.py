import os
import time
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from datetime import datetime
from threading import Thread
import shutil

import piexif
import tkinter.ttk as ttk
import csv

def get_date_piexif(filepath):
    try:
        exif_dict = piexif.load(filepath)
        date_bytes = exif_dict['Exif'].get(piexif.ExifIFD.DateTimeOriginal)
        if date_bytes:
            return date_bytes.decode('utf-8')
    except Exception:
        pass
    return None

class ExifParserGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("EXIF Processor v2.0")
        self.root.geometry("900x500")

        self.folder_path = tk.StringVar()
        self.grouped_folder_path = tk.StringVar()
        self.time_interval = tk.StringVar(value="3")
        self.start_group_number = tk.StringVar(value="1")
        self.overwrite_files = tk.BooleanVar(value=False)

        # Переменные для пульсации кнопки
        self.is_pulsing = False
        self.pulse_colors = ["#3e3e4e", "#565f89"]
        self.current_pulse_color = 0

        # Создаем главный фрейм для лучшей организации
        main_frame = tk.Frame(root, bg="#1a1b26")
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # Создаем левую панель для кнопок
        left_panel = tk.Frame(main_frame, bg="#1a1b26")
        left_panel.pack(side='left', fill='y', padx=5)

        # Создаем правую панель для полей ввода и лога
        right_panel = tk.Frame(main_frame, bg="#1a1b26")
        right_panel.pack(side='right', fill='both', expand=True, padx=5)

        # Фрейм для полей ввода
        top_frame = tk.Frame(right_panel, bg="#1a1b26")
        top_frame.pack(fill='x', pady=5)

        # Первая строка с полем ввода
        entry_frame1 = tk.Frame(top_frame, bg="#1a1b26")
        entry_frame1.pack(fill='x', pady=2)
        tk.Label(entry_frame1, text="Исходная:", bg="#1a1b26", fg="#7aa2f7", 
               font=("Courier New", 10), width=10).pack(side='left')
        self.entry = tk.Entry(entry_frame1, textvariable=self.folder_path,
                            bg="#24283b", fg="#ffffff", insertbackground="#ffffff",
                            relief="flat", font=("Courier New", 10))
        self.entry.pack(side='left', fill='x', expand=True, padx=5)
        tk.Button(entry_frame1, text="...", command=self.select_folder,
                 font=("Courier New", 9), bg="#414868", fg="#ffffff",
                 activebackground="#565f89", activeforeground="#ffffff",
                 relief="flat", width=3).pack(side='right')

        # Вторая строка с полем ввода
        entry_frame2 = tk.Frame(top_frame, bg="#1a1b26")
        entry_frame2.pack(fill='x', pady=2)
        tk.Label(entry_frame2, text="Группы:", bg="#1a1b26", fg="#7aa2f7",
               font=("Courier New", 10), width=10).pack(side='left')
        self.grouped_entry = tk.Entry(entry_frame2, textvariable=self.grouped_folder_path,
                                    bg="#24283b", fg="#ffffff", insertbackground="#ffffff",
                                    relief="flat", font=("Courier New", 10))
        self.grouped_entry.pack(side='left', fill='x', expand=True, padx=5)
        tk.Button(entry_frame2, text="...", command=self.select_grouped_folder,
                 font=("Courier New", 9), bg="#414868", fg="#ffffff",
                 activebackground="#565f89", activeforeground="#ffffff",
                 relief="flat", width=3).pack(side='right')

        # Добавляем поле для ввода интервала времени
        entry_frame3 = tk.Frame(top_frame, bg="#1a1b26")
        entry_frame3.pack(fill='x', pady=2)
        tk.Label(entry_frame3, text="Интервал:", bg="#1a1b26", fg="#7aa2f7",
               font=("Courier New", 10), width=10).pack(side='left')
        self.time_interval_entry = tk.Entry(entry_frame3, textvariable=self.time_interval,
                                    bg="#24283b", fg="#ffffff", insertbackground="#ffffff",
                                    relief="flat", font=("Courier New", 10), width=10)
        self.time_interval_entry.pack(side='left', padx=5)
        tk.Label(entry_frame3, text="сек", bg="#1a1b26", fg="#7aa2f7",
               font=("Courier New", 10)).pack(side='left')

        # Поле для начального номера группы
        entry_frame4 = tk.Frame(top_frame, bg="#1a1b26")
        entry_frame4.pack(fill='x', pady=2)
        tk.Label(entry_frame4, text="Старт с:", bg="#1a1b26", fg="#7aa2f7",
               font=("Courier New", 10), width=10).pack(side='left')
        self.start_group_entry = tk.Entry(entry_frame4, textvariable=self.start_group_number,
                                    bg="#24283b", fg="#ffffff", insertbackground="#ffffff",
                                    relief="flat", font=("Courier New", 10), width=10)
        self.start_group_entry.pack(side='left', padx=5)

        # Чекбокс для перезаписи файлов
        self.overwrite_check = tk.Checkbutton(entry_frame4, text="Перезаписывать файлы",
                                            variable=self.overwrite_files,
                                            bg="#1a1b26", fg="#7aa2f7",
                                            selectcolor="#24283b",
                                            activebackground="#1a1b26",
                                            activeforeground="#7aa2f7",
                                            font=("Courier New", 10))
        self.overwrite_check.pack(side='right', padx=5)

        # Настройка кнопок в левой панели
        btn_style = {
            "width": 12,
            "height": 2,
            "font": ("Courier New", 10, "bold"),
            "bg": "#414868",
            "fg": "#ffffff",
            "activebackground": "#565f89",
            "activeforeground": "#ffffff",
            "relief": "flat"
        }

        self.btn_full = tk.Button(left_panel, text="АНАЛИЗ", command=self.run_full, **btn_style)
        self.btn_full.pack(pady=(0,5))

        self.btn_copy = tk.Button(left_panel, text="КОПИРОВАТЬ", command=self.copy_files_by_group, **btn_style)
        self.btn_copy.pack(pady=5)

        self.btn_move_groups = tk.Button(left_panel, text="ПЕРЕМЕСТИТЬ", command=self.move_files_by_group, **btn_style)
        self.btn_move_groups.pack(pady=5)

        self.btn_move_back = tk.Button(left_panel, text="ВЕРНУТЬ", command=self.move_files_to_main_folder, **btn_style)
        self.btn_move_back.pack(pady=5)

        # Метка времени в верхнем правом углу
        self.time_full = tk.Label(right_panel, text="Время: -", 
                                bg="#1a1b26", fg="#7aa2f7",
                                font=("Courier New", 9))
        self.time_full.pack(anchor='ne', padx=5, pady=5)

        self.progress = tk.DoubleVar()
        # Прогресс бар под полями ввода
        self.progress_bar = ttk.Progressbar(right_panel, variable=self.progress, maximum=100)
        self.progress_bar.pack(fill='x', padx=5, pady=5)

        # Лог в правой панели
        self.log = scrolledtext.ScrolledText(right_panel, bg="#121622", fg="#33ffcc", 
                                           font=('Consolas', 10))
        self.log.pack(fill='both', expand=True, padx=5, pady=5)

        self.parsed_results = []

        # При инициализации оставляем путь пустым, он будет обновляться при выборе исходной папки
        self.grouped_folder_path.set("")


    def move_files_by_group(self):
        if hasattr(self, 'worker_thread') and self.worker_thread.is_alive():
            messagebox.showwarning("Внимание", "Процесс уже запущен")
            return

        folder = self.folder_path.get()
        grouped_folder = self.grouped_folder_path.get().strip()
        if not grouped_folder:
            grouped_folder = folder + "_grouped"
        csv_path = os.path.join(folder, "grouped_dates.csv")
        if not os.path.exists(csv_path):
            messagebox.showerror("Ошибка", "Файл группировки CSV не найден")
            return
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                groups = {}
                for row in reader:
                    group = row['Group']
                    filename = row['FileName']
                    if group not in groups:
                        groups[group] = []
                    groups[group].append(filename)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось прочитать CSV: {e}")
            return

        try:
            start_num = max(1, int(self.start_group_number.get()))
        except ValueError:
            start_num = 1

        # --- Формируем текст подтверждения ---
        confirm_lines = [f"Папка назначения: {grouped_folder}"]
        for group, files in sorted(groups.items(), key=lambda x: int(x[0])):
            group_num = int(group) + start_num - 1
            if files:
                first_file = files[0]
                last_file = files[-1]
                confirm_lines.append(f"Группа {group_num:03d}: {first_file} – {last_file}")

        confirm = self.show_confirm_dialog(confirm_lines)
        if not confirm:
            self.log_message("Операция перемещения отменена пользователем.", "#ff6e6e")
            return

        self.worker_thread = Thread(target=self._move_files_by_group, daemon=True)
        self.worker_thread.start()

    def show_confirm_dialog(self, lines):
        win = tk.Toplevel(self.root)
        win.title("Вы уверены?")
        win.geometry("500x350")
        win.grab_set()
        label = tk.Label(win, text="Будут перемещены группы файлов:", font=("Courier New", 10, "bold"))
        label.pack(pady=8)
        txt = scrolledtext.ScrolledText(win, width=70, height=12, font=("Consolas", 10))
        txt.pack(padx=10, pady=5, fill='both', expand=True)
        txt.insert(tk.END, "\n".join(lines))
        txt.config(state='disabled')
        btn_frame = tk.Frame(win)
        btn_frame.pack(pady=10)
        result = {'ok': False}
        def on_ok():
            result['ok'] = True
            win.destroy()
        def on_cancel():
            win.destroy()
        ok_btn = tk.Button(btn_frame, text="Да, переместить", command=on_ok, width=18, bg="#7aa2f7", fg="#fff", font=("Courier New", 10, "bold"))
        ok_btn.pack(side='left', padx=10)
        cancel_btn = tk.Button(btn_frame, text="Отмена", command=on_cancel, width=12, bg="#414868", fg="#fff", font=("Courier New", 10))
        cancel_btn.pack(side='left', padx=10)
        win.wait_window()
        return result['ok']

    def _move_files_by_group(self):
        folder = self.folder_path.get()
        if not os.path.isdir(folder):
            self.root.after(0, lambda: messagebox.showerror("Ошибка", "Выберите корректную папку с изображениями"))
            return

        grouped_folder = self.grouped_folder_path.get().strip()
        if not grouped_folder:
            grouped_folder = folder + "_grouped"
            self.grouped_folder_path.set(grouped_folder)
            self.root.after(0, lambda: self.log_message(f"Папка для групп не указана, будет использована: {grouped_folder}", "#bb99ff"))
        os.makedirs(grouped_folder, exist_ok=True)

        csv_path = os.path.join(folder, "grouped_dates.csv")
        if not os.path.exists(csv_path):
            self.root.after(0, lambda: messagebox.showerror("Ошибка", "Файл группировки CSV не найден"))
            return

        groups = {}
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    group = row['Group']
                    filename = row['FileName']
                    if group not in groups:
                        groups[group] = []
                    groups[group].append(filename)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Ошибка", f"Не удалось прочитать CSV: {e}"))
            return

        total_files = sum(len(files) for files in groups.values())
        processed_files = 0
        log_buffer = []
        batch_size = 20

        self.root.after(0, lambda: self.progress.set(0))
        self.root.after(0, lambda: self.log_message("\n=== Запуск перемещения файлов ===", "#ffcc33"))
        self.root.after(0, lambda: self.log_message(f"Папка назначения: {grouped_folder}", "#bb99ff"))

        try:
            start_num = max(1, int(self.start_group_number.get()))
        except ValueError:
            start_num = 1
            self.root.after(0, lambda: self.log_message("Неверный формат начального номера, используется значение 1", "#ff6e6e"))

        overwrite = self.overwrite_files.get()

        for group, files in groups.items():
            group_num = int(group) + start_num - 1
            group_folder = os.path.join(grouped_folder, f"{group_num:03d}")
            os.makedirs(group_folder, exist_ok=True)

            for filename in files:
                src_path = os.path.join(folder, filename)
                dst_path = os.path.join(group_folder, filename)
                try:
                    if os.path.exists(dst_path):
                        if overwrite:
                            os.remove(dst_path)
                            shutil.move(src_path, dst_path)
                            rel_dst_path = os.path.relpath(dst_path, grouped_folder)
                            log_buffer.append(f"Перезапись: {filename} -> {rel_dst_path}")
                        else:
                            log_buffer.append(f"Пропуск: {filename} (файл уже существует)")
                            continue
                    else:
                        shutil.move(src_path, dst_path)
                        rel_dst_path = os.path.relpath(dst_path, grouped_folder)
                        log_buffer.append(f"Перемещение: {filename} -> {rel_dst_path}")
                except Exception as e:
                    self.root.after(0, lambda msg=f"Ошибка при перемещении {filename}: {e}": self.log_message(msg, "#ff6e6e"))

                processed_files += 1
                if len(log_buffer) >= batch_size or processed_files == total_files:
                    progress = (processed_files / total_files) * 100
                    self.root.after(0, lambda p=progress: self.progress.set(p))
                    self.root.after(0, lambda lb="\n".join(log_buffer): self.log_message(lb, "#7aa2f7"))
                    log_buffer.clear()

        total_groups = len(groups)
        summary = [
            "\n=== Итоги перемещения ===",
            f"Обработано файлов: {total_files}",
            f"Создано групп: {total_groups}",
            f"Папка назначения: {grouped_folder}"
        ]
        summary.append("\nРаспределение по группам:")
        for group, files in sorted(groups.items(), key=lambda x: int(x[0])):
            summary.append(f"Группа {int(group):03d}: {len(files)} файлов")

        self.root.after(0, lambda: self.log_message("\n".join(summary), "#33ff33"))
        self.root.after(0, lambda: self.log_message("Перемещение по группам завершено", "#33ffcc"))



        # При инициализации оставляем путь пустым, он будет обновляться при выборе исходной папки
        self.grouped_folder_path.set("")

        self.root.configure(bg="#1a1b26")

        self.entry.configure(bg="#2e2e3e", fg="#ffffff", insertbackground="#ffffff")
        self.grouped_entry.configure(bg="#2e2e3e", fg="#ffffff", insertbackground="#ffffff")

        self.btn_full.configure(bg="#3e3e4e", fg="#ffffff", activebackground="#4e4e5e", activeforeground="#ffffff")
        self.btn_copy.configure(bg="#3e3e4e", fg="#ffffff", activebackground="#4e4e5e", activeforeground="#ffffff")
        self.btn_move_back.configure(bg="#3e3e4e", fg="#ffffff", activebackground="#4e4e5e", activeforeground="#ffffff")

        self.time_full.configure(bg="#1e1e2e", fg="#ffffff")


        style = ttk.Style()
        style.theme_use("clam")
        # Темнее фон прогресс-бара
        style.configure("Cyber.Horizontal.TProgressbar",
                       thickness=15,
                       troughcolor="#0e1016",
                       background="#7aa2f7",
                       bordercolor="#181926")
        self.progress_bar.configure(style="Cyber.Horizontal.TProgressbar")

        # Цвет скроллбаров лога
        style.configure("Custom.Vertical.TScrollbar",
                        gripcount=0,
                        background="#24283b",
                        darkcolor="#24283b",
                        lightcolor="#24283b",
                        troughcolor="#1a1b26",
                        bordercolor="#1a1b26",
                        arrowcolor="#7aa2f7")
        style.map("Custom.Vertical.TScrollbar",
                  background=[('active', '#414868'), ('!active', '#24283b')])

        # Применить стиль к скроллбару лога
        for child in self.log.winfo_children():
            if isinstance(child, ttk.Scrollbar):
                child.configure(style="Custom.Vertical.TScrollbar")

        self.log.configure(bg="#121622", fg="#33ffcc", font=('Consolas', 10), insertbackground="#ffffff")

    def log_message(self, msg, color="#33ffcc"):
        self.log.tag_configure(color, foreground=color)
        self.log.insert(tk.END, msg + "\n", color)
        self.log.see(tk.END)

    def select_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.folder_path.set(path)
            # Автоматически обновляем путь для группировки
            default_grouped = path + "_grouped"
            if not self.grouped_folder_path.get():
                self.grouped_folder_path.set(default_grouped)

    def select_grouped_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.grouped_folder_path.set(path)

    def pulse_button(self):
        if self.is_pulsing:
            self.current_pulse_color = (self.current_pulse_color + 1) % 2
            self.btn_copy.configure(bg=self.pulse_colors[self.current_pulse_color])
            self.root.after(500, self.pulse_button)  # Пульсация каждые 500мс

    def stop_pulse(self):
        self.is_pulsing = False
        self.btn_copy.configure(bg="#3e3e4e")  # Возвращаем исходный цвет

    def run_full(self):
        if hasattr(self, 'worker_thread') and self.worker_thread.is_alive():
            messagebox.showwarning("Внимание", "Процесс уже запущен")
            return
        self.parsed_results.clear()
        self.progress.set(0)
        self.log.delete('1.0', tk.END)
        self.worker_thread = Thread(target=self.full_pipeline, daemon=True)
        self.worker_thread.start()

    def full_pipeline(self):
        folder = self.folder_path.get()
        if not os.path.isdir(folder):
            self.root.after(0, lambda: messagebox.showerror("Ошибка", "Выберите корректную папку с изображениями"))
            return

        files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
        files = [f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.tiff', '.tif'))]

        if not files:
            self.root.after(0, lambda: self.log_message("Нет изображений для обработки."))
            return

        self.root.after(0, lambda: self.log_message("\n=== Запуск парсинга Piexif ==="))
        start_parse = time.time()

        batch_size = 20
        log_buffer = []
        total = len(files)
        for i, f in enumerate(files, 1):
            filepath = os.path.join(folder, f)
            date = get_date_piexif(filepath)
            self.parsed_results.append({'filename': f, 'date': date})
            log_buffer.append(f"{f}: {date}")

            if i % batch_size == 0 or i == total:
                progress_percent = i / total * 100
                self.root.after(0, lambda p=progress_percent: self.progress.set(p))
                self.root.after(0, lambda lb="\n".join(log_buffer): self.log_message(lb))
                log_buffer.clear()

        elapsed_parse = time.time() - start_parse
        self.root.after(0, lambda: self.time_full.config(text=f"Парсинг: {elapsed_parse:.4f} с"))
        self.root.after(0, lambda: self.log_message(f"Парсинг завершён за {elapsed_parse:.4f} секунд."))

        # Сохраняем результат парсинга
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"results_piexif_{timestamp}.txt"
            filepath = os.path.join(folder, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Результаты парсинга Piexif ({elapsed_parse:.4f} с)\n\n")
                for item in self.parsed_results:
                    f.write(f"{item['filename']}: {item['date']}\n")
            self.root.after(0, lambda: self.log_message(f"Результаты сохранены в файл: {filepath}"))
        except Exception as e:
            self.root.after(0, lambda: self.log_message(f"Ошибка при сохранении файла: {e}"))

        # Группировка
        self.root.after(0, lambda: self.log_message("\n=== Запуск группировки ==="))
        start_group = time.time()

        valid = []
        for item in self.parsed_results:
            dt_str = item['date']
            if dt_str:
                try:
                    dt = datetime.strptime(dt_str, '%Y:%m:%d %H:%M:%S')
                    valid.append({'filename': item['filename'], 'datetime': dt})
                except Exception:
                    pass

        if not valid:
            self.root.after(0, lambda: self.log_message("Нет файлов с валидной датой для группировки."))
            return

        valid.sort(key=lambda x: x['datetime'])

        groups = []
        group_number = 1
        prev_time = None
        try:
            delta_sec = int(self.time_interval.get())
        except ValueError:
            delta_sec = 3
            self.root.after(0, lambda: self.log_message("Неверный формат интервала, используется значение по умолчанию: 3 сек", "#ff6e6e"))

        for item in valid:
            if prev_time and (item['datetime'] - prev_time).total_seconds() > delta_sec:
                group_number += 1
            groups.append({'filename': item['filename'], 'datetime': item['datetime'], 'group': group_number})
            prev_time = item['datetime']

        out_path = os.path.join(folder, "grouped_dates.csv")
        try:
            with open(out_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['FileName', 'DateTimeOriginal', 'Group'])
                for row in groups:
                    writer.writerow([row['filename'], row['datetime'].strftime('%Y:%m:%d %H:%M:%S'), row['group']])
            self.root.after(0, lambda: self.log_message(f"Группировка завершена. CSV сохранён: {out_path}"))
        except Exception as e:
            self.root.after(0, lambda: self.log_message(f"Ошибка при сохранении CSV: {e}"))

        elapsed_group = time.time() - start_group
        self.root.after(0, lambda: self.time_full.config(text=f"Парсинг: {elapsed_parse:.4f} с, Группировка: {elapsed_group:.4f} с"))
        self.root.after(0, lambda: self.log_message(f"Группировка завершена за {elapsed_group:.4f} секунд."))

        total_elapsed = elapsed_parse + elapsed_group
        self.root.after(0, lambda: self.time_full.config(text=f"Итого: {total_elapsed:.4f} с"))

    def copy_files_by_group(self):
        if hasattr(self, 'worker_thread') and self.worker_thread.is_alive():
            messagebox.showwarning("Внимание", "Процесс уже запущен")
            return
        # Запускаем пульсацию
        self.is_pulsing = True
        self.pulse_button()
        self.worker_thread = Thread(target=self._copy_files_by_group, daemon=True)
        self.worker_thread.start()

    def _copy_files_by_group(self):
        folder = self.folder_path.get()
        if not os.path.isdir(folder):
            self.root.after(0, lambda: messagebox.showerror("Ошибка", "Выберите корректную папку с изображениями"))
            self.root.after(0, self.stop_pulse)  # Останавливаем пульсацию при ошибке
            return

        grouped_folder = self.grouped_folder_path.get().strip()
        if not grouped_folder:
            # Если папка не указана, создаем рядом с исходной
            grouped_folder = folder + "_grouped"
            self.grouped_folder_path.set(grouped_folder)  # Сразу обновляем значение
            self.root.after(0, lambda: self.log_message(f"Папка для групп не указана, будет использована: {grouped_folder}", "#bb99ff"))
            
        os.makedirs(grouped_folder, exist_ok=True)

        csv_path = os.path.join(folder, "grouped_dates.csv")
        if not os.path.exists(csv_path):
            self.root.after(0, lambda: messagebox.showerror("Ошибка", "Файл группировки CSV не найден"))
            return

        groups = {}
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    group = row['Group']
                    filename = row['FileName']
                    if group not in groups:
                        groups[group] = []
                    groups[group].append(filename)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Ошибка", f"Не удалось прочитать CSV: {e}"))
            return

        total_files = sum(len(files) for files in groups.values())
        processed_files = 0
        log_buffer = []
        batch_size = 20

        self.root.after(0, lambda: self.progress.set(0))
        self.root.after(0, lambda: self.log_message("\n=== Запуск копирования файлов ===", "#ffcc33"))  # Желтый цвет для заголовков
        self.root.after(0, lambda: self.log_message(f"Папка назначения: {grouped_folder}", "#bb99ff"))  # Фиолетовый цвет для информации о папке

        # Получаем начальный номер группы
        try:
            start_num = max(1, int(self.start_group_number.get()))
        except ValueError:
            start_num = 1
            self.root.after(0, lambda: self.log_message("Неверный формат начального номера, используется значение 1", "#ff6e6e"))

        overwrite = self.overwrite_files.get()

        for group, files in groups.items():
            group_num = int(group) + start_num - 1  # Учитываем начальный номер
            group_folder = os.path.join(grouped_folder, f"{group_num:03d}")
            os.makedirs(group_folder, exist_ok=True)
            
            for filename in files:
                src_path = os.path.join(folder, filename)
                dst_path = os.path.join(group_folder, filename)
                try:
                    if os.path.exists(dst_path):
                        if overwrite:
                            shutil.copy(src_path, dst_path)
                            rel_dst_path = os.path.relpath(dst_path, grouped_folder)
                            log_buffer.append(f"Перезапись: {filename} -> {rel_dst_path}")
                        else:
                            log_buffer.append(f"Пропуск: {filename} (файл уже существует)")
                            continue
                    else:
                        shutil.copy(src_path, dst_path)
                        rel_dst_path = os.path.relpath(dst_path, grouped_folder)
                        log_buffer.append(f"Копирование: {filename} -> {rel_dst_path}")
                except Exception as e:
                    # Добавляем ошибку сразу в лог с красным цветом
                    self.root.after(0, lambda msg=f"Ошибка при копировании {filename}: {e}": 
                                  self.log_message(msg, "#ff6e6e"))  # Красный цвет для ошибок

                processed_files += 1
                if len(log_buffer) >= batch_size or processed_files == total_files:
                    progress = (processed_files / total_files) * 100
                    self.root.after(0, lambda p=progress: self.progress.set(p))
                    self.root.after(0, lambda lb="\n".join(log_buffer): self.log_message(lb, "#7aa2f7"))  # Голубой цвет для процесса копирования
                    log_buffer.clear()

        # Формируем итоговую статистику
        total_groups = len(groups)
        summary = [
            "\n=== Итоги копирования ===",
            f"Обработано файлов: {total_files}",
            f"Создано групп: {total_groups}",
            f"Папка назначения: {grouped_folder}"
        ]
        
        # Добавляем статистику по группам
        summary.append("\nРаспределение по группам:")
        for group, files in sorted(groups.items(), key=lambda x: int(x[0])):
            group_folder = f"{int(group):03d}"
            summary.append(f"Группа {group_folder}: {len(files)} файлов")

        # Выводим итоги зеленым цветом
        self.root.after(0, lambda: self.log_message("\n".join(summary), "#33ff33"))  # Зеленый цвет для итогов
        self.root.after(0, lambda: self.log_message("Копирование по группам завершено", "#33ffcc"))  # Стандартный цвет для статуса
        
        # Останавливаем пульсацию кнопки
        self.root.after(0, self.stop_pulse)

    def move_files_to_main_folder(self):
        folder = self.folder_path.get()
        grouped_folder = self.grouped_folder_path.get().strip()
        if not os.path.isdir(folder):
            messagebox.showerror("Ошибка", "Выберите корректную папку с изображениями")
            return
        if not os.path.isdir(grouped_folder):
            messagebox.showerror("Ошибка", "Папка групп не найдена")
            return

        subfolders = [os.path.join(grouped_folder, d) for d in os.listdir(grouped_folder) if os.path.isdir(os.path.join(grouped_folder, d))]
        moved = 0
        for subfolder in subfolders:
            for filename in os.listdir(subfolder):
                src_path = os.path.join(subfolder, filename)
                dst_path = os.path.join(folder, filename)
                try:
                    if os.path.exists(dst_path):
                        base, extension = os.path.splitext(filename)
                        counter = 1
                        while os.path.exists(dst_path):
                            dst_path = os.path.join(folder, f"{base}_copy{counter}{extension}")
                            counter += 1
                    shutil.move(src_path, dst_path)
                    moved += 1
                except Exception as e:
                    self.log_message(f"Ошибка при перемещении {filename}: {e}")

        self.log_message(f"Перемещено файлов: {moved}")
        self.log_message("Перемещение файлов в основную папку завершено")

if __name__ == "__main__":
    root = tk.Tk()
    app = ExifParserGUI(root)
    root.mainloop()

import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class FinanceManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Личный финансовый менеджер")
        self.root.geometry("1000x600")

        # Инициализация данных
        self.data_file = "finance_data.json"
        self.data = {
            "transactions": [],
            "categories": {
                "income": ["Зарплата", "Фриланс", "Инвестиции", "Подарки"],
                "expense": ["Еда", "Транспорт", "Жилье", "Развлечения", "Одежда"]
            },
            "settings": {
                "theme": "light"
            }
        }

        # Загрузка данных
        self.load_data()

        # Настройка темы
        self.set_theme(self.data["settings"]["theme"])

        # Создание интерфейса
        self.create_widgets()

    def set_theme(self, theme):
        self.data["settings"]["theme"] = theme
        if theme == "dark":
            self.bg_color = "#2d2d2d"
            self.fg_color = "#ffffff"
            self.entry_bg = "#3d3d3d"
            self.button_bg = "#4d4d4d"
            self.tree_bg = "#3d3d3d"
            self.tree_fg = "#ffffff"
            self.tree_heading_bg = "#2d2d2d"
        else:
            self.bg_color = "#f0f0f0"
            self.fg_color = "#000000"
            self.entry_bg = "#ffffff"
            self.button_bg = "#e0e0e0"
            self.tree_bg = "#ffffff"
            self.tree_fg = "#000000"
            self.tree_heading_bg = "#f0f0f0"

        self.root.configure(bg=self.bg_color)

    def create_widgets(self):
        # Создание меню
        self.create_menu()

        # Основные вкладки
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Вкладка добавления операций
        self.create_transaction_tab()

        # Вкладка просмотра операций
        self.create_history_tab()

        # Вкладка анализа
        self.create_analysis_tab()

        # Вкладка категорий
        self.create_categories_tab()

        # Вкладка настроек
        self.create_settings_tab()

    def create_menu(self):
        menubar = tk.Menu(self.root)

        # Меню файла
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Экспорт данных", command=self.export_data)
        file_menu.add_command(label="Импорт данных", command=self.import_data)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)
        menubar.add_cascade(label="Файл", menu=file_menu)

        self.root.config(menu=menubar)

    def create_transaction_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Добавить операцию")

        # Тип операции
        tk.Label(tab, text="Тип операции:", bg=self.bg_color, fg=self.fg_color).grid(row=0, column=0, padx=10, pady=10,
                                                                                     sticky="w")
        self.transaction_type = tk.StringVar(value="expense")
        tk.Radiobutton(tab, text="Доход", variable=self.transaction_type, value="income",
                       bg=self.bg_color, fg=self.fg_color, selectcolor=self.bg_color).grid(row=0, column=1, padx=5,
                                                                                           pady=5, sticky="w")
        tk.Radiobutton(tab, text="Расход", variable=self.transaction_type, value="expense",
                       bg=self.bg_color, fg=self.fg_color, selectcolor=self.bg_color).grid(row=0, column=2, padx=5,
                                                                                           pady=5, sticky="w")

        # Категория
        tk.Label(tab, text="Категория:", bg=self.bg_color, fg=self.fg_color).grid(row=1, column=0, padx=10, pady=10,
                                                                                  sticky="w")
        self.category = tk.StringVar()
        self.category_combobox = ttk.Combobox(tab, textvariable=self.category, state="readonly")
        self.category_combobox.grid(row=1, column=1, columnspan=2, padx=10, pady=10, sticky="we")
        self.update_category_combobox()

        # Сумма
        tk.Label(tab, text="Сумма:", bg=self.bg_color, fg=self.fg_color).grid(row=2, column=0, padx=10, pady=10,
                                                                              sticky="w")
        self.amount = tk.DoubleVar()
        tk.Entry(tab, textvariable=self.amount, bg=self.entry_bg, fg=self.fg_color).grid(row=2, column=1, columnspan=2,
                                                                                         padx=10, pady=10, sticky="we")

        # Дата
        tk.Label(tab, text="Дата:", bg=self.bg_color, fg=self.fg_color).grid(row=3, column=0, padx=10, pady=10,
                                                                             sticky="w")
        self.date = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        tk.Entry(tab, textvariable=self.date, bg=self.entry_bg, fg=self.fg_color).grid(row=3, column=1, columnspan=2,
                                                                                       padx=10, pady=10, sticky="we")

        # Описание
        tk.Label(tab, text="Описание:", bg=self.bg_color, fg=self.fg_color).grid(row=4, column=0, padx=10, pady=10,
                                                                                 sticky="w")
        self.description = tk.StringVar()
        tk.Entry(tab, textvariable=self.description, bg=self.entry_bg, fg=self.fg_color).grid(row=4, column=1,
                                                                                              columnspan=2, padx=10,
                                                                                              pady=10, sticky="we")

        # Кнопка добавления
        tk.Button(tab, text="Добавить операцию", command=self.add_transaction,
                  bg=self.button_bg, fg=self.fg_color).grid(row=5, column=0, columnspan=3, padx=10, pady=20,
                                                            sticky="we")

        # Привязка события изменения типа операции
        self.transaction_type.trace("w", lambda *args: self.update_category_combobox())

    def update_category_combobox(self):
        transaction_type = self.transaction_type.get()
        self.category_combobox['values'] = self.data["categories"][transaction_type]
        if self.data["categories"][transaction_type]:
            self.category.set(self.data["categories"][transaction_type][0])

    def create_history_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="История операций")

        # Фильтры
        filter_frame = tk.Frame(tab, bg=self.bg_color)
        filter_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(filter_frame, text="Тип:", bg=self.bg_color, fg=self.fg_color).grid(row=0, column=0, padx=5, pady=5)
        self.filter_type = tk.StringVar(value="all")
        ttk.Combobox(filter_frame, textvariable=self.filter_type, values=["all", "income", "expense"],
                     state="readonly").grid(row=0, column=1, padx=5, pady=5)

        tk.Label(filter_frame, text="Категория:", bg=self.bg_color, fg=self.fg_color).grid(row=0, column=2, padx=5,
                                                                                           pady=5)
        self.filter_category = tk.StringVar()
        ttk.Combobox(filter_frame, textvariable=self.filter_category, state="readonly").grid(row=0, column=3, padx=5,
                                                                                             pady=5)

        tk.Label(filter_frame, text="Дата от:", bg=self.bg_color, fg=self.fg_color).grid(row=0, column=4, padx=5,
                                                                                         pady=5)
        self.filter_date_from = tk.StringVar()
        tk.Entry(filter_frame, textvariable=self.filter_date_from, width=10, bg=self.entry_bg, fg=self.fg_color).grid(
            row=0, column=5, padx=5, pady=5)

        tk.Label(filter_frame, text="до:", bg=self.bg_color, fg=self.fg_color).grid(row=0, column=6, padx=5, pady=5)
        self.filter_date_to = tk.StringVar()
        tk.Entry(filter_frame, textvariable=self.filter_date_to, width=10, bg=self.entry_bg, fg=self.fg_color).grid(
            row=0, column=7, padx=5, pady=5)

        tk.Button(filter_frame, text="Применить", command=self.apply_filters,
                  bg=self.button_bg, fg=self.fg_color).grid(row=0, column=8, padx=5, pady=5)

        # Таблица операций
        columns = ("id", "date", "type", "category", "amount", "description")
        self.transactions_tree = ttk.Treeview(tab, columns=columns, show="headings", selectmode="browse")

        self.transactions_tree.heading("id", text="ID")
        self.transactions_tree.heading("date", text="Дата")
        self.transactions_tree.heading("type", text="Тип")
        self.transactions_tree.heading("category", text="Категория")
        self.transactions_tree.heading("amount", text="Сумма")
        self.transactions_tree.heading("description", text="Описание")

        self.transactions_tree.column("id", width=50, anchor="center")
        self.transactions_tree.column("date", width=100, anchor="center")
        self.transactions_tree.column("type", width=100, anchor="center")
        self.transactions_tree.column("category", width=150, anchor="center")
        self.transactions_tree.column("amount", width=100, anchor="center")
        self.transactions_tree.column("description", width=250, anchor="w")

        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=self.transactions_tree.yview)
        self.transactions_tree.configure(yscrollcommand=scrollbar.set)

        self.transactions_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Кнопка удаления
        tk.Button(tab, text="Удалить выбранное", command=self.delete_selected_transaction,
                  bg=self.button_bg, fg=self.fg_color).pack(side="bottom", fill="x", padx=10, pady=10)

        # Обновление таблицы
        self.update_transactions_tree()

    def create_analysis_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Анализ")

        # Период анализа
        period_frame = tk.Frame(tab, bg=self.bg_color)
        period_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(period_frame, text="Период:", bg=self.bg_color, fg=self.fg_color).pack(side="left", padx=5, pady=5)
        self.analysis_period = tk.StringVar(value="month")
        ttk.Combobox(period_frame, textvariable=self.analysis_period,
                     values=["day", "week", "month", "year", "all"], state="readonly").pack(side="left", padx=5, pady=5)

        tk.Button(period_frame, text="Обновить", command=self.update_analysis,
                  bg=self.button_bg, fg=self.fg_color).pack(side="left", padx=5, pady=5)

        # Графики
        self.figure = plt.Figure(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, tab)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Статистика
        stats_frame = tk.Frame(tab, bg=self.bg_color)
        stats_frame.pack(fill=tk.X, padx=10, pady=10)

        self.total_income_label = tk.Label(stats_frame, text="Доходы: 0", bg=self.bg_color, fg=self.fg_color)
        self.total_income_label.pack(side="left", padx=10, pady=5)

        self.total_expense_label = tk.Label(stats_frame, text="Расходы: 0", bg=self.bg_color, fg=self.fg_color)
        self.total_expense_label.pack(side="left", padx=10, pady=5)

        self.balance_label = tk.Label(stats_frame, text="Баланс: 0", bg=self.bg_color, fg=self.fg_color)
        self.balance_label.pack(side="left", padx=10, pady=5)

        # Первоначальное обновление анализа
        self.update_analysis()

    def create_categories_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Категории")

        # Доходы
        tk.Label(tab, text="Категории доходов:", bg=self.bg_color, fg=self.fg_color).pack(pady=(10, 5))
        self.income_categories_listbox = tk.Listbox(tab, bg=self.entry_bg, fg=self.fg_color)
        self.income_categories_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Добавление категории доходов
        income_frame = tk.Frame(tab, bg=self.bg_color)
        income_frame.pack(fill=tk.X, padx=10, pady=5)

        self.new_income_category = tk.StringVar()
        tk.Entry(income_frame, textvariable=self.new_income_category, bg=self.entry_bg, fg=self.fg_color).pack(
            side="left", fill=tk.X, expand=True, padx=5)
        tk.Button(income_frame, text="Добавить", command=lambda: self.add_category("income"),
                  bg=self.button_bg, fg=self.fg_color).pack(side="left", padx=5)

        # Расходы
        tk.Label(tab, text="Категории расходов:", bg=self.bg_color, fg=self.fg_color).pack(pady=(10, 5))
        self.expense_categories_listbox = tk.Listbox(tab, bg=self.entry_bg, fg=self.fg_color)
        self.expense_categories_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Добавление категории расходов
        expense_frame = tk.Frame(tab, bg=self.bg_color)
        expense_frame.pack(fill=tk.X, padx=10, pady=5)

        self.new_expense_category = tk.StringVar()
        tk.Entry(expense_frame, textvariable=self.new_expense_category, bg=self.entry_bg, fg=self.fg_color).pack(
            side="left", fill=tk.X, expand=True, padx=5)
        tk.Button(expense_frame, text="Добавить", command=lambda: self.add_category("expense"),
                  bg=self.button_bg, fg=self.fg_color).pack(side="left", padx=5)

        # Кнопка удаления
        tk.Button(tab, text="Удалить выбранные", command=self.delete_selected_categories,
                  bg=self.button_bg, fg=self.fg_color).pack(fill=tk.X, padx=10, pady=10)

        # Обновление списков категорий
        self.update_categories_lists()

    def create_settings_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Настройки")

        # Тема
        tk.Label(tab, text="Тема интерфейса:", bg=self.bg_color, fg=self.fg_color).pack(pady=(20, 5))
        self.theme_var = tk.StringVar(value=self.data["settings"]["theme"])
        theme_frame = tk.Frame(tab, bg=self.bg_color)
        theme_frame.pack()

        tk.Radiobutton(theme_frame, text="Светлая", variable=self.theme_var, value="light",
                       command=self.change_theme, bg=self.bg_color, fg=self.fg_color, selectcolor=self.bg_color).pack(
            side="left", padx=10)
        tk.Radiobutton(theme_frame, text="Темная", variable=self.theme_var, value="dark",
                       command=self.change_theme, bg=self.bg_color, fg=self.fg_color, selectcolor=self.bg_color).pack(
            side="left", padx=10)

        # Резервное копирование
        tk.Label(tab, text="Резервное копирование:", bg=self.bg_color, fg=self.fg_color).pack(pady=(20, 5))

        backup_frame = tk.Frame(tab, bg=self.bg_color)
        backup_frame.pack()

        tk.Button(backup_frame, text="Создать резервную копию", command=self.create_backup,
                  bg=self.button_bg, fg=self.fg_color).pack(side="left", padx=5, pady=5)
        tk.Button(backup_frame, text="Восстановить из копии", command=self.restore_from_backup,
                  bg=self.button_bg, fg=self.fg_color).pack(side="left", padx=5, pady=5)

    def change_theme(self):
        self.set_theme(self.theme_var.get())
        self.save_data()
        # Пересоздаем интерфейс для применения новой темы
        for child in self.root.winfo_children():
            child.destroy()
        self.create_widgets()

    def add_transaction(self):
        try:
            transaction = {
                "id": len(self.data["transactions"]) + 1,
                "date": self.date.get(),
                "type": self.transaction_type.get(),
                "category": self.category.get(),
                "amount": float(self.amount.get()),
                "description": self.description.get()
            }

            self.data["transactions"].append(transaction)
            self.save_data()

            # Очистка полей
            self.amount.set(0)
            self.description.set("")

            # Обновление таблицы
            self.update_transactions_tree()
            self.update_analysis()

            messagebox.showinfo("Успех", "Операция успешно добавлена")
        except ValueError:
            messagebox.showerror("Ошибка", "Проверьте правильность введенных данных")

    def update_transactions_tree(self):
        # Очистка таблицы
        for item in self.transactions_tree.get_children():
            self.transactions_tree.delete(item)

        # Заполнение таблицы
        for transaction in self.data["transactions"]:
            self.transactions_tree.insert("", "end", values=(
                transaction["id"],
                transaction["date"],
                "Доход" if transaction["type"] == "income" else "Расход",
                transaction["category"],
                f"{transaction['amount']:.2f}",
                transaction["description"]
            ))

    def apply_filters(self):
        # В реальном приложении здесь бы применялись фильтры к данным
        # Для простоты просто обновляем таблицу
        self.update_transactions_tree()

    def delete_selected_transaction(self):
        selected = self.transactions_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите операцию для удаления")
            return

        selected_id = int(self.transactions_tree.item(selected[0], "values")[0])

        # Удаление операции
        self.data["transactions"] = [t for t in self.data["transactions"] if t["id"] != selected_id]
        self.save_data()

        # Обновление таблицы
        self.update_transactions_tree()
        self.update_analysis()

        messagebox.showinfo("Успех", "Операция успешно удалена")

    def update_analysis(self):
        # Расчет статистики
        total_income = sum(t["amount"] for t in self.data["transactions"] if t["type"] == "income")
        total_expense = sum(t["amount"] for t in self.data["transactions"] if t["type"] == "expense")
        balance = total_income - total_expense

        # Обновление меток
        self.total_income_label.config(text=f"Доходы: {total_income:.2f}")
        self.total_expense_label.config(text=f"Расходы: {total_expense:.2f}")
        self.balance_label.config(text=f"Баланс: {balance:.2f}")

        # Создание графиков
        self.figure.clear()

        # График доходов по категориям
        income_data = {}
        for t in self.data["transactions"]:
            if t["type"] == "income":
                income_data[t["category"]] = income_data.get(t["category"], 0) + t["amount"]

        if income_data:
            ax1 = self.figure.add_subplot(121)
            ax1.pie(income_data.values(), labels=income_data.keys(), autopct="%1.1f%%")
            ax1.set_title("Доходы по категориям")

        # График расходов по категориям
        expense_data = {}
        for t in self.data["transactions"]:
            if t["type"] == "expense":
                expense_data[t["category"]] = expense_data.get(t["category"], 0) + t["amount"]

        if expense_data:
            ax2 = self.figure.add_subplot(122)
            ax2.pie(expense_data.values(), labels=expense_data.keys(), autopct="%1.1f%%")
            ax2.set_title("Расходы по категориям")

        self.canvas.draw()

    def add_category(self, category_type):
        if category_type == "income":
            new_category = self.new_income_category.get().strip()
        else:
            new_category = self.new_expense_category.get().strip()

        if not new_category:
            messagebox.showwarning("Внимание", "Введите название категории")
            return

        if new_category in self.data["categories"][category_type]:
            messagebox.showwarning("Внимание", "Такая категория уже существует")
            return

        self.data["categories"][category_type].append(new_category)
        self.save_data()

        if category_type == "income":
            self.new_income_category.set("")
        else:
            self.new_expense_category.set("")

        self.update_categories_lists()
        self.update_category_combobox()

        messagebox.showinfo("Успех", "Категория успешно добавлена")

    def update_categories_lists(self):
        self.income_categories_listbox.delete(0, tk.END)
        for category in self.data["categories"]["income"]:
            self.income_categories_listbox.insert(tk.END, category)

        self.expense_categories_listbox.delete(0, tk.END)
        for category in self.data["categories"]["expense"]:
            self.expense_categories_listbox.insert(tk.END, category)

    def delete_selected_categories(self):
        # Удаление выбранных категорий доходов
        selected_income = self.income_categories_listbox.curselection()
        if selected_income:
            category = self.income_categories_listbox.get(selected_income[0])
            self.data["categories"]["income"].remove(category)

        # Удаление выбранных категорий расходов
        selected_expense = self.expense_categories_listbox.curselection()
        if selected_expense:
            category = self.expense_categories_listbox.get(selected_expense[0])
            self.data["categories"]["expense"].remove(category)

        self.save_data()
        self.update_categories_lists()
        self.update_category_combobox()

        messagebox.showinfo("Успех", "Выбранные категории удалены")

    def create_backup(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Сохранить резервную копию"
        )

        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(self.data, f, ensure_ascii=False, indent=4)
                messagebox.showinfo("Успех", "Резервная копия успешно создана")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось создать резервную копию: {str(e)}")

    def restore_from_backup(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Выберите резервную копию для восстановления"
        )

        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
                self.save_data()

                # Пересоздаем интерфейс для применения новых данных
                for child in self.root.winfo_children():
                    child.destroy()
                self.create_widgets()

                messagebox.showinfo("Успех", "Данные успешно восстановлены из резервной копии")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось восстановить данные: {str(e)}")

    def export_data(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Экспорт данных"
        )

        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(self.data, f, ensure_ascii=False, indent=4)
                messagebox.showinfo("Успех", "Данные успешно экспортированы")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось экспортировать данные: {str(e)}")

    def import_data(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Импорт данных"
        )

        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
                self.save_data()

                # Пересоздаем интерфейс для применения новых данных
                for child in self.root.winfo_children():
                    child.destroy()
                self.create_widgets()

                messagebox.showinfo("Успех", "Данные успешно импортированы")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось импортировать данные: {str(e)}")

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except:
                # Если файл поврежден, создаем новый с данными по умолчанию
                self.save_data()
        else:
            self.save_data()

    def save_data(self):
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    root = tk.Tk()
    app = FinanceManager(root)
    root.mainloop()
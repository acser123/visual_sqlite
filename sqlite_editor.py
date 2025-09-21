import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sqlite3

class RecordWindow(tk.Toplevel):
    def __init__(self, parent, columns, record=None):
        super().__init__(parent)
        self.transient(parent)
        self.parent = parent
        self.columns = columns
        self.record = record
        self.entries = {}

        if self.record:
            self.title("Edit Record")
        else:
            self.title("Add Record")

        for i, col in enumerate(self.columns):
            ttk.Label(self, text=col).grid(row=i, column=0, padx=5, pady=5, sticky="w")
            entry = ttk.Entry(self, width=40)
            entry.grid(row=i, column=1, padx=5, pady=5)
            if self.record:
                entry.insert(0, self.record[i])
            self.entries[col] = entry

        button_frame = ttk.Frame(self)
        button_frame.grid(row=len(self.columns), columnspan=2, pady=10)

        save_button = ttk.Button(button_frame, text="Save", command=self.save)
        save_button.pack(side="left", padx=5)
        cancel_button = ttk.Button(button_frame, text="Cancel", command=self.destroy)
        cancel_button.pack(side="left", padx=5)

    def save(self):
        values = [entry.get() for entry in self.entries.values()]
        self.parent.save_record(values, self.record)
        self.destroy()

class SQLiteEditor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SQLite Editor")
        self.geometry("800x600")
        self.conn = None

        # Frame for database connection
        db_frame = ttk.LabelFrame(self, text="Database Connection")
        db_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(db_frame, text="Database File:").pack(side="left", padx=5, pady=5)
        self.db_path_entry = ttk.Entry(db_frame, width=50)
        self.db_path_entry.pack(side="left", padx=5, pady=5, expand=True, fill="x")

        self.connect_button = ttk.Button(db_frame, text="Connect", command=self.connect_db)
        self.connect_button.pack(side="left", padx=5, pady=5)

        # Frame for schema and data
        main_frame = ttk.Frame(self)
        main_frame.pack(padx=10, pady=10, fill="both", expand=True)

        schema_frame = ttk.LabelFrame(main_frame, text="Schema")
        schema_frame.pack(side="left", padx=5, pady=5, fill="y")

        self.table_list = tk.Listbox(schema_frame)
        self.table_list.pack(fill="both", expand=True)
        self.table_list.bind("<<ListboxSelect>>", self.show_table_data)

        data_frame = ttk.LabelFrame(main_frame, text="Data")
        data_frame.pack(side="left", padx=5, pady=5, fill="both", expand=True)

        self.data_tree = ttk.Treeview(data_frame)
        self.data_tree.pack(fill="both", expand=True)

        # Buttons for editing
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=5)

        self.add_button = ttk.Button(button_frame, text="Add Record", command=self.add_record)
        self.add_button.pack(side="left", padx=5)
        self.edit_button = ttk.Button(button_frame, text="Edit Record", command=self.edit_record)
        self.edit_button.pack(side="left", padx=5)
        self.delete_button = ttk.Button(button_frame, text="Delete Record", command=self.delete_record)
        self.delete_button.pack(side="left", padx=5)


    def connect_db(self):
        db_path = self.db_path_entry.get()
        if not db_path:
            db_path = filedialog.askopenfilename(
                title="Select SQLite Database File",
                filetypes=(("SQLite files", "*.sqlite *.db"), ("All files", "*.*"))
            )
            if not db_path:
                return
            self.db_path_entry.delete(0, tk.END)
            self.db_path_entry.insert(0, db_path)

        try:
            self.conn = sqlite3.connect(db_path)
            self.load_schema()
            messagebox.showinfo("Success", "Connected to the database successfully.")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to connect to database: {e}")

    def load_schema(self):
        if not self.conn:
            return

        self.table_list.delete(0, tk.END)
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        for table in tables:
            self.table_list.insert(tk.END, table[0])

    def show_table_data(self, event):
        selection = self.table_list.curselection()
        if not selection:
            return

        table_name = self.table_list.get(selection[0])

        # Clear previous data
        for i in self.data_tree.get_children():
            self.data_tree.delete(i)
        self.data_tree["columns"] = []

        if not self.conn:
            return

        cursor = self.conn.cursor()
        try:
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [info[1] for info in cursor.fetchall()]
            self.data_tree["columns"] = columns

            for col in columns:
                self.data_tree.heading(col, text=col)
                self.data_tree.column(col, width=100)

            self.data_tree.heading("#0", text="Row ID")
            self.data_tree.column("#0", width=50)

            cursor.execute(f"SELECT rowid, * FROM {table_name}")
            for row in cursor.fetchall():
                self.data_tree.insert("", "end", text=row[0], values=row[1:])
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to fetch data for table {table_name}: {e}")

    def delete_record(self):
        selected_item = self.data_tree.focus()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a record to delete.")
            return

        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this record?"):
            return

        selection = self.table_list.curselection()
        if not selection:
            return
        table_name = self.table_list.get(selection[0])

        row_id = self.data_tree.item(selected_item)["text"]

        if not self.conn:
            return

        cursor = self.conn.cursor()
        try:
            cursor.execute(f"DELETE FROM {table_name} WHERE rowid = ?", (row_id,))
            self.conn.commit()
            self.show_table_data(None)  # Refresh data
            messagebox.showinfo("Success", "Record deleted successfully.")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to delete record: {e}")

    def add_record(self):
        selection = self.table_list.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a table to add a record to.")
            return
        table_name = self.table_list.get(selection[0])

        cursor = self.conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [info[1] for info in cursor.fetchall()]

        RecordWindow(self, columns)

    def edit_record(self):
        selected_item = self.data_tree.focus()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a record to edit.")
            return

        selection = self.table_list.curselection()
        if not selection:
            return
        table_name = self.table_list.get(selection[0])

        record_values = self.data_tree.item(selected_item)["values"]
        row_id = self.data_tree.item(selected_item)["text"]

        cursor = self.conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [info[1] for info in cursor.fetchall()]

        RecordWindow(self, columns, record=(record_values, row_id))

    def save_record(self, values, record=None):
        selection = self.table_list.curselection()
        if not selection:
            return
        table_name = self.table_list.get(selection[0])

        cursor = self.conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [info[1] for info in cursor.fetchall()]

        if record: # Update
            row_id = record[1]
            set_clause = ", ".join([f"{col} = ?" for col in columns])
            try:
                cursor.execute(f"UPDATE {table_name} SET {set_clause} WHERE rowid = ?", (*values, row_id))
                self.conn.commit()
                self.show_table_data(None)
                messagebox.showinfo("Success", "Record updated successfully.")
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Failed to update record: {e}")
        else: # Insert
            placeholders = ", ".join(["?" for _ in columns])
            try:
                cursor.execute(f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})", values)
                self.conn.commit()
                self.show_table_data(None)
                messagebox.showinfo("Success", "Record added successfully.")
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Failed to add record: {e}")

if __name__ == "__main__":
    app = SQLiteEditor()
    app.mainloop()

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
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

class AddTableWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.transient(parent)
        self.parent = parent
        self.title("Add New Table")
        self.geometry("400x400")

        self.column_widgets = []

        # Main frame
        main_frame = ttk.Frame(self)
        main_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Table Name
        name_frame = ttk.Frame(main_frame)
        name_frame.pack(fill="x", pady=5)
        ttk.Label(name_frame, text="Table Name:").pack(side="left", padx=5)
        self.table_name_entry = ttk.Entry(name_frame)
        self.table_name_entry.pack(side="left", fill="x", expand=True, padx=5)

        # Columns Frame
        columns_outer_frame = ttk.LabelFrame(main_frame, text="Columns")
        columns_outer_frame.pack(fill="both", expand=True, pady=5)

        self.columns_frame = ttk.Frame(columns_outer_frame)
        self.columns_frame.pack(fill="both", expand=True)

        # Add/Remove buttons for columns
        col_button_frame = ttk.Frame(main_frame)
        col_button_frame.pack(pady=5)
        ttk.Button(col_button_frame, text="Add Column", command=self.add_column_row).pack(side="left", padx=5)
        ttk.Button(col_button_frame, text="Remove Column", command=self.remove_column_row).pack(side="left", padx=5)

        # Create/Cancel buttons
        main_button_frame = ttk.Frame(main_frame)
        main_button_frame.pack(pady=10, side="bottom")
        ttk.Button(main_button_frame, text="Create Table", command=self.create_table).pack(side="left", padx=5)
        ttk.Button(main_button_frame, text="Cancel", command=self.destroy).pack(side="left", padx=5)

        # Start with one column row
        self.add_column_row()

    def add_column_row(self):
        frame = ttk.Frame(self.columns_frame)
        frame.pack(fill="x", padx=5, pady=2)

        name_label = ttk.Label(frame, text="Name:")
        name_label.pack(side="left", padx=2)
        name_entry = ttk.Entry(frame, width=15)
        name_entry.pack(side="left", padx=2)

        type_label = ttk.Label(frame, text="Type:")
        type_label.pack(side="left", padx=2)
        type_combo = ttk.Combobox(frame, values=["TEXT", "INTEGER", "REAL", "NUMERIC", "BLOB"], width=10)
        type_combo.pack(side="left", padx=2, fill="x", expand=True)
        type_combo.set("TEXT")

        self.column_widgets.append((frame, name_entry, type_combo))

    def remove_column_row(self):
        if len(self.column_widgets) > 1:
            frame, _, _ = self.column_widgets.pop()
            frame.destroy()

    def create_table(self):
        table_name = self.table_name_entry.get().strip()
        if not table_name:
            messagebox.showerror("Error", "Table name cannot be empty.", parent=self)
            return

        columns = []
        for _, name_entry, type_combo in self.column_widgets:
            col_name = name_entry.get().strip()
            col_type = type_combo.get().strip()
            if not col_name:
                messagebox.showerror("Error", "Column name cannot be empty.", parent=self)
                return
            if not col_type:
                messagebox.showerror("Error", "Column type cannot be empty.", parent=self)
                return
            columns.append((col_name, col_type))

        if not columns:
            messagebox.showerror("Error", "Table must have at least one column.", parent=self)
            return

        self.parent.create_table(table_name, columns)
        self.destroy()

class AddColumnWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.transient(parent)
        self.parent = parent
        self.title("Add Column")

        # Column Name
        ttk.Label(self, text="Column Name:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.name_entry = ttk.Entry(self, width=30)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        # Column Type
        ttk.Label(self, text="Data Type:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.type_combo = ttk.Combobox(self, values=["TEXT", "INTEGER", "REAL", "NUMERIC", "BLOB"], width=27)
        self.type_combo.grid(row=1, column=1, padx=5, pady=5)
        self.type_combo.set("TEXT")

        # Default Value
        ttk.Label(self, text="Default Value:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.default_entry = ttk.Entry(self, width=30)
        self.default_entry.grid(row=2, column=1, padx=5, pady=5)

        # Buttons
        button_frame = ttk.Frame(self)
        button_frame.grid(row=3, columnspan=2, pady=10)
        ttk.Button(button_frame, text="Add", command=self.add).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.destroy).pack(side="left", padx=5)

    def add(self):
        name = self.name_entry.get().strip()
        dtype = self.type_combo.get().strip()
        default = self.default_entry.get().strip()

        if not name or not dtype:
            messagebox.showerror("Error", "Column name and type are required.", parent=self)
            return

        self.parent.execute_add_column(name, dtype, default)
        self.destroy()

class RenameColumnWindow(tk.Toplevel):
    def __init__(self, parent, columns):
        super().__init__(parent)
        self.transient(parent)
        self.parent = parent
        self.title("Rename Column")

        # Old Column Name
        ttk.Label(self, text="Column to Rename:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.old_name_combo = ttk.Combobox(self, values=columns, width=30, state="readonly")
        self.old_name_combo.grid(row=0, column=1, padx=5, pady=5)
        if columns:
            self.old_name_combo.set(columns[0])

        # New Column Name
        ttk.Label(self, text="New Column Name:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.new_name_entry = ttk.Entry(self, width=33)
        self.new_name_entry.grid(row=1, column=1, padx=5, pady=5)

        # Buttons
        button_frame = ttk.Frame(self)
        button_frame.grid(row=2, columnspan=2, pady=10)
        ttk.Button(button_frame, text="Rename", command=self.rename).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.destroy).pack(side="left", padx=5)

    def rename(self):
        old_name = self.old_name_combo.get()
        new_name = self.new_name_entry.get().strip()

        if not old_name or not new_name:
            messagebox.showerror("Error", "Both old and new column names are required.", parent=self)
            return

        self.parent.execute_rename_column(old_name, new_name)
        self.destroy()

class DeleteColumnWindow(tk.Toplevel):
    def __init__(self, parent, columns):
        super().__init__(parent)
        self.transient(parent)
        self.parent = parent
        self.title("Delete Column")

        ttk.Label(self, text="Column to Delete:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.column_combo = ttk.Combobox(self, values=columns, width=30, state="readonly")
        self.column_combo.grid(row=0, column=1, padx=5, pady=5)
        if columns:
            self.column_combo.set(columns[0])

        button_frame = ttk.Frame(self)
        button_frame.grid(row=1, columnspan=2, pady=10)
        ttk.Button(button_frame, text="Delete", command=self.delete).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.destroy).pack(side="left", padx=5)

    def delete(self):
        column_name = self.column_combo.get()
        if not column_name:
            messagebox.showerror("Error", "You must select a column to delete.", parent=self)
            return

        if messagebox.askyesno("Confirm", f"Are you sure you want to delete the column '{column_name}'? This cannot be undone.", parent=self):
            self.parent.execute_delete_column(column_name)

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

        schema_button_frame = ttk.Frame(schema_frame)
        schema_button_frame.pack(pady=5)

        self.add_table_button = ttk.Button(schema_button_frame, text="Add", command=self.add_table)
        self.add_table_button.pack(side="left", padx=2)
        self.rename_table_button = ttk.Button(schema_button_frame, text="Rename", command=self.rename_table)
        self.rename_table_button.pack(side="left", padx=2)
        self.delete_table_button = ttk.Button(schema_button_frame, text="Delete", command=self.delete_table)
        self.delete_table_button.pack(side="left", padx=2)

        data_frame = ttk.LabelFrame(main_frame, text="Data")
        data_frame.pack(side="left", padx=5, pady=5, fill="both", expand=True)

        column_button_frame = ttk.Frame(data_frame)
        column_button_frame.pack(pady=5, fill="x")

        self.add_column_button = ttk.Button(column_button_frame, text="Add Column", command=self.add_column)
        self.add_column_button.pack(side="left", padx=5)
        self.rename_column_button = ttk.Button(column_button_frame, text="Rename Column", command=self.rename_column)
        self.rename_column_button.pack(side="left", padx=5)
        self.delete_column_button = ttk.Button(column_button_frame, text="Delete Column", command=self.delete_column)
        self.delete_column_button.pack(side="left", padx=5)

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

    def delete_table(self):
        selection = self.table_list.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a table to delete.")
            return

        table_name = self.table_list.get(selection[0])

        if not messagebox.askyesno("Confirm", f"Are you sure you want to delete the table '{table_name}'? This cannot be undone."):
            return

        if not self.conn:
            return

        cursor = self.conn.cursor()
        try:
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
            self.conn.commit()
            self.load_schema()
            # Clear the data view
            for i in self.data_tree.get_children():
                self.data_tree.delete(i)
            self.data_tree["columns"] = []
            messagebox.showinfo("Success", f"Table '{table_name}' deleted successfully.")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to delete table '{table_name}': {e}")

    def rename_table(self):
        selection = self.table_list.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a table to rename.")
            return

        old_name = self.table_list.get(selection[0])

        new_name = simpledialog.askstring("Rename Table", "Enter new table name:", parent=self)

        if not new_name or new_name.isspace():
            return

        if not self.conn:
            return

        cursor = self.conn.cursor()
        try:
            # It's important to quote table names to handle spaces and special characters
            cursor.execute(f'ALTER TABLE "{old_name}" RENAME TO "{new_name}"')
            self.conn.commit()
            self.load_schema()

            # Update the listbox selection to the new name if possible
            for i, item in enumerate(self.table_list.get(0, tk.END)):
                if item == new_name:
                    self.table_list.selection_set(i)
                    self.show_table_data(None)
                    break

            messagebox.showinfo("Success", f"Table '{old_name}' renamed to '{new_name}' successfully.")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to rename table '{old_name}': {e}")

    def add_table(self):
        if not self.conn:
            messagebox.showwarning("Warning", "Please connect to a database first.")
            return
        AddTableWindow(self)

    def create_table(self, table_name, columns):
        if not self.conn:
            return

        # Quote identifiers to be safe
        quoted_table_name = f'"{table_name}"'
        column_defs = []
        for name, type in columns:
            column_defs.append(f'"{name}" {type}')

        sql = f"CREATE TABLE {quoted_table_name} ({', '.join(column_defs)})"

        cursor = self.conn.cursor()
        try:
            cursor.execute(sql)
            self.conn.commit()
            self.load_schema()
            messagebox.showinfo("Success", f"Table '{table_name}' created successfully.")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to create table '{table_name}': {e}")

    def add_column(self):
        selection = self.table_list.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a table first.")
            return
        AddColumnWindow(self)

    def execute_add_column(self, col_name, col_type, col_default):
        selection = self.table_list.curselection()
        if not selection:
            return # Should not happen if button is used correctly
        table_name = self.table_list.get(selection[0])

        sql = f'ALTER TABLE "{table_name}" ADD COLUMN "{col_name}" {col_type}'
        if col_default:
            # For default values, strings should be quoted, numbers should not.
            # A simple check for digits should suffice for this tool's purpose.
            if col_default.isdigit() or (col_default.startswith('-') and col_default[1:].isdigit()):
                 sql += f" DEFAULT {col_default}"
            else:
                 sql += f" DEFAULT '{col_default}'"

        cursor = self.conn.cursor()
        try:
            cursor.execute(sql)
            self.conn.commit()
            self.show_table_data(None) # Refresh data view
            messagebox.showinfo("Success", f"Column '{col_name}' added to table '{table_name}'.")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to add column: {e}")

    def rename_column(self):
        selection = self.table_list.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a table first.")
            return

        # Get current columns from the treeview
        columns = self.data_tree["columns"]
        if not columns:
            messagebox.showwarning("Warning", "No columns found for the selected table.")
            return

        RenameColumnWindow(self, list(columns))

    def execute_rename_column(self, old_name, new_name):
        selection = self.table_list.curselection()
        if not selection:
            return
        table_name = self.table_list.get(selection[0])

        sql = f'ALTER TABLE "{table_name}" RENAME COLUMN "{old_name}" TO "{new_name}"'

        cursor = self.conn.cursor()
        try:
            cursor.execute(sql)
            self.conn.commit()
            self.show_table_data(None) # Refresh data view
            messagebox.showinfo("Success", f"Column '{old_name}' renamed to '{new_name}'.")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to rename column: {e}")

    def delete_column(self):
        selection = self.table_list.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a table first.")
            return

        columns = self.data_tree["columns"]
        if not columns:
            messagebox.showwarning("Warning", "No columns found for the selected table.")
            return

        DeleteColumnWindow(self, list(columns))

    def execute_delete_column(self, column_name):
        selection = self.table_list.curselection()
        if not selection:
            return
        table_name = self.table_list.get(selection[0])

        sql = f'ALTER TABLE "{table_name}" DROP COLUMN "{column_name}"'

        cursor = self.conn.cursor()
        try:
            cursor.execute(sql)
            self.conn.commit()
            self.show_table_data(None) # Refresh data view
            messagebox.showinfo("Success", f"Column '{column_name}' deleted from table '{table_name}'.")
        except sqlite3.Error as e:
            # Provide a more helpful error message if the command is not supported
            if "no such column" in str(e).lower():
                 messagebox.showerror("Error", f"Column '{column_name}' does not exist.")
            elif "near 'DROP'":
                 messagebox.showerror("Error", f"This version of SQLite may not support DROP COLUMN. Error: {e}")
            else:
                 messagebox.showerror("Error", f"Failed to delete column: {e}")

if __name__ == "__main__":
    app = SQLiteEditor()
    app.mainloop()

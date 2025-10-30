import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import csv
from datetime import datetime
import matplotlib.pyplot as plt

# ========================= Database Setup ==========================
conn = sqlite3.connect("portfolio.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS portfolio (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    category TEXT,
    quantity REAL,
    price REAL,
    date TEXT
)
""")
conn.commit()

# ========================= Functions ===============================
def add_investment():
    name = name_var.get()
    category = category_var.get()
    qty = quantity_var.get()
    price = price_var.get()
    date = date_var.get()

    if not (name and category and qty and price and date):
        messagebox.showwarning("Input Error", "All fields are required!")
        return

    cursor.execute("""
        INSERT INTO portfolio (name, category, quantity, price, date)
        VALUES (?, ?, ?, ?, ?)
    """, (name, category, qty, price, date))
    conn.commit()
    load_data()
    clear_fields()

def delete_investment():
    selected = tree.focus()
    if not selected:
        messagebox.showwarning("Delete Error", "Select an investment to delete!")
        return
    values = tree.item(selected, "values")
    cursor.execute("DELETE FROM portfolio WHERE id=?", (values[0],))
    conn.commit()
    load_data()

def update_investment():
    selected = tree.focus()
    if not selected:
        messagebox.showwarning("Update Error", "Select an investment to update!")
        return
    values = tree.item(selected, "values")
    cursor.execute("""
        UPDATE portfolio SET name=?, category=?, quantity=?, price=?, date=?
        WHERE id=?
    """, (name_var.get(), category_var.get(), quantity_var.get(), price_var.get(), date_var.get(), values[0]))
    conn.commit()
    load_data()
    clear_fields()

def load_data():
    for item in tree.get_children():
        tree.delete(item)
    cursor.execute("SELECT * FROM portfolio")
    for row in cursor.fetchall():
        tree.insert("", "end", values=row)
    update_summary()

def clear_fields():
    name_var.set("")
    category_var.set("Stocks")
    quantity_var.set("")
    price_var.set("")
    date_var.set(datetime.now().strftime("%Y-%m-%d"))

def update_summary():
    cursor.execute("SELECT SUM(quantity * price) FROM portfolio")
    total_value = cursor.fetchone()[0] or 0
    cursor.execute("SELECT COUNT(*) FROM portfolio")
    count = cursor.fetchone()[0]
    cursor.execute("SELECT AVG(price) FROM portfolio")
    avg_price = cursor.fetchone()[0] or 0

    summary_label.config(
        text=f"💰 Total: ₹{total_value:.2f}   |   📦 Assets: {count}   |   📊 Avg. Price: ₹{avg_price:.2f}"
    )

def search_data():
    query = search_var.get().lower()
    for item in tree.get_children():
        tree.delete(item)
    cursor.execute("SELECT * FROM portfolio WHERE LOWER(name) LIKE ? OR LOWER(category) LIKE ?", (f"%{query}%", f"%{query}%"))
    for row in cursor.fetchall():
        tree.insert("", "end", values=row)

def export_csv():
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files","*.csv")])
    if not file_path:
        return
    cursor.execute("SELECT * FROM portfolio")
    rows = cursor.fetchall()
    with open(file_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Name", "Category", "Quantity", "Price", "Date"])
        writer.writerows(rows)
    messagebox.showinfo("Export Successful", f"Data exported to {file_path}")

def show_chart():
    cursor.execute("SELECT category, SUM(quantity * price) FROM portfolio GROUP BY category")
    data = cursor.fetchall()
    if not data:
        messagebox.showinfo("No Data", "No data available for chart.")
        return

    categories, values = zip(*data)
    plt.figure(figsize=(6,6))
    plt.pie(values, labels=categories, autopct="%1.1f%%", startangle=90)
    plt.title("Portfolio Distribution by Category")
    plt.show()

# ========================= GUI Setup ===============================
root = tk.Tk()
root.title("💼 Portfolio Tracker")
root.geometry("900x600")
root.config(bg="#eef5ff")

# Variables
name_var = tk.StringVar()
category_var = tk.StringVar(value="Stocks")
quantity_var = tk.DoubleVar()
price_var = tk.DoubleVar()
date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
search_var = tk.StringVar()

# ========================= Top Section =============================
header = tk.Label(root, text="📈 Portfolio Tracker Dashboard", font=("Arial Rounded MT Bold", 18), bg="#007acc", fg="white", pady=10)
header.pack(fill="x")

# Search Bar
search_frame = tk.Frame(root, bg="#eef5ff")
search_frame.pack(pady=10)
tk.Label(search_frame, text="Search:", bg="#eef5ff", font=("Arial", 10, "bold")).pack(side="left")
tk.Entry(search_frame, textvariable=search_var, width=25).pack(side="left", padx=5)
ttk.Button(search_frame, text="🔍 Find", command=search_data).pack(side="left", padx=5)
ttk.Button(search_frame, text="🔄 Show All", command=load_data).pack(side="left")

# ========================= Form Frame =============================
form_frame = tk.LabelFrame(root, text="Add / Edit Investment", bg="#eef5ff", padx=10, pady=10, font=("Arial", 10, "bold"))
form_frame.pack(padx=10, pady=10, fill="x")

labels = ["Name:", "Category:", "Quantity:", "Price (₹):", "Date (YYYY-MM-DD):"]
for i, text in enumerate(labels):
    tk.Label(form_frame, text=text, bg="#eef5ff", font=("Arial", 10, "bold")).grid(row=i//2, column=(i%2)*2, padx=5, pady=5, sticky="e")

tk.Entry(form_frame, textvariable=name_var, width=25).grid(row=0, column=1, padx=5)
ttk.Combobox(form_frame, textvariable=category_var, values=["Stocks", "Crypto", "Mutual Funds", "Gold", "Real Estate"], width=23).grid(row=0, column=3)
tk.Entry(form_frame, textvariable=quantity_var, width=25).grid(row=1, column=1)
tk.Entry(form_frame, textvariable=price_var, width=25).grid(row=1, column=3)
tk.Entry(form_frame, textvariable=date_var, width=25).grid(row=2, column=1)

# Buttons
btn_frame = tk.Frame(root, bg="#eef5ff")
btn_frame.pack(pady=10)
ttk.Button(btn_frame, text="➕ Add", command=add_investment).grid(row=0, column=0, padx=5)
ttk.Button(btn_frame, text="✏️ Update", command=update_investment).grid(row=0, column=1, padx=5)
ttk.Button(btn_frame, text="❌ Delete", command=delete_investment).grid(row=0, column=2, padx=5)
ttk.Button(btn_frame, text="💾 Export CSV", command=export_csv).grid(row=0, column=3, padx=5)
ttk.Button(btn_frame, text="📊 Show Chart", command=show_chart).grid(row=0, column=4, padx=5)
ttk.Button(btn_frame, text="🧹 Clear", command=clear_fields).grid(row=0, column=5, padx=5)

# ========================= Table =============================
tree_frame = tk.Frame(root)
tree_frame.pack(pady=10, fill="x")

columns = ("ID", "Name", "Category", "Quantity", "Price", "Date")
tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=10)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, anchor="center", width=130)
tree.pack(fill="x")

# ========================= Summary =============================
summary_label = tk.Label(root, text="💰 Total: ₹0.00 | 📦 Assets: 0 | 📊 Avg. Price: ₹0.00", 
                         bg="#eef5ff", font=("Arial", 11, "bold"), fg="#007acc")
summary_label.pack(pady=10)

# Load existing data
load_data()

root.mainloop()

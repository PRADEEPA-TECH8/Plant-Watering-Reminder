import sqlite3
import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta

# Watering intervals (in days)
watering_intervals = {
    "Succulent": 7,
    "Flower": 3,
    "Vegetable": 2
}

# ------------------ Add Plant to Database ------------------ #
def add_plant():
    name = name_entry.get()
    plant_type = type_var.get()

    if name and plant_type:
        # Calculate the next watering date based on the plant type
        interval = watering_intervals.get(plant_type, 3)
        next_water_date = (datetime.now() + timedelta(days=interval)).date()

        # Insert the plant into the database with the next_water_date
        conn = sqlite3.connect('plants.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO plants (name, type, last_watered, next_water_date) VALUES (?, ?, date('now'), ?)", 
                       (name, plant_type, next_water_date))
        conn.commit()
        conn.close()

        # Show success message
        messagebox.showinfo("Success", f"{name} added with next watering date: {next_water_date}")
        name_entry.delete(0, tk.END)

        # Reload the plant names into the dropdown after adding a new plant
        load_plant_names()
    else:
        messagebox.showwarning("Input Error", "Please enter all fields.")

# ------------------ Show Plants That Need Watering ------------------ #
def show_due_plants():
    conn = sqlite3.connect('plants.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, type, last_watered, next_water_date FROM plants")
    plants = cursor.fetchall()
    conn.close()

    due_list = []

    for name, ptype, last_watered, next_water_date in plants:
        # Handle case where next_water_date is None
        if not next_water_date:
            continue

        interval = watering_intervals.get(ptype, 3)
        try:
            next_water_date = datetime.strptime(next_water_date, "%Y-%m-%d")
            if datetime.today().date() >= next_water_date.date():
                due_list.append(f"{name} ({ptype}) needs water today!")
        except ValueError:
            continue  # If there's an issue parsing the date, just skip the plant

    if due_list:
        messagebox.showinfo("Water Today", "\n".join(due_list))
    else:
        messagebox.showinfo("All Good 🌿", "No plants need watering today!")

# ------------------ Load Plant Names into Dropdown ------------------ #
def load_plant_names():
    conn = sqlite3.connect('plants.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM plants")
    names = [row[0] for row in cursor.fetchall()]
    conn.close()

    # Update the dropdown menu with plant names
    menu = plant_menu["menu"]
    menu.delete(0, "end")
    for name in names:
        menu.add_command(label=name, command=lambda value=name: selected_plant.set(value))

# ------------------ Water Now ------------------ #
def water_now():
    plant = selected_plant.get()
    if plant:
        conn = sqlite3.connect('plants.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE plants SET last_watered = date('now') WHERE name = ?", (plant,))
        # Update next_water_date after watering the plant
        cursor.execute("UPDATE plants SET next_water_date = date('now', '+? day') WHERE name = ?", 
                       (watering_intervals.get(selected_plant.get(), 3), plant))
        conn.commit()
        conn.close()
        messagebox.showinfo("Watered 💧", f"{plant} watered today!")
    else:
        messagebox.showwarning("Oops", "Please select a plant to water!")

# ------------------ GUI ------------------ #
root = tk.Tk()
root.title("🌱 Plant Watering Reminder")

# Add Plant Section
tk.Label(root, text="Plant Name:").grid(row=0, column=0, padx=10, pady=10)
name_entry = tk.Entry(root)
name_entry.grid(row=0, column=1)

tk.Label(root, text="Plant Type:").grid(row=1, column=0, padx=10, pady=10)
type_var = tk.StringVar()
type_options = ["Succulent", "Flower", "Vegetable"]
type_menu = tk.OptionMenu(root, type_var, *type_options)
type_menu.grid(row=1, column=1)

add_button = tk.Button(root, text="Add Plant", command=add_plant)
add_button.grid(row=2, columnspan=2, pady=10)

# Check Due Plants Button
check_button = tk.Button(root, text="🌧️ Check Who Needs Water", command=show_due_plants)
check_button.grid(row=3, columnspan=2, pady=5)

# Water Now Section
tk.Label(root, text="Water Now:").grid(row=4, column=0, padx=10, pady=5)
selected_plant = tk.StringVar()
plant_menu = tk.OptionMenu(root, selected_plant, "")
plant_menu.grid(row=4, column=1)

water_button = tk.Button(root, text="💧 Water Now", command=water_now)
water_button.grid(row=5, columnspan=2, pady=10)

# Load initial plant names into the dropdown
load_plant_names()

root.mainloop()





import sqlite3

# Connect to the database
conn = sqlite3.connect('plants.db')
cursor = conn.cursor()

# Check if the column already exists before adding it
cursor.execute("PRAGMA table_info(plants)")
columns = [column[1] for column in cursor.fetchall()]

if 'next_water_date' not in columns:
    cursor.execute("ALTER TABLE plants ADD COLUMN next_water_date TEXT")
    print("Column 'next_water_date' added successfully!")
else:
    print("Column 'next_water_date' already exists.")

# Commit and close the connection
conn.commit()
conn.close()


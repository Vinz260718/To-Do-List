import sqlite3

# Fungsi untuk membuat database dan tabel tugas jika belum ada
def create_db():
    conn = sqlite3.connect('tasks.db')  # Nama database
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task TEXT NOT NULL,
        time TEXT NOT NULL,
        status TEXT NOT NULL
    )''')
    
    conn.commit()
    conn.close()

create_db()  # Jalankan untuk membuat tabel saat pertama kali
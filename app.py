import sqlite3
from flask import Flask, request
import requests
import time

app = Flask(__name__)

# Token Bot Telegram
BOT_TOKEN = '8144985039:AAHEP1y_NYto3JQlF-eHtWvS9u5xkbidHgU'
TELEGRAM_API = f'https://api.telegram.org/bot{BOT_TOKEN}'

# Fungsi untuk menambahkan tugas baru ke database
def add_task_to_db(task, time):
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    
    cursor.execute('''INSERT INTO tasks (task, time, status) VALUES (?, ?, ?)''', 
                   (task, time, 'pending'))  # Status awalnya 'pending'
    
    conn.commit()
    conn.close()

# Fungsi untuk mengambil tugas yang statusnya 'pending'
def get_pending_tasks():
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    
    cursor.execute('''SELECT task, time FROM tasks WHERE status = 'pending' ''')
    tasks = cursor.fetchall()
    
    conn.close()
    return tasks

# Fungsi untuk mengubah status tugas menjadi 'completed'
def complete_task_in_db(task):
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    
    cursor.execute('''UPDATE tasks SET status = 'completed' WHERE task = ?''', (task,))
    
    conn.commit()
    conn.close()

# Fungsi untuk mengirimkan pesan ke Telegram
def send_message(chat_id, text):
    payload = {'chat_id': chat_id, 'text': text}
    requests.post(f'{TELEGRAM_API}/sendMessage', json=payload)

# Fungsi untuk mengirimkan reminder ke Telegram
def send_reminder(chat_id, task, time_str):
    emoji = get_emoji(task)
    message = f"*📌 Reminder Ulang* {emoji}\n\n**Tugas:** {task}\n**Waktu:** {time_str}\n\n⏰ Waktunya kembali fokus!"
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown',
        'reply_markup': {
            'inline_keyboard': [
                [
                    {'text': '✅ COMPLETED!', 'callback_data': f'completed|{task}'},
                    {'text': '⏰ JEDA 10 MENIT!', 'callback_data': f'delay|{task}|{time_str}'}
                ]
            ]
        }
    }
    requests.post(f'{TELEGRAM_API}/sendMessage', json=payload)

# Fungsi untuk mendapatkan emoji berdasarkan tugas
def get_emoji(text):
    lower = text.lower()
    if 'workout' in lower:
        return '💪'
    if 'meeting' in lower:
        return '📅'
    if 'study' in lower:
        return '📚'
    return '🔔'

# Route untuk halaman utama
@app.route('/')
def home():
    return 'Hello, World!'

# Webhook endpoint untuk Telegram
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    print(f"Data diterima: {data}")  # Log data yang diterima dari Telegram
    
    if 'message' in data:
        chat_id = data['message']['chat']['id']
        text = data['message'].get('text', '')
        
        if text == '/list':
            tasks = get_pending_tasks()
            if tasks:
                task_list = "\n".join([f"{task[0]} - {task[1]}" for task in tasks])
                send_message(chat_id, f"🔔 Tugas yang sedang berjalan:\n{task_list}")
            else:
                send_message(chat_id, "🔔 Tidak ada tugas yang sedang berjalan.")
        
        elif text.startswith('/add '):
            task_text = text[len('/add '):].strip()
            add_task_to_db(task_text, '09:00')  # Asumsi waktu default adalah 09:00
            send_message(chat_id, f"Tugas baru '{task_text}' berhasil ditambahkan!")

    elif 'callback_query' in data:
        callback_data = data['callback_query']['data']
        chat_id = data['callback_query']['message']['chat']['id']
        message_id = data['callback_query']['message']['message_id']
        
        if callback_data.startswith('completed'):
            task = callback_data.split('|')[1]
            complete_task_in_db(task)
            send_message(chat_id, f'✅ Tugas "{task}" telah diselesaikan!')
        elif callback_data.startswith('delay'):
            task = callback_data.split('|')[1]
            time_str = callback_data.split('|')[2]
            send_message(chat_id, f'⏳ Tugas "{task}" dijadwalkan ulang 10 menit lagi.')
            # Menjadwalkan ulang pengingat dalam 10 menit
            time.sleep(600)  # Simulasikan delay 10 menit
            send_reminder(chat_id, task, time_str)

    return '', 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
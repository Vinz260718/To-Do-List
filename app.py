from flask import Flask, request
import requests
import time

app = Flask(__name__)

# Token Bot Telegram
BOT_TOKEN = '8144985039:AAHEP1y_NYto3JQlF-eHtWvS9u5xkbidHgU'
TELEGRAM_API = f'https://api.telegram.org/bot{BOT_TOKEN}'

# Daftar tugas yang sedang berjalan
tasks = []

# Route untuk halaman utama
@app.route('/')
def home():
    return 'Hello, World!'

# Webhook endpoint untuk Telegram
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    print(f"Data diterima: {data}")  # Log data yang diterima dari Telegram
    
    if 'callback_query' in data:
        callback_data = data['callback_query']['data']
        chat_id = data['callback_query']['message']['chat']['id']
        message_id = data['callback_query']['message']['message_id']
        
        if callback_data.startswith('completed'):
            task = callback_data.split('|')[1]
            send_message(chat_id, f'✅ Tugas "{task}" telah diselesaikan!')
            remove_task(task)  # Hapus tugas setelah selesai
        elif callback_data.startswith('delay'):
            task = callback_data.split('|')[1]
            time_str = callback_data.split('|')[2]
            send_message(chat_id, f'⏳ Tugas "{task}" dijadwalkan ulang 10 menit lagi.')
            # Menjadwalkan ulang pengingat dalam 10 menit
            time.sleep(600)  # Simulasikan delay 10 detik (ganti dengan 600 untuk 10 menit)
            send_reminder(chat_id, task, time_str)
    
    return '', 200

@app.route('/list', methods=['GET'])
def list_tasks():
    if len(tasks) == 0:
        return "🔔 Tidak ada tugas yang sedang berjalan."
    
    task_list = "\n".join([f"**{task['text']}** - {task['time']}" for task in tasks])
    return f"🔔 Daftar Tugas yang sedang berjalan:\n\n{task_list}"

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

def send_message(chat_id, text):
    payload = {'chat_id': chat_id, 'text': text}
    requests.post(f'{TELEGRAM_API}/sendMessage', json=payload)

def get_emoji(text):
    lower = text.lower()
    if 'workout' in lower:
        return '💪'
    if 'meeting' in lower:
        return '📅'
    if 'study' in lower:
        return '📚'
    return '🔔'

def add_task(text, time_str):
    task = {"text": text, "time": time_str}
    tasks.append(task)  # Menambahkan task ke list tasks
    return task

def remove_task(task_text):
    global tasks
    tasks = [task for task in tasks if task['text'] != task_text]  # Hapus tugas yang sudah diselesaikan

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
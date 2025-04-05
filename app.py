from flask import Flask, request
import requests
import time

app = Flask(__name__)

# Token Bot Telegram
BOT_TOKEN = '8144985039:AAHEP1y_NYto3JQlF-eHtWvS9u5xkbidHgU'
TELEGRAM_API = f'https://api.telegram.org/bot{BOT_TOKEN}'

# Menyimpan tugas yang sedang berjalan
active_tasks = []

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
        text = data['message'].get('text', '')
        chat_id = data['message']['chat']['id']

        # Perintah /list untuk menampilkan tugas yang sedang berjalan
        if text.startswith('/list'):
            send_task_list(chat_id)
        
        # Perintah /add untuk menambahkan tugas
        elif text.startswith('/add'):
            task = text.replace('/add ', '').strip()
            if task:
                add_task(task, chat_id)
                send_message(chat_id, f"Tugas '{task}' telah ditambahkan!")
            else:
                send_message(chat_id, "❗ Masukkan tugas setelah /add.")

    if 'callback_query' in data:
        callback_data = data['callback_query']['data']
        chat_id = data['callback_query']['message']['chat']['id']
        message_id = data['callback_query']['message']['message_id']
        
        if callback_data.startswith('completed'):
            task = callback_data.split('|')[1]
            send_message(chat_id, f'✅ Tugas "{task}" telah diselesaikan!')
            active_tasks.remove(task)  # Hapus task yang selesai
        elif callback_data.startswith('delay'):
            task = callback_data.split('|')[1]
            time_str = callback_data.split('|')[2]
            send_message(chat_id, f'⏳ Tugas "{task}" dijadwalkan ulang 10 menit lagi.')
            # Menjadwalkan ulang pengingat dalam 10 menit
            time.sleep(600)  # Simulasikan delay 10 menit
            send_reminder(chat_id, task, time_str)

    return '', 200

def add_task(task, chat_id):
    # Menambahkan tugas ke daftar active_tasks
    active_tasks.append(task)

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

def send_task_list(chat_id):
    if not active_tasks:
        send_message(chat_id, "🔔 Tidak ada tugas yang sedang berjalan.")
    else:
        task_list = "\n".join([f"📋 {task}" for task in active_tasks])
        send_message(chat_id, f"📝 Daftar Tugas yang Sedang Berjalan:\n{task_list}")

def get_emoji(text):
    lower = text.lower()
    if 'workout' in lower:
        return '💪'
    if 'meeting' in lower:
        return '📅'
    if 'study' in lower:
        return '📚'
    return '🔔'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
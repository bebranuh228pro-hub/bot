import requests
import json
import time
import random
from datetime import datetime, timedelta

TOKEN = "8381452796:AAHWqDk26Q3RYfad4nyzIiE79gu8GyGRFsY"

premium_users = {}
pro_users = {}
subscriptions = {}
scam_database = {
    "scammer123": "Мошенник - обман с предоплатой",
    "fake_seller": "Фейковый продавец аккаунтов", 
}
scripts_database = {
    "🎮 Blox Fruits": {"price": 300, "code": "loadstring(game:HttpGet('https://raw.githubusercontent.com/bloxfruit/script/main/loader.lua'))()"},
    "🔫 Arsenal": {"price": 200, "code": "loadstring(game:HttpGet('https://raw.githubusercontent.com/arsenal/script/main/loader.lua'))()"},
}

premium_scripts = {
    "🔥 Premium Script 1": "loadstring(game:HttpGet('https://premium-scripts.com/1.lua'))()",
    "⚡ Premium Script 2": "loadstring(game:HttpGet('https://premium-scripts.com/2.lua'))()",
    "🎯 Premium Script 3": "loadstring(game:HttpGet('https://premium-scripts.com/3.lua'))()",
    "💎 Premium Script 4": "loadstring(game:HttpGet('https://premium-scripts.com/4.lua'))()",
    "🚀 Premium Script 5": "loadstring(game:HttpGet('https://premium-scripts.com/5.lua'))()",
}

name_history_db = {
    "username123": ["oldname_2022", "newname_2023", "currentname"],
    "user456": ["original", "updated_2024"],
    "premium_user": ["start_name", "middle_name", "current_premium"],
    "pro_user": ["pro_original", "pro_updated_2024"],
}

gift_history_db = {
    "username123": [
        {"date": "2024-01-15", "gift": "🎁 Premium Star", "from": "friend_user"},
        {"date": "2024-02-20", "gift": "⭐ Super Gift", "from": "admin"}
    ],
    "premium_user": [
        {"date": "2024-01-10", "gift": "🎨 Rare NFT #1234", "from": "gift_bot"},
        {"date": "2024-03-05", "gift": "👾 CryptoPunk #5678", "from": "nft_giver"}
    ],
}

ton_spent_db = {
    "username123": 45.50,
    "premium_user": 120.75,
    "pro_user": 356.20,
    "rich_user": 1200.00,
}

purchased_gifts_db = {
    "username123": [
        {"date": "2024-01-10", "gift": "🎁 Premium Pack", "price": "1500⭐"},
        {"date": "2024-02-15", "gift": "⭐ Star Bundle", "price": "2500⭐"}
    ],
    "premium_user": [
        {"date": "2024-01-05", "gift": "💎 Diamond Box", "price": "5000⭐"},
        {"date": "2024-03-01", "gift": "🚀 Rocket Pack", "price": "7500⭐"}
    ],
}

cities = ["Москва", "Санкт-Петербург", "Новосибирск", "Екатеринбург", "Казань", "Нижний Новгород", "Челябинск", "Самара", "Омск", "Ростов-на-Дону", "Уфа", "Красноярск", "Воронеж", "Пермь", "Волгоград"]
devices = ["📱 Android", "📱 iPhone", "💻 PC", "💻 Mac", "📱 iPad", "💻 Linux", "📱 Windows Phone"]

last_update_id = 0
processed_updates = set()
last_hourly_alert = 0
last_90min_alert = 0
last_2hour_alert = 0
last_saturday_alert = 0
donation_amounts = {}
spin_balances = {}
admin_users = set()
admin_usernames = {}
user_activity = set()
spin_bets = {}
user_states = {}
admin_contact_mode = {}

def send_message(chat_id, text, reply_markup=None):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)
    try:
        result = requests.post(url, data=data, timeout=10)
        return result
    except:
        return None

def get_updates():
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last_update_id + 1}"
    try:
        response = requests.get(url, timeout=10)
        return response.json().get("result", [])
    except:
        return []

def get_user_info(user_id):
    url = f"https://api.telegram.org/bot{TOKEN}/getChat?chat_id={user_id}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json().get("result", {})
    except:
        pass
    return {}

def main_menu(chat_id):
    keyboard = [
        [{"text": "🔍 ПОИСК"}, {"text": "🛡️ ПРОВЕРКА ЧАТА"}],
        [{"text": "🎰 СПИН"}, {"text": "🎮 СКРИПТЫ"}],
        [{"text": "💳 ПОДПИСКИ"}, {"text": "❤️ ДОНАТ"}],
    ]
    
    if has_premium_access(chat_id) or has_pro_access(chat_id):
        keyboard.append([{"text": "💎 ПРЕМИУМ"}, {"text": "🚀 PRO"}])
    
    keyboard.append([{"text": "📞 ОТВЕТ АДМИНАМ"}])
    keyboard.append([{"text": "❓ ПОМОЩЬ"}])
    
    if chat_id in admin_users:
        keyboard.append([{"text": "⚙️ АДМИН ПАНЕЛЬ"}])
    
    return {"keyboard": keyboard, "resize_keyboard": True}

def spin_menu():
    keyboard = [
        [{"text": "💰 БАЛАНС"}, {"text": "🎰 КРУТИТЬ"}],
        [{"text": "💸 ВЫВОД"}, {"text": "🔙 НАЗАД"}]
    ]
    return {"keyboard": keyboard, "resize_keyboard": True}

def spin_bet_menu():
    keyboard = [
        [{"text": "500⭐"}, {"text": "1000⭐"}],
        [{"text": "1500⭐"}, {"text": "2000⭐"}],
        [{"text": "🎯 МОЯ СТАВКА"}],
        [{"text": "🔙 НАЗАД"}]
    ]
    return {"keyboard": keyboard, "resize_keyboard": True}

def admin_menu():
    keyboard = [
        [{"text": "📊 СТАТИСТИКА"}, {"text": "👥 ПОЛЬЗОВАТЕЛИ"}],
        [{"text": "📢 ОПОВЕЩЕНИЯ"}, {"text": "⭐ ЗВЕЗДЫ"}],
        [{"text": "👑 АДМИНЫ"}, {"text": "💎 УСТАНОВИТЬ ПОДПИСКУ"}],
        [{"text": "🔙 НАЗАД"}]
    ]
    return {"keyboard": keyboard, "resize_keyboard": True}

def scripts_menu(chat_id):
    keyboard = []
    
    if has_premium_access(chat_id) or has_pro_access(chat_id):
        for script_name in premium_scripts.keys():
            keyboard.append([{"text": f"{script_name} 🎁"}])
    
    for script_name in scripts_database.keys():
        keyboard.append([{"text": f"{script_name} - {scripts_database[script_name]['price']}⭐"}])
    
    keyboard.append([{"text": "🔙 НАЗАД"}])
    return {"keyboard": keyboard, "resize_keyboard": True}

def subscriptions_menu():
    keyboard = [
        [{"text": "💎 10Д ПРЕМИУМ - 300⭐"}, {"text": "🚀 10Д PRO - 400⭐"}],
        [{"text": "💎 МЕСЯЦ ПРЕМИУМ - 400⭐"}, {"text": "🚀 МЕСЯЦ PRO - 500⭐"}],
        [{"text": "💎 ГОД ПРЕМИУМ - 500⭐"}, {"text": "🚀 ГОД PRO - 600⭐"}],
        [{"text": "💎 НАВСЕГДА ПРЕМИУМ - 1500⭐"}, {"text": "🚀 НАВСЕГДА PRO - 3000⭐"}],
        [{"text": "🔙 НАЗАД"}]
    ]
    return {"keyboard": keyboard, "resize_keyboard": True}

def help_menu():
    keyboard = [
        [{"text": "📞 Поддержка"}, {"text": "❓ FAQ"}],
        [{"text": "💎 О подписках"}, {"text": "🔙 НАЗАД"}]
    ]
    return {"keyboard": keyboard, "resize_keyboard": True}

def has_premium_access(chat_id):
    if chat_id in premium_users:
        return True
    if chat_id in subscriptions:
        sub = subscriptions[chat_id]
        if sub["type"] == "premium" and sub["expires"] > time.time():
            return True
    return False

def has_pro_access(chat_id):
    if chat_id in pro_users:
        return True
    if chat_id in subscriptions:
        sub = subscriptions[chat_id]
        if sub["type"] == "pro" and sub["expires"] > time.time():
            return True
    return False

def get_real_user_info(username):
    try:
        username = username.replace('@', '').strip()
        tg_url = f"https://t.me/{username}"
        
        response = requests.head(tg_url, timeout=5)
        if response.status_code != 200:
            return None
        
        tg_info = get_telegram_info(username)
        return tg_info
        
    except:
        return None

def get_telegram_info(username):
    try:
        tg_url = f"https://t.me/{username}"
        
        response = requests.head(tg_url, timeout=5)
        exists = response.status_code == 200
        
        if not exists:
            return None
            
        join_date = f"202{random.randint(1,3)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
        last_seen = random.choice(['только что', '5 минут назад', '1 час назад', 'вчера'])
        daily_time = f"{random.randint(1, 8)}ч {random.randint(1, 59)}м"
        city = random.choice(cities)
        device = random.choice(devices)
        
        name_history = name_history_db.get(username, [username])
        gift_history = gift_history_db.get(username, [])
        purchased_gifts = purchased_gifts_db.get(username, [])
        ton_spent = ton_spent_db.get(username, random.uniform(5.0, 150.0))
        
        return {
            'exists': True,
            'username': username,
            'profile_url': tg_url,
            'join_date': join_date,
            'last_seen': last_seen,
            'daily_time': daily_time,
            'city': city,
            'device': device,
            'scam_status': scam_database.get(username, "✅ Чистый"),
            'risk_level': random.choice(["Низкий", "Средний", "Высокий"]),
            'reputation': random.randint(1, 100),
            'name_history': name_history,
            'gift_history': gift_history,
            'purchased_gifts': purchased_gifts,
            'ton_spent': ton_spent
        }
    except:
        return None

def check_chat_security(chat_link):
    try:
        chat_link = chat_link.replace('https://t.me/', '').replace('@', '')
        
        bots_count = random.randint(1, 5)
        admin_count = random.randint(2, 8)
        security_level = random.choice(["Слабый", "Средний", "Сильный"])
        
        return {
            'bots_count': bots_count,
            'admin_count': admin_count,
            'security_level': security_level,
            'link_restrictions': random.choice([True, False]),
            'anti_spam': random.choice([True, False]),
            'member_count': random.randint(100, 50000)
        }
    except:
        return None

def send_invoice(chat_id, amount, payload, title, description):
    invoice_url = f"https://api.telegram.org/bot{TOKEN}/sendInvoice"
    invoice_data = {
        "chat_id": chat_id,
        "title": title,
        "description": description,
        "payload": payload,
        "provider_token": "STARS",
        "currency": "XTR",
        "prices": json.dumps([{"label": "Stars", "amount": amount}])
    }
    try:
        requests.post(invoice_url, data=invoice_data, timeout=10)
    except:
        pass

def activate_subscription(chat_id, sub_type, duration_days):
    expires = time.time() + (duration_days * 24 * 60 * 60)
    subscriptions[chat_id] = {
        "type": sub_type,
        "expires": expires
    }

def send_broadcast_message(message):
    all_users = user_activity.copy()
    success_count = 0
    for user_id in all_users:
        try:
            result = send_message(user_id, message)
            if result and result.status_code == 200:
                success_count += 1
            time.sleep(0.05)
        except:
            pass
    return success_count

def check_scheduled_alerts():
    global last_hourly_alert, last_90min_alert, last_2hour_alert, last_saturday_alert
    
    current_time = time.time()
    now = datetime.now()
    
    if now.minute == 0 and current_time - last_hourly_alert >= 3500:
        last_hourly_alert = current_time
        message = "🎣 <b>STEAL A BRAINROT</b> 🎮\n🏆 Начался ивент: <b>РЫБАЛКА</b> ✅"
        send_broadcast_message(message)
    
    if now.minute == 30 and now.hour % 2 == 1 and current_time - last_90min_alert >= 5300:
        last_90min_alert = current_time
        message = "☢️ <b>STEAL A BRAINROT</b> 🎮\n🏆 Начался ивент: <b>РАДИАЦИЯ</b> ⚡"
        send_broadcast_message(message)
    
    if now.minute == 0 and now.hour % 2 == 0 and current_time - last_2hour_alert >= 7100:
        last_2hour_alert = current_time
        message = "🎣☢️ <b>STEAL A BRAINROT</b> 🎮\n🏆 Начались ивенты: <b>РЫБАЛКА + РАДИАЦИЯ</b> 🎯"
        send_broadcast_message(message)
    
    if now.weekday() == 5 and now.hour == 23 and now.minute == 0 and current_time - last_saturday_alert >= 3600:
        last_saturday_alert = current_time
        message = "🎁 <b>STEAL A BRAINROT</b> 🧠\n🏆 АДМИН РАЗДАЕТ РАННИЕ ПОДАРКИ 🎉"
        send_broadcast_message(message)
    
    if now.weekday() == 5 and now.hour == 0 and now.minute == 0 and current_time - last_saturday_alert >= 3600:
        last_saturday_alert = current_time
        message = "⚡ <b>STEAL A BRAINROT</b> 🧠\n🏆 НАЧАЛСЯ АДМИН АБЬЮЗ 🎯"
        send_broadcast_message(message)

def process_spin(chat_id, bet_amount):
    if chat_id not in spin_balances:
        spin_balances[chat_id] = 0
    
    if spin_balances[chat_id] < bet_amount:
        return f"❌ <b>НЕДОСТАТОЧНО СРЕДСТВ!</b>\n\n💰 Ваш баланс: {spin_balances[chat_id]}⭐\n💸 Нужно: {bet_amount}⭐"
    
    spin_balances[chat_id] -= bet_amount
    
    symbols = ["🍒", "🍋", "🍊", "🍇", "🔔", "⭐", "💎", "7️⃣"]
    result = [random.choice(symbols) for _ in range(3)]
    
    win_multiplier = 0
    if result[0] == result[1] == result[2]:
        if result[0] == "7️⃣":
            win_multiplier = 10
        elif result[0] == "💎":
            win_multiplier = 5
        elif result[0] == "⭐":
            win_multiplier = 3
        else:
            win_multiplier = 2
    
    win_amount = bet_amount * win_multiplier
    
    if win_multiplier > 0:
        spin_balances[chat_id] += win_amount
        return f"""🎰 <b>РЕЗУЛЬТАТ СПИНА:</b>

{' | '.join(result)}

🎉 <b>ВЫ ВЫИГРАЛИ {win_amount}⭐!</b>
💰 Множитель: x{win_multiplier}
💎 Баланс: {spin_balances[chat_id]}⭐"""
    else:
        return f"""🎰 <b>РЕЗУЛЬТАТ СПИНА:</b>

{' | '.join(result)}

😔 <b>ПОВЕЗЕТ В СЛЕДУЮЩИЙ РАЗ!</b>
💎 Баланс: {spin_balances[chat_id]}⭐"""

print("🕵️ Бот запущен...")

while True:
    try:
        check_scheduled_alerts()
        
        updates = get_updates()
        for update in updates:
            update_id = update["update_id"]
            
            if update_id in processed_updates:
                continue
                
            processed_updates.add(update_id)
            last_update_id = update_id

            if "message" not in update:
                continue
                
            chat_id = update["message"]["chat"]["id"]
            user_activity.add(chat_id)
            text = update["message"].get("text", "").strip()
            
            current_state = user_states.get(chat_id, "menu")
            
            if text == "/start":
                user_states[chat_id] = "menu"
                welcome_msg = """🎮 <b>ДОБРО ПОЖАЛОВАТЬ В МЕГА ХАБ!</b> 🏆

✨ <b>Возможности бота:</b>
• 🔍 Поиск информации о пользователях
• 🛡️ Проверка безопасности чатов  
• 🎮 Скрипты для игр
• 🎰 Игровой автомат с выводом
• 💎 Премиум и PRO подписки
• ❤️ Поддержка разработчиков

⚡ <i>И многое другое!</i>

🎯 <b>В этом ТГ канале:</b> 
<a href="https://t.me/YtM1xaILL_Info_bot_news">https://t.me/YtM1xaILL_Info_bot_news</a>

💫 <b>РЕГУЛЯРНО раздают:</b>
✨ Подписки ПРЕМИУМ/PRO 
👑 Назначают АДМИНОВ 
⭐ Раздают ЗВЕЗДЫ 
🎁 И много других подарков!

🚀 <i>Не упусти свой шанс!</i> 💎"""
                send_message(chat_id, welcome_msg, main_menu(chat_id))
            
            elif text == "АДМИНВХАТЕХАКЕРВРЕКАХАБОБА12345":
                admin_users.add(chat_id)
                user_info = get_user_info(chat_id)
                username = user_info.get('username', f'user_{chat_id}')
                admin_usernames[chat_id] = username
                user_states[chat_id] = "menu"
                send_message(chat_id, "⚡ <b>АДМИН ПАНЕЛЬ АКТИВИРОВАНА!</b> 👑", main_menu(chat_id))
            
            elif text == "ПЛЮСПРЕМКА":
                premium_users[chat_id] = True
                yandex_disk_link = "https://disk.yandex.ru/d/SNy2CcLBBAVomw"
                send_message(chat_id, f"💎 <b>ПРЕМИУМ ПОДПИСКА АКТИВИРОВАНА НАВСЕГДА!</b> 🎉\n\n📂 <b>Доступ к 100+ скриптам:</b>\n{yandex_disk_link}\n\n✨ Теперь вам доступны все премиум скрипты!", main_menu(chat_id))
            
            elif text == "ПЛЮСПРОПОДПИСОЧКА":
                pro_users[chat_id] = True
                if chat_id not in spin_balances:
                    spin_balances[chat_id] = 0
                spin_balances[chat_id] += 10000
                funpay_link = "https://funpay.com/users/16978665/"
                send_message(chat_id, f"🎖️ <b>PRO ПОДПИСКА АКТИВИРОВАНА!</b> 💵\n\nДля вас доступен премиальный магазин со скриптами и услугами:\n{funpay_link}\n\n💰✅ <b>+10000⭐ на ваш баланс!</b>\n💎 Теперь ваш баланс: {spin_balances[chat_id]}⭐", main_menu(chat_id))
            
            elif text == "💎 ПРЕМИУМ" and (has_premium_access(chat_id) or has_pro_access(chat_id)):
                if has_premium_access(chat_id):
                    yandex_disk_link = "https://disk.yandex.ru/d/SNy2CcLBBAVomw"
                    premium_info = f"""💎 <b>ВОЗМОЖНОСТИ ПРЕМИУМ ПОДПИСКИ:</b>

✨ <b>Доступ к эксклюзивным функциям:</b>
• 100+ премиум скриптов
• Расширенный поиск пользователей
• Приоритетная поддержка
• Премиум скрипты в меню

📂 <b>Яндекс-диск со скриптами:</b>
{yandex_disk_link}

🎁 <b>Дополнительные возможности:</b>
• NFT подарки в поиске
• Расширенная статистика
• Эксклюзивный контент"""
                else:
                    premium_info = """💎 <b>ПРЕМИУМ ПОДПИСКА</b>

✨ <b>Будут доступны эксклюзивные функции:</b>
• 100+ премиум скриптов
• Расширенный поиск пользователей
• Приоритетная поддержка
• Премиум скрипты в меню

🎁 <b>Дополнительные возможности:</b>
• NFT подарки в поиске
• Расширенная статистика
• Эксклюзивный контент

💫 <i>Приобретите подписку чтобы получить доступ</i> 🔓"""
                
                send_message(chat_id, premium_info, main_menu(chat_id))
            
            elif text == "🚀 PRO" and (has_pro_access(chat_id) or has_premium_access(chat_id)):
                if has_pro_access(chat_id):
                    funpay_link = "https://funpay.com/users/16978665/"
                    pro_info = f"""🚀 <b>ВОЗМОЖНОСТИ PRO ПОДПИСКИ:</b>

🎖️ <b>Максимальный доступ ко всем функциям:</b>
• Все возможности Премиум
• PRO эксклюзивные скрипты
• Полная история смен юзернеймов
• Реальные данные о потраченных TON
• Персональная поддержка

🛒 <b>Премиальный магазин:</b>
{funpay_link}

💰 <b>Бонусы:</b>
• +10000⭐ на баланс при активации
• Ранний доступ к новым функциям
• VIP статус в сообществе"""
                else:
                    pro_info = """🚀 <b>PRO ПОДПИСКА</b>

🎖️ <b>Будут доступны максимальные возможности:</b>
• Все функции Премиум
• PRO эксклюзивные скрипты
• Полная история смен юзернеймов
• Реальные данные о потраченных TON
• Персональная поддержка

💰 <b>Бонусы:</b>
• +10000⭐ на баланс при активации
• Ранний доступ к новым функциям
• VIP статус в сообществе

💫 <i>Приобретите подписку чтобы получить доступ</i> 🔓"""
                
                send_message(chat_id, pro_info, main_menu(chat_id))
            
            elif text == "📞 ОТВЕТ АДМИНАМ":
                admin_contact_mode[chat_id] = True
                send_message(chat_id, "📞 <b>НАПИШИТЕ СООБЩЕНИЕ АДМИНАМ:</b>\n\nВаше сообщение будет отправлено всем администраторам бота 💬")
            
            elif chat_id in admin_contact_mode and admin_contact_mode[chat_id]:
                if text != "📞 ОТВЕТ АДМИНАМ":
                    message_to_admins = f"📩 <b>СООБЩЕНИЕ ОТ ПОЛЬЗОВАТЕЛЯ:</b>\nID: {chat_id}\n\n{text}"
                    admin_count = 0
                    for admin_id in admin_users:
                        try:
                            send_message(admin_id, message_to_admins)
                            admin_count += 1
                            time.sleep(0.1)
                        except:
                            pass
                    send_message(chat_id, f"✅ <b>СООБЩЕНИЕ ОТПРАВЛЕНО {admin_count} АДМИНИСТРАТОРАМ!</b> 📨", main_menu(chat_id))
                    admin_contact_mode[chat_id] = False
            
            elif text == "🔍 ПОИСК":
                user_states[chat_id] = "waiting_username"
                send_message(chat_id, "🔍 <b>ОТПРАВЬТЕ ЮЗЕРНЕЙМ:</b>\n\nПример: @username 👤")
            
            elif text == "🛡️ ПРОВЕРКА ЧАТА":
                user_states[chat_id] = "waiting_chat_link"
                send_message(chat_id, "🛡️ <b>ОТПРАВЬТЕ ССЫЛКУ НА ЧАТ:</b>\n\nПример: @chatname или https://t.me/chatname 💬")
            
            elif text == "🎮 СКРИПТЫ":
                user_states[chat_id] = "scripts_menu"
                send_message(chat_id, "🎮 <b>ВЫБЕРИТЕ СКРИПТ:</b> 🕹️", scripts_menu(chat_id))
            
            elif text == "💎 ПОДПИСКИ" or text == "💳 ПОДПИСКИ":
                user_states[chat_id] = "subscriptions_menu"
                send_message(chat_id, "💎 <b>ВЫБЕРИТЕ ПОДПИСКУ:</b> 👑", subscriptions_menu())
            
            elif text == "🎰 СПИН":
                user_states[chat_id] = "spin_menu"
                send_message(chat_id, "🎰 <b>АВТОМАТ УДАЧИ!</b> 🎯\n\nВыберите действие 👇", spin_menu())
            
            elif text == "💰 БАЛАНС" and user_states.get(chat_id) == "spin_menu":
                balance = spin_balances.get(chat_id, 0)
                send_message(chat_id, f"💰 <b>ВАШ БАЛАНС:</b> {balance}⭐ 💎", spin_menu())
            
            elif text == "🎰 КРУТИТЬ" and user_states.get(chat_id) == "spin_menu":
                user_states[chat_id] = "waiting_spin_bet"
                send_message(chat_id, "🎯 <b>ВЫБЕРИТЕ СТАВКУ:</b> ⭐", spin_bet_menu())
            
            elif text == "🎯 МОЯ СТАВКА" and user_states.get(chat_id) == "waiting_spin_bet":
                user_states[chat_id] = "waiting_custom_bet"
                send_message(chat_id, "🎯 <b>НАПИШИТЕ СУММУ ДЛЯ СТАВКИ:</b>\n\nВведите число - сколько звезд хотите поставить: ⭐")
            
            elif user_states.get(chat_id) == "waiting_custom_bet" and text.isdigit():
                bet_amount = int(text)
                if bet_amount <= 0:
                    send_message(chat_id, "❌ <b>СТАВКА ДОЛЖНА БЫТЬ БОЛЬШЕ 0!</b> ⚠️", spin_bet_menu())
                    user_states[chat_id] = "waiting_spin_bet"
                    continue
                    
                if chat_id not in spin_balances:
                    spin_balances[chat_id] = 0
                
                if spin_balances[chat_id] >= bet_amount:
                    spin_result = process_spin(chat_id, bet_amount)
                    user_states[chat_id] = "spin_menu"
                    send_message(chat_id, spin_result, spin_menu())
                else:
                    send_message(chat_id, f"❌ <b>НЕДОСТАТОЧНО СРЕДСТВ!</b>\n\n💰 Ваш баланс: {spin_balances[chat_id]}⭐\n💸 Нужно: {bet_amount}⭐", spin_bet_menu())
                    user_states[chat_id] = "waiting_spin_bet"
            
            elif text == "💸 ВЫВОД" and user_states.get(chat_id) == "spin_menu":
                send_message(chat_id, "💸 <b>ВЫВОД СРЕДСТВ</b>\n\n📞 Напишите @DontWarryImTheStrongest\n\n⚠️ <b>ВЫВОД ОТ 50000⭐!</b> 💰", spin_menu())
            
            elif text in ["500⭐", "1000⭐", "1500⭐", "2000⭐"] and user_states.get(chat_id) == "waiting_spin_bet":
                bet_amount = int(text.replace("⭐", ""))
                if chat_id not in spin_balances:
                    spin_balances[chat_id] = 0
                
                if spin_balances[chat_id] >= bet_amount:
                    spin_result = process_spin(chat_id, bet_amount)
                    user_states[chat_id] = "spin_menu"
                    send_message(chat_id, spin_result, spin_menu())
                else:
                    send_message(chat_id, f"❌ <b>НЕДОСТАТОЧНО СРЕДСТВ!</b>\n\n💰 Ваш баланс: {spin_balances[chat_id]}⭐\n💸 Нужно: {bet_amount}⭐", spin_bet_menu())
            
            elif text == "⚙️ АДМИН ПАНЕЛЬ" and chat_id in admin_users:
                user_states[chat_id] = "admin_menu"
                send_message(chat_id, "⚙️ <b>АДМИН ПАНЕЛЬ</b> 👑", admin_menu())
            
            elif text == "📊 СТАТИСТИКА" and chat_id in admin_users and user_states.get(chat_id) == "admin_menu":
                user_list = list(user_activity)[:10]
                users_with_info = []
                for user_id in user_list:
                    user_info = get_user_info(user_id)
                    username = user_info.get('username', f'user_{user_id}')
                    users_with_info.append(f"• ID: {user_id} | @{username}")
                
                users_display = "\n".join(users_with_info) if users_with_info else "• Нет активных пользователей"
                
                stats = f"""📊 <b>СТАТИСТИКА БОТА</b> 👑

👥 Всего пользователей: {len(user_activity)}
⭐ Премиум: {len(premium_users)}
🚀 PRO: {len(pro_users)}
🎰 Игроков в спин: {len(spin_balances)}
💎 Всего звезд в обороте: {sum(spin_balances.values())}

👤 <b>Последние пользователи:</b>
{users_display}

📈 <i>Активная статистика</i> 📊"""
                send_message(chat_id, stats, admin_menu())
            
            elif text == "👥 ПОЛЬЗОВАТЕЛИ" and chat_id in admin_users and user_states.get(chat_id) == "admin_menu":
                user_list = list(user_activity)[:15]
                users_with_info = []
                for user_id in user_list:
                    user_info = get_user_info(user_id)
                    username = user_info.get('username', f'user_{user_id}')
                    users_with_info.append(f"• ID: {user_id} | @{username}")
                
                users_display = "\n".join(users_with_info) if users_with_info else "• Нет активных пользователей"
                
                send_message(chat_id, f"👥 <b>ПОСЛЕДНИЕ ПОЛЬЗОВАТЕЛИ:</b>\n\n{users_display}\n\n📋 <i>Всего: {len(user_activity)}</i>", admin_menu())
            
            elif text == "👑 АДМИНЫ" and chat_id in admin_users and user_states.get(chat_id) == "admin_menu":
                admins_list = []
                for admin_id, username in admin_usernames.items():
                    admins_list.append(f"• ID: {admin_id} | @{username}")
                
                admins_display = "\n".join(admins_list) if admins_list else "• Нет администраторов"
                
                admin_info = f"""👑 <b>СПИСОК АДМИНИСТРАТОРОВ:</b>

{admins_display}

⚡ <b>Команды управления:</b>
• <code>ID_пользователя назначить</code> - добавить админа
• <code>ID_пользователя снять</code> - удалить админа

💫 <i>Только владелец может управлять админами</i> 👑"""
                send_message(chat_id, admin_info, admin_menu())
            
            elif text.endswith("назначить") and chat_id in admin_users:
                try:
                    user_id = int(text.replace(" назначить", "").strip())
                    user_info = get_user_info(user_id)
                    if user_info:
                        username = user_info.get('username', f'user_{user_id}')
                        admin_users.add(user_id)
                        admin_usernames[user_id] = username
                        send_message(chat_id, f"✅ <b>АДМИН ДОБАВЛЕН!</b> 👑\n\nПользователь ID: {user_id} (@{username}) теперь администратор 🎉", admin_menu())
                    else:
                        send_message(chat_id, "❌ <b>ПОЛЬЗОВАТЕЛЬ НЕ НАЙДЕН!</b> ⚠️", admin_menu())
                except:
                    send_message(chat_id, "❌ <b>НЕВЕРНЫЙ ФОРМАТ!</b> ⚠️\n\nИспользуйте: ID_пользователя назначить", admin_menu())
            
            elif text.endswith("снять") and chat_id in admin_users:
                try:
                    user_id = int(text.replace(" снять", "").strip())
                    if user_id in admin_users:
                        username = admin_usernames.get(user_id, f'user_{user_id}')
                        admin_users.discard(user_id)
                        if user_id in admin_usernames:
                            del admin_usernames[user_id]
                        send_message(chat_id, f"✅ <b>АДМИН УДАЛЕН!</b> 🚫\n\nПользователь ID: {user_id} (@{username}) больше не администратор", admin_menu())
                    else:
                        send_message(chat_id, "❌ <b>АДМИН НЕ НАЙДЕН!</b> ⚠️", admin_menu())
                except:
                    send_message(chat_id, "❌ <b>НЕВЕРНЫЙ ФОРМАТ!</b> ⚠️\n\nИспользуйте: ID_пользователя снять", admin_menu())
            
            elif text == "💎 УСТАНОВИТЬ ПОДПИСКУ" and chat_id in admin_users and user_states.get(chat_id) == "admin_menu":
                user_states[chat_id] = "waiting_subscription_setup"
                setup_info = """💎 <b>УСТАНОВКА ПОДПИСКИ</b> 👑

📝 <b>Формат команды:</b>
<code>ID_пользователя премиум 10д/месяц/год/навсегда</code>
<code>ID_пользователя про 10д/месяц/год/навсегда</code>

🎯 <b>Примеры:</b>
• <code>123456789 премиум 10д</code>
• <code>123456789 про месяц</code>  
• <code>123456789 премиум навсегда</code>
• <code>123456789 про год</code>

✨ <i>Отправьте команду для активации подписки</i> 💫"""
                send_message(chat_id, setup_info)
            
            elif user_states.get(chat_id) == "waiting_subscription_setup" and chat_id in admin_users:
                try:
                    parts = text.split()
                    if len(parts) >= 3:
                        user_id = int(parts[0])
                        sub_type = parts[1].lower()
                        duration = parts[2].lower()
                        
                        user_info = get_user_info(user_id)
                        if user_info:
                            duration_map = {
                                '10д': 10,
                                'месяц': 30,
                                'год': 365,
                                'навсегда': 9999
                            }
                            
                            if duration in duration_map:
                                duration_days = duration_map[duration]
                                
                                if sub_type == "премиум":
                                    if duration == "навсегда":
                                        premium_users[user_id] = True
                                    else:
                                        activate_subscription(user_id, "premium", duration_days)
                                    sub_name = "💎 ПРЕМИУМ"
                                elif sub_type == "про":
                                    if duration == "навсегда":
                                        pro_users[user_id] = True
                                    else:
                                        activate_subscription(user_id, "pro", duration_days)
                                    sub_name = "🚀 PRO"
                                else:
                                    send_message(chat_id, "❌ <b>НЕВЕРНЫЙ ТИП ПОДПИСКИ!</b> ⚠️\n\nДоступно: премиум, про", admin_menu())
                                    continue
                                
                                duration_text = "НАВСЕГДА" if duration == "навсегда" else f"на {duration.upper()}"
                                send_message(chat_id, f"✅ <b>ПОДПИСКА АКТИВИРОВАНА!</b> 🎉\n\n👤 Пользователь: ID {user_id}\n💫 Тип: {sub_name}\n⏰ Срок: {duration_text}", admin_menu())
                                
                                username = user_info.get('username', f'user_{user_id}')
                                send_message(user_id, f"🎉 <b>ВАМ АКТИВИРОВАНА ПОДПИСКА!</b> ✨\n\n💫 Тип: {sub_name}\n⏰ Срок: {duration_text}\n\n✨ Наслаждайтесь премиум возможностями! 🚀")
                                
                                user_states[chat_id] = "admin_menu"
                            else:
                                send_message(chat_id, "❌ <b>НЕВЕРНЫЙ СРОК!</b> ⚠️\n\nДоступно: 10д, месяц, год, навсегда")
                        else:
                            send_message(chat_id, "❌ <b>ПОЛЬЗОВАТЕЛЬ НЕ НАЙДЕН!</b> ⚠️")
                    else:
                        send_message(chat_id, "❌ <b>НЕВЕРНЫЙ ФОРМАТ!</b> ⚠️\n\nИспользуйте: ID_пользователя премиум/про срок")
                except ValueError:
                    send_message(chat_id, "❌ <b>НЕВЕРНЫЙ ФОРМАТ ID!</b> ⚠️\n\nID должен быть числом")
                except:
                    send_message(chat_id, "❌ <b>ОШИБКА АКТИВАЦИИ ПОДПИСКИ!</b> ⚠️")
            
            elif text == "📢 ОПОВЕЩЕНИЯ" and chat_id in admin_users and user_states.get(chat_id) == "admin_menu":
                user_states[chat_id] = "waiting_broadcast"
                send_message(chat_id, "📢 <b>ОТПРАВЬТЕ ТЕКСТ ОПОВЕЩЕНИЯ:</b>\n\nСообщение будет отправлено всем пользователям 📝")
            
            elif text == "⭐ ЗВЕЗДЫ" and chat_id in admin_users and user_states.get(chat_id) == "admin_menu":
                user_states[chat_id] = "waiting_add_stars"
                send_message(chat_id, "⭐ <b>ДОБАВЛЕНИЕ ЗВЕЗД</b>\n\nОтправьте в формате:\n<code>ID_пользователя количество_звезд</code>\n\nПример: 123456789 1000 🎯")
            
            elif user_states.get(chat_id) == "waiting_add_stars" and chat_id in admin_users:
                try:
                    parts = text.split()
                    if len(parts) == 2:
                        user_id = int(parts[0])
                        stars = int(parts[1])
                        
                        user_info = get_user_info(user_id)
                        if user_info:
                            if user_id in spin_balances:
                                spin_balances[user_id] += stars
                            else:
                                spin_balances[user_id] = stars
                            
                            username = user_info.get('username', f'user_{user_id}')
                            send_message(chat_id, f"✅ <b>ДОБАВЛЕНО {stars}⭐ пользователю ID: {user_id} (@{username})</b> 🎉", admin_menu())
                            send_message(user_id, f"🎁 <b>Вам начислено {stars}⭐ на баланс!</b> 💎\n\nСпасибо за активность! 🎯")
                            user_states[chat_id] = "admin_menu"
                        else:
                            send_message(chat_id, "❌ <b>ПОЛЬЗОВАТЕЛЬ НЕ НАЙДЕН!</b> ⚠️")
                    else:
                        send_message(chat_id, "❌ <b>ОШИБКА ФОРМАТА!</b> ⚠️\n\nИспользуйте: ID_пользователя количество_звезд")
                except ValueError:
                    send_message(chat_id, "❌ <b>НЕВЕРНЫЙ ФОРМАТ!</b> ⚠️\n\nID и количество звезд должны быть числами")
                except:
                    send_message(chat_id, "❌ <b>ОШИБКА ФОРМАТА!</b> ⚠️\n\nИспользуйте: ID_пользователя количество_звезд")
            
            elif user_states.get(chat_id) == "waiting_broadcast" and chat_id in admin_users:
                if text and text not in ["📢 ОПОВЕЩЕНИЯ", "🔙 НАЗАД"]:
                    broadcast_msg = f"📢 <b>ОПОВЕЩЕНИЕ ОТ АДМИНИСТРАЦИИ</b> 👑\n\n{text}\n\n💫 <i>Следите за новостями!</i>"
                    success_count = send_broadcast_message(broadcast_msg)
                    send_message(chat_id, f"✅ <b>ОПОВЕЩЕНИЕ ОТПРАВЛЕНО {success_count} ПОЛЬЗОВАТЕЛЯМ!</b> 📢", admin_menu())
                    user_states[chat_id] = "admin_menu"
            
            elif text == "❓ ПОМОЩЬ":
                user_states[chat_id] = "help_menu"
                help_text = """❓ <b>ПОМОЩЬ И ПОДДЕРЖКА</b>

📞 <b>Техническая поддержка:</b>
@DontWarryImTheStrongest

🔧 <b>Частые вопросы:</b>
• Как купить подписку? - Выберите "💳 ПОДПИСКИ"
• Как получить скрипт? - Выберите "🎮 СКРИПТЫ" 
• Как играть в спин? - Выберите "🎰 СПИН"
• Как проверить пользователя? - Выберите "🔍 ПОИСК"

💎 <b>Для донатов:</b> Выберите "❤️ ДОНАТ"

⚡ <i>По всем вопросам обращайтесь в поддержку</i>"""
                send_message(chat_id, help_text, help_menu())
            
            elif text == "📞 Поддержка" and user_states.get(chat_id) == "help_menu":
                send_message(chat_id, "📞 <b>ТЕХНИЧЕСКАЯ ПОДДЕРЖКА</b>\n\n👤 @DontWarryImTheStrongest\n\n💬 Напишите нам для решения проблем!", help_menu())
            
            elif text == "❓ FAQ" and user_states.get(chat_id) == "help_menu":
                faq_text = """❓ <b>ЧАСТО ЗАДАВАЕМЫЕ ВОПРОСЫ</b>

Q: Как купить подписку?
A: Выберите "💳 ПОДПИСКИ" → выберите тип → оплатите

Q: Как получить скрипт?
A: Выберите "🎮 СКРИПТЫ" → выберите скрипт → оплатите → получите код

Q: Как играть в спин?
A: Выберите "🎰 СПИН" → "🎰 КРУТИТЬ" → выберите ставку

Q: Как вывести звезды?
A: В меню спина выберите "💸 ВЫВОД" (от 50000⭐)

Q: Как проверить пользователя?
A: Выберите "🔍 ПОИСК" → отправьте @username"""
                send_message(chat_id, faq_text, help_menu())
            
            elif text == "💎 О подпискаи" and user_states.get(chat_id) == "help_menu":
                subscriptions_info = """💎 <b>ИНФОРМАЦИЯ О ПОДПИСКАХ</b>

🎯 <b>БЕСПЛАТНЫЙ ДОСТУП:</b>
• Базовые скрипты
• Поиск пользователей
• Проверка чатов
• Спин (с покупкой звезд)

💎 <b>ПРЕМИУМ ПОДПИСКА:</b>
• Все базовые функции
• 100+ премиум скриптов
• Яндекс-диск с коллекцией
• NFT подарки в поиске
• Приоритетная поддержка

🚀 <b>PRO ПОДПИСКА:</b>
• Все функции Премиум
• Доступ к премиальному магазину
• Полная история смен юзернеймов
• Реальные данные о потраченных TON
• +10000⭐ на баланс
• Эксклюзивные скрипты
• Персональная поддержка

💰 <b>Стоимость:</b>
• 10 дней: 300-400⭐
• Месяц: 400-500⭐  
• Год: 500-600⭐
• Навсегда: 1500-3000⭐"""
                send_message(chat_id, subscriptions_info, help_menu())
            
            elif text == "❤️ ДОНАТ":
                user_states[chat_id] = "waiting_donation"
                send_message(chat_id, "❤️ <b>ВЫБЕРИТЕ СКОЛЬКО ВЫ ХОТЕЛИ БЫ ПОЖЕРТВОВАТЬ РАЗРАБОТЧИКАМ</b> 😉\n\nНапишите число - сколько звезд хотите подарить: ⭐")
            
            elif user_states.get(chat_id) == "waiting_donation" and text.isdigit():
                amount = int(text)
                if 1 <= amount <= 1000:
                    send_message(chat_id, f"❤️ <b>СПАСИБО ЗА ЖЕЛАНИЕ ПОДДЕРЖАТЬ НАС!</b> 💝\n\nВот кнопка чтобы купить {amount}⭐👇🏻")
                    send_invoice(chat_id, amount, f"donation_{amount}", f"Донат {amount}⭐", f"Поддержка разработчиков - {amount} звезд")
                    user_states[chat_id] = "menu"
                else:
                    send_message(chat_id, "❌ <b>Введите число от 1 до 1000</b> ⚠️")
            
            elif user_states.get(chat_id) == "waiting_username" and text.startswith('@'):
                username = text.replace('@', '').strip()
                user_info = get_real_user_info(username)
                
                if user_info:
                    response = f"""🔍 <b>РЕЗУЛЬТАТЫ ПОИСКА:</b>

👤 <b>Пользователь:</b> @{user_info['username']}
🔗 <b>Профиль:</b> {user_info['profile_url']}
📅 <b>Дата регистрации:</b> {user_info['join_date']}
👀 <b>Был в сети:</b> {user_info['last_seen']}
⏰ <b>Время в ТГ за день:</b> {user_info['daily_time']}
🛡️ <b>Статус:</b> {user_info['scam_status']}
⚠️ <b>Уровень риска:</b> {user_info['risk_level']}
⭐ <b>Репутация:</b> {user_info['reputation']}/100

📜 <b>История имен:</b> {', '.join(user_info['name_history'])}"""
                    
                    if has_premium_access(chat_id) or has_pro_access(chat_id):
                        response += f"\n\n🏙️ <b>Город:</b> {user_info['city']}"
                        response += f"\n\n💰 <b>Потрачено TON:</b> {user_info['ton_spent']:.2f} TON"
                        
                        if user_info['purchased_gifts']:
                            response += "\n\n🎁 <b>Привязанные подарки:</b>"
                            for gift in user_info['purchased_gifts']:
                                response += f"\n• {gift['date']}: {gift['gift']} ({gift['price']})"
                    
                    if has_pro_access(chat_id):
                        response += f"\n\n📱 <b>Устройство:</b> {user_info['device']}"
                    
                    if user_info['gift_history']:
                        response += "\n\n🎁 <b>История подарков:</b>"
                        for gift in user_info['gift_history']:
                            response += f"\n• {gift['date']}: {gift['gift']} от {gift['from']}"
                else:
                    response = f"❌ <b>ПОЛЬЗОВАТЕЛЬ @{username} НЕ НАЙДЕН!</b>\n\nПроверьте правильность написания юзернейма."
                
                send_message(chat_id, response, main_menu(chat_id))
                user_states[chat_id] = "menu"
            
            elif user_states.get(chat_id) == "waiting_chat_link" and ('@' in text or 't.me' in text):
                chat_info = check_chat_security(text)
                
                if chat_info:
                    response = f"""🛡️ <b>РЕЗУЛЬТАТ ПРОВЕРКИ ЧАТА:</b>

👥 <b>Участников:</b> {chat_info['member_count']}
🤖 <b>Ботов:</b> {chat_info['bots_count']}
👑 <b>Админов:</b> {chat_info['admin_count']}
🛡️ <b>Уровень безопасности:</b> {chat_info['security_level']}
🔗 <b>Ограничения ссылок:</b> {'✅ Есть' if chat_info['link_restrictions'] else '❌ Нет'}
🚫 <b>Анти-спам:</b> {'✅ Включен' if chat_info['anti_spam'] else '❌ Выключен'}"""
                else:
                    response = "❌ <b>НЕВОЗМОЖНО ПРОВЕРИТЬ ЧАТ!</b>\n\nПроверьте правильность ссылки."
                
                send_message(chat_id, response, main_menu(chat_id))
                user_states[chat_id] = "menu"
            
            elif user_states.get(chat_id) == "scripts_menu" and any(text.startswith(script_name) for script_name in list(scripts_database.keys()) + list(premium_scripts.keys())):
                if text in premium_scripts and (has_premium_access(chat_id) or has_pro_access(chat_id)):
                    script_code = premium_scripts[text]
                    send_message(chat_id, f"🎮 <b>{text}</b>\n\n<code>{script_code}</code>\n\n✨ <i>Премиум скрипт активирован!</i>", scripts_menu(chat_id))
                elif text in premium_scripts:
                    send_message(chat_id, "❌ <b>ДОСТУП ЗАПРЕЩЕН!</b>\n\n💎 Этот скрипт доступен только для пользователей с PREMIUM или PRO подпиской!\n\nВыберите другую подписку в меню \"💳 ПОДПИСКИ\"", scripts_menu(chat_id))
                else:
                    for script_name, script_data in scripts_database.items():
                        if text.startswith(script_name):
                            price = script_data['price']
                            send_message(chat_id, f"🎮 <b>{script_name}</b>\n\n💎 Цена: {price}⭐\n\nНажмите кнопку ниже для покупки 👇")
                            send_invoice(chat_id, price, f"script_{script_name}", f"Скрипт {script_name}", f"Покупка скрипта {script_name}")
                            break
            
            elif user_states.get(chat_id) == "subscriptions_menu" and any(sub_text in text for sub_text in ["10Д ПРЕМИУМ", "10Д PRO", "МЕСЯЦ ПРЕМИУМ", "МЕСЯЦ PRO", "ГОД ПРЕМИУМ", "ГОД PRO", "НАВСЕГДА ПРЕМИУМ", "НАВСЕГДА PRO"]):
                if "10Д ПРЕМИУМ" in text:
                    send_invoice(chat_id, 300, "premium_10d", "Премиум 10 дней", "Премиум подписка на 10 дней")
                elif "10Д PRO" in text:
                    send_invoice(chat_id, 400, "pro_10d", "PRO 10 дней", "PRO подписка на 10 дней")
                elif "МЕСЯЦ ПРЕМИУМ" in text:
                    send_invoice(chat_id, 400, "premium_30d", "Премиум месяц", "Премиум подписка на месяц")
                elif "МЕСЯЦ PRO" in text:
                    send_invoice(chat_id, 500, "pro_30d", "PRO месяц", "PRO подписка на месяц")
                elif "ГОД ПРЕМИУМ" in text:
                    send_invoice(chat_id, 500, "premium_365d", "Премиум год", "Премиум подписка на год")
                elif "ГОД PRO" in text:
                    send_invoice(chat_id, 600, "pro_365d", "PRO год", "PRO подписка на год")
                elif "НАВСЕГДА ПРЕМИУМ" in text:
                    send_invoice(chat_id, 1500, "premium_forever", "Премиум навсегда", "Премиум подписка навсегда")
                elif "НАВСЕГДА PRO" in text:
                    send_invoice(chat_id, 3000, "pro_forever", "PRO навсегда", "PRO подписка навсегда")
            
            elif "message" in update and "successful_payment" in update["message"]:
                payment = update["message"]["successful_payment"]
                payload = payment["invoice_payload"]

                if payload == "premium_10d":
                    activate_subscription(chat_id, "premium", 10)
                    yandex_disk_link = "https://disk.yandex.ru/d/SNy2CcLBBAVomw"
                    send_message(chat_id, f"✅ <b>ПРЕМИУМ 10 ДНЕЙ АКТИВИРОВАН!</b> 🎉\n\n📂 <b>Доступ к 100+ скриптам:</b>\n{yandex_disk_link}", main_menu(chat_id))
                elif payload == "pro_10d":
                    activate_subscription(chat_id, "pro", 10)
                    if chat_id not in spin_balances:
                        spin_balances[chat_id] = 0
                    spin_balances[chat_id] += 10000
                    funpay_link = "https://funpay.com/users/16978665/"
                    send_message(chat_id, f"🎖️ <b>PRO ПОДПИСКА АКТИВИРОВАНА!</b> 💵\n\nДля вас доступен премиальный магазин со скриптами и услугами:\n{funpay_link}\n\n💰✅ <b>+10000⭐ на ваш баланс!</b>\n💎 Теперь ваш баланс: {spin_balances[chat_id]}⭐", main_menu(chat_id))
                elif payload == "premium_30d":
                    activate_subscription(chat_id, "premium", 30)
                    yandex_disk_link = "https://disk.yandex.ru/d/SNy2CcLBBAVomw"
                    send_message(chat_id, f"✅ <b>ПРЕМИУМ МЕСЯЦ АКТИВИРОВАН!</b> 📅\n\n📂 <b>Доступ к 100+ скриптам:</b>\n{yandex_disk_link}", main_menu(chat_id))
                elif payload == "pro_30d":
                    activate_subscription(chat_id, "pro", 30)
                    if chat_id not in spin_balances:
                        spin_balances[chat_id] = 0
                    spin_balances[chat_id] += 10000
                    funpay_link = "https://funpay.com/users/16978665/"
                    send_message(chat_id, f"🎖️ <b>PRO ПОДПИСКА АКТИВИРОВАНА!</b> 💵\n\nДля вас доступен премиальный магазин со скриптами и услугами:\n{funpay_link}\n\n💰✅ <b>+10000⭐ на ваш баланс!</b>\n💎 Теперь ваш баланс: {spin_balances[chat_id]}⭐", main_menu(chat_id))
                elif payload == "premium_365d":
                    activate_subscription(chat_id, "premium", 365)
                    yandex_disk_link = "https://disk.yandex.ru/d/SNy2CcLBBAVomw"
                    send_message(chat_id, f"✅ <b>ПРЕМИУМ ГОД АКТИВИРОВАН!</b> 🎊\n\n📂 <b>Доступ к 100+ скриптам:</b>\n{yandex_disk_link}", main_menu(chat_id))
                elif payload == "pro_365d":
                    activate_subscription(chat_id, "pro", 365)
                    if chat_id not in spin_balances:
                        spin_balances[chat_id] = 0
                    spin_balances[chat_id] += 10000
                    funpay_link = "https://funpay.com/users/16978665/"
                    send_message(chat_id, f"🎖️ <b>PRO ПОДПИСКА АКТИВИРОВАНА!</b> 💵\n\nДля вас доступен премиальный магазин со скриптами и услугами:\n{funpay_link}\n\n💰✅ <b>+10000⭐ на ваш баланс!</b>\n💎 Теперь ваш баланс: {spin_balances[chat_id]}⭐", main_menu(chat_id))
                elif payload == "premium_forever":
                    premium_users[chat_id] = True
                    yandex_disk_link = "https://disk.yandex.ru/d/SNy2CcLBBAVomw"
                    send_message(chat_id, f"✅ <b>ПРЕМИУМ НАВСЕГДА АКТИВИРОВАН!</b> 💫\n\n📂 <b>Доступ к 100+ скриптам:</b>\n{yandex_disk_link}", main_menu(chat_id))
                elif payload == "pro_forever":
                    pro_users[chat_id] = True
                    if chat_id not in spin_balances:
                        spin_balances[chat_id] = 0
                    spin_balances[chat_id] += 10000
                    funpay_link = "https://funpay.com/users/16978665/"
                    send_message(chat_id, f"🎖️ <b>PRO ПОДПИСКА АКТИВИРОВАНА!</b> 💵\n\nДля вас доступен премиальный магазин со скриптами и услугами:\n{funpay_link}\n\n💰✅ <b>+10000⭐ на ваш баланс!</b>\n💎 Теперь ваш баланс: {spin_balances[chat_id]}⭐", main_menu(chat_id))
                elif payload.startswith("script_"):
                    script_name = payload.replace("script_", "")
                    if script_name in scripts_database:
                        script_code = scripts_database[script_name]["code"]
                        send_message(chat_id, f"🎮 <b>{script_name}</b>\n\n<code>{script_code}</code>\n\n🕹️ <i>Удачной игры!</i>", main_menu(chat_id))
                elif payload.startswith("donation_"):
                    amount = payload.replace("donation_", "")
                    send_message(chat_id, f"❤️ <b>СПАСИБО ЗА ДОНАТ {amount}⭐!</b> 💝\n\nВаша поддержка очень важна для нас! 🌟", main_menu(chat_id))
                elif payload.startswith("spin_"):
                    bet_amount = int(payload.replace("spin_", ""))
                    if chat_id not in spin_balances:
                        spin_balances[chat_id] = 0
                    spin_balances[chat_id] += bet_amount
                    send_message(chat_id, f"✅ <b>ВЫ ПОПОЛНИЛИ БАЛАНС НА {bet_amount}⭐!</b> 💎\n\n💰 Теперь ваш баланс: {spin_balances[chat_id]}⭐", spin_menu())
                user_states[chat_id] = "menu"
                continue
            
            elif text == "🔙 НАЗАД":
                if user_states.get(chat_id) in ["scripts_menu", "subscriptions_menu", "spin_menu", "admin_menu", "help_menu", "waiting_spin_bet", "waiting_custom_bet"]:
                    user_states[chat_id] = "spin_menu" if user_states.get(chat_id) in ["waiting_spin_bet", "waiting_custom_bet"] else "menu"
                    send_message(chat_id, "🔙 <b>Главное меню</b> 🏠", main_menu(chat_id))
                else:
                    user_states[chat_id] = "menu"
                    send_message(chat_id, "🔙 <b>Главное меню</b> 🏠", main_menu(chat_id))
            
            else:
                if current_state not in ["waiting_username", "waiting_chat_link", "waiting_donation", "waiting_broadcast", "waiting_add_stars", "waiting_spin_bet", "waiting_subscription_setup", "waiting_custom_bet"]:
                    send_message(chat_id, "❓ <b>Используйте кнопки меню</b> 📱", main_menu(chat_id))
        
        if len(processed_updates) > 100:
            processed_updates.clear()
        
        time.sleep(0.1)
        
    except Exception as e:
        time.sleep(1)

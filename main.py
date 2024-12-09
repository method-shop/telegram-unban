import telebot
import requests
import threading
import json
import time
from telebot import types

                                                                                                                                                                                                 
# BY : @ziddi_beatz1  |   6110266480


TOKEN = '6805752027:AAHiCrrdTsieMCdWATYek6di1TPOP0-OADY' 
ADMIN_IDS = [6110266480]  
mandatory_subscription_channel = '@ziddi_beatz'  


USER_DATA_FILE = 'user_data.json'


def load_user_data():
    try:
        with open(USER_DATA_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_user_data():
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(user_data, f)


user_data = load_user_data()

bot_active = True


bot = telebot.TeleBot(TOKEN)

user_data = {}  
sending_threads = {}  


# A default cliche in the bot
DEFAULT_MESSAGE = """

Dear Telegram Support Team,

I am reaching out due to an unexpected issue preventing me from accessing my Telegram account. Upon attempting to log in or register, I received a notification stating that my phone number has been blocked on Telegram.

I am genuinely puzzled by this restriction, as I have always adhered to Telegram’s terms and policies. I believe this may have been an unintentional error, and I kindly request your assistance in promptly reviewing my account to restore my access.

Thank you for your time and support in resolving this matter.

"""

def send_support_request(message, email, phone):
    cookies = {
        'stel_ssid': '56d1a6474a3a7304f3_4667009158728337944',
        'stel_ln': 'ar',
    }
    
    headers = {
        'authority': 'telegram.org',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9,ar-SA;q=0.8,ar;q=0.7,en-GB;q=0.6',
        'cache-control': 'max-age=0',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://telegram.org',
        'referer': 'https://telegram.org/support?setln=ar',
        'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
    }

    data = {
        'message': message,
        'email': email,
        'phone': phone,
        'setln': 'ar',
    }

    response = requests.post('https://telegram.org/support', cookies=cookies, headers=headers, data=data).text
    success_indicator = '<div class="alert alert-success"><b>شكرًا على بلاغك&#33;</b><br/>سنحاول الرّد بأسرع ما يمكن.</div>'
    return success_indicator in response

def start_sending(chat_id, message, email, phone, message_id):
    count = 0
    while sending_threads.get(chat_id, False):
        if send_support_request(message, email, phone):
            count += 1
            markup = telebot.types.InlineKeyboardMarkup()
            stop_button = telebot.types.InlineKeyboardButton('🛑 Off', callback_data='stop')
            markup.add(stop_button)
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f"✅ has been sent {count} Reports.", reply_markup=markup)
        else:
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f"❌Failed to send the report {count + 1}.")


def check_subscription(user_id):
    try:
        user_status = bot.get_chat_member(mandatory_subscription_channel, user_id)
        return user_status.status in ['member', 'administrator', 'creator']
    except Exception as e:
        print(f"Error checking subscription: {e}")
        return False

  
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id 

    if not bot_active and user_id not in ADMIN_IDS:
        bot.reply_to(message, "Sorry, the bot is currently down for maintenance. Please try later.")
        return

    if not check_subscription(user_id):
        bot.send_message(
            message.chat.id,
            "⚠️ You must subscribe to the developer channel to use the bot.\n\n"
            f"🔗 Click here to go to the channel and subscribe: {mandatory_subscription_channel}"
        )
        return

    markup = telebot.types.InlineKeyboardMarkup()
    default_button = telebot.types.InlineKeyboardButton('Use a default message', callback_data='use_default_message')
    developer_channel_button = telebot.types.InlineKeyboardButton(text='Developer channel', url=f'https://t.me/{mandatory_subscription_channel[1:]}')
    markup.add(default_button)
    markup.add(developer_channel_button)

    bot.reply_to(message, "Welcome! 👋 Please send the message you would like to send to support.", reply_markup=markup)
    
    user_data[message.chat.id] = {'step': 'message'}
    user_data[message.chat.id] = {'step': 'message', 'last_activity': time.time(), 'reports_sent': 0}
    save_user_data()

@bot.callback_query_handler(func=lambda call: call.data == 'use_default_message')


def use_default_message(call):

    chat_id = call.message.chat.id
    user_data[chat_id]['message'] = DEFAULT_MESSAGE
    user_data[chat_id]['step'] = 'email'
    bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text="Send now your email.")

@bot.message_handler(func=lambda msg: msg.chat.id in user_data and user_data[msg.chat.id]['step'] == 'message')
def get_message(message):

    user_data[message.chat.id]['message'] = message.text
    user_data[message.chat.id]['step'] = 'email'
    bot.reply_to(message, "Thanks! ✉️ Now, please send email.")

@bot.message_handler(func=lambda msg: msg.chat.id in user_data and user_data[msg.chat.id]['step'] == 'email')
def get_email(message):
    """Get the email from the user"""
    user_data[message.chat.id]['email'] = message.text
    user_data[message.chat.id]['step'] = 'phone'
    bot.reply_to(message, "great! 📞 Finally, send the phone number.")

@bot.message_handler(func=lambda msg: msg.chat.id in user_data and user_data[msg.chat.id]['step'] == 'phone')
def get_phone(message):#-
    """Get the phone number and start the sending process"""
    user_data[message.chat.id]['phone'] = message.text
    msg_text = user_data[message.chat.id].get('message', '')
    email = user_data[message.chat.id].get('email', '')
    phone = user_data[message.chat.id]['phone']

    if not msg_text or not email:#-
        bot.reply_to(message, "There is an error in the data entered. Please start over.")
        return

    markup = telebot.types.InlineKeyboardMarkup()#-
    stop_button = telebot.types.InlineKeyboardButton('🛑Off', callback_data='stop')
    developer_channel_button = types.InlineKeyboardButton(text='Developer channel', url='https://t.me/ziddi_beatz')

    markup.add(stop_button)
    markup.add(developer_channel_button)                                                                                


    msg = bot.reply_to(message, "🔄Start sending reports...", reply_markup=markup)
    sending_threads[message.chat.id] = True
    thread = threading.Thread(target=start_sending, args=(message.chat.id, msg_text, email, phone, msg.message_id))#-
    thread.start()
def start_sending(chat_id, message, email, phone, message_id):
    count = 0
    while sending_threads.get(chat_id, False):
        if send_support_request(message, email, phone):
            count += 1
            user_data[chat_id]['reports_sent'] = count
            save_user_data()#+
            markup = telebot.types.InlineKeyboardMarkup()
            stop_button = telebot.types.InlineKeyboardButton('🛑 Off', callback_data='stop')
            markup.add(stop_button)
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f"✅ has been sent {count} Reports.", reply_markup=markup)#+
        else:
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f"❌Failed to send the report {count + 1}.")#+

@bot.callback_query_handler(func=lambda call: call.data == 'stop')
def stop_sending(call):
    chat_id = call.message.chat.id
    if sending_threads.get(chat_id, False):
        sending_threads[chat_id] = False
        bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text="🛑Sending reports has been stopped. You can start over.")
        if chat_id in user_data:
            del user_data[chat_id]
    bot.answer_callback_query(call.id)





@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id in ADMIN_IDS:
        markup = telebot.types.InlineKeyboardMarkup()
        stats_button = telebot.types.InlineKeyboardButton('📊 statistics', callback_data='admin_stats')
        broadcast_button = telebot.types.InlineKeyboardButton('📢 Send to everyone', callback_data='admin_broadcast')
        logs_button = telebot.types.InlineKeyboardButton('📋 Records', callback_data='admin_logs')
        users_button = telebot.types.InlineKeyboardButton('👥 Users', callback_data='admin_users')
        markup.add(stats_button, broadcast_button)
        markup.add( users_button)
        markup.add(logs_button)

        bot.reply_to(message, "Welcome to the admin panel. Choose one of the options:", reply_markup=markup)
    else:
        bot.reply_to(message, "Sorry, this command is only available to administrators.")



@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_'))
def admin_callback(call):
    if call.from_user.id in ADMIN_IDS:
        if call.data == 'admin_stats':
            show_stats(call.message)
        elif call.data == 'admin_broadcast':
            start_broadcast(call.message)
        elif call.data == 'admin_toggle_bot':
            toggle_bot(call.message)
        elif call.data == 'admin_logs':
            show_logs(call.message)
        elif call.data == 'admin_users':
            show_users(call.message)
        elif call.data == 'admin_ban':
            start_ban_process(call.message)
    else:
        bot.answer_callback_query(call.id, "You are not authorized to use this feature")


def get_user_id_by_username(username):

    for user_id, user_info in user_data.items():
        if user_info.get('username') == username:
            return user_id
    return None


def show_stats(message):
    users_count = len(user_data)
    active_users = sum(1 for user in user_data.values() if user.get('last_activity', 0) > time.time() - 86400)
    total_reports = sum(user.get('reports_sent', 0) for user in user_data.values())
    stats_message = f"📊 Bot statistics:\n\n" \
                    f"👥 Total users: {users_count}\n" \
                    f"🟢Active users (24 hours): {active_users}\n" \
                    f"📩Total reports sent: {total_reports}"
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=stats_message)

def start_broadcast(message):
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, 
                          text="Now send the message you want to send to all users:")
    user_data[message.chat.id] = {'step': 'admin_broadcast'}

def toggle_bot(message):
    global bot_active
def show_users(message):
    user_list = "List of users:\n\n"
    for user_id, user_info in user_data.items():
        user_list += f"representative: {user_id}\n"
        user_list += f"The end of happiness: {datetime.datetime.fromtimestamp(user_info.get('last_activity', 0)).strftime('%Y-%m-%d %H:%M:%S')}\n"
        user_list += f"Reports sent: {user_info.get('reports_sent', 0)}\n"
        user_list += f"Forbidden: {'Yes' if user_info.get('banned', False) else 'no'}\n\n"
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=user_list)

def start_ban_process(message):
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, 
                          text="Submit the ID of the user you want to block or unblock:")
    user_data[message.chat.id] = {'step': 'admin_ban'}



def show_logs(message):
    logs = "Last 10 operations:\n" + "\n".join([f"Process {i+1}" for i in range(10)])
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=logs)
    try:#+
        with open('bot_logs.txt', 'r', encoding='utf-8') as log_file:
            logs = log_file.readlines()[-10:] 
        log_text = "Latest 10 events:\n\n" + "".join(logs)
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=log_text)
    except FileNotFoundError:
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="No records available.")

import datetime

def log_event(event):
    with open('bot_logs.txt', 'a', encoding='utf-8') as log_file:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file.write(f"{timestamp} - {event}\n")


    return True

def get_user_details(user_id):
    if user_id not in user_data:
        return None
    user = user_data[user_id]
    return f"User ID : {user_id}\n" \
           f"The end of happiness: {datetime.datetime.fromtimestamp(user.get('last_activity', 0)).strftime('%Y-%m-%d %H:%M:%S')}\n" \
           f"Number of reports sent: {user.get('reports_sent', 0)}\n" \



@bot.message_handler(func=lambda msg: msg.chat.id in user_data and user_data[msg.chat.id].get('step') == 'admin_broadcast')
def send_broadcast(message):
    if message.from_user.id in ADMIN_IDS:
        broadcast_message = message.text
        success_count = 0
        for user_id in user_data.keys():
            try:
                bot.send_message(user_id, broadcast_message)
                success_count += 1
            except Exception as e:
                print(f"Failed to send message to {user_id}: {e}")
        bot.reply_to(message, f"The message was successfully sent to {success_count} user.")
        user_data[message.chat.id].pop('step', None)
    else:
        bot.reply_to(message, "Sorry, this is only available to administrators.")

# BY : @ziddi_beatz  |   6110266480

bot.infinity_polling()

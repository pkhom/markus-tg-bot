import os
import random
from datetime import datetime, timedelta

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

API_TOKEN = "5010145034:AAHAqSJkVZ5NnDRKMsOAUjSKBznZGwd94LQ"

bot = telebot.TeleBot(API_TOKEN)

last_pet_time = {}
last_feed_time = {}

last_message_id = 0

msg_to_delete = 0

mg_count = 1
mg_user_id = 0
incorrect = 0
chosen = 0

asked_for_food = False

games = ["Mouse catch game"]


def mouse_game(chat_id, user_id, user_name):
    global mg_count, mg_user_id, msg_to_delete, incorrect

    keyboard = InlineKeyboardMarkup()
    left_button = InlineKeyboardButton(text="⬅️🐭", callback_data="mg_0")
    right_button = InlineKeyboardButton(text="🐭➡️", callback_data="mg_1")
    up_button = InlineKeyboardButton(text="⬆️🐭⬆️️", callback_data="mg_2")
    down_button = InlineKeyboardButton(text="⬇️🐭⬇️", callback_data="mg_3")
    keyboard.add(up_button, row_width=1)
    keyboard.add(left_button, right_button, row_width=2)
    keyboard.add(down_button, row_width=1)

    if mg_count == 1:
        mg_user_id = user_id
        bot.send_message(chat_id,
                         "🐭*The Mouse Game\n\nMove the mouse toy left and right and I will try to catch it!\nI have 5 attempts*",
                         parse_mode="Markdown")
        incorrect = random.randint(0, 3)
        msg_to_delete = bot.send_message(chat_id, f"Mrra {mg_count}/5", reply_markup=keyboard).id

        mg_count += 1
    elif mg_count < 6 and mg_count != 1:
        bot.delete_message(chat_id, msg_to_delete)
        incorrect = random.randint(0, 3)
        msg_to_delete = bot.send_message(chat_id, f"Mrra {mg_count}/5", reply_markup=keyboard).id

        mg_count += 1
    elif mg_count == 6:
        bot.delete_message(chat_id, msg_to_delete)
        bot.send_message(chat_id, "Mrr, you won... (rep +1)")
        update_reputation(user_id, user_name)
        mg_user_id = 0
        mg_count = 0
        incorrect = 0

def update_reputation(user_id, user_name):
    reputation_data = {}
    file_path = "../stats/rep.txt"

    if os.stat(file_path).st_size == 0:
        print("File exists but is empty.")
    else:
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                for line in file:
                    line = line.strip()
                    if line:
                        username, userid, rep = line.split(":")
                        reputation_data[int(userid)] = {"username": username, "rep": int(rep)}
        except FileNotFoundError:
            return

    print("Before")
    print(reputation_data)

    if user_id in reputation_data:
        reputation_data[user_id]["rep"] += 1
    else:
        reputation_data[user_id] = {"username": user_name, "rep": 1}


    with open(file_path, "w", encoding="utf-8") as file:
        for userid, data in reputation_data.items():
            file.write(f"{data['username']}:{userid}:{data['rep']}\n")

    print("After")
    print(reputation_data)

def get_reputation():
    reputation_data = {}
    file_path = "../stats/rep.txt"
    text = "*Reputation:*\n\n"

    # Read the file and store data in a dictionary
    if os.stat(file_path).st_size == 0:
        print("File exists but is empty.")
        return
    else:
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                for line in file:
                    line = line.strip()
                    if line:  # Skip empty lines
                        username, userid, rep = line.split(":")
                        reputation_data[int(userid)] = {"username": username, "rep": int(rep)}
        except FileNotFoundError:
            return

    reputation_data_sorted = sorted(reputation_data.items(), key=lambda item: item[1]["rep"], reverse=True)

    for userid, data in reputation_data_sorted:
        if data["rep"] == 0:
            continue
        else:
            text += f"[{data['username']}](tg://user?id={userid}): {data['rep']}\n"

    return text


@bot.message_handler(commands=["pet"])
def pet_command(message: telebot.types.Message):
    current_time = datetime.now()

    if message.from_user.id in last_pet_time:
        last_time = last_pet_time[message.from_user.id]
        time_diff = current_time - last_time

        if time_diff < timedelta(hours=2):
            remaining_time = timedelta(hours=2) - time_diff
            hours, remainder = divmod(remaining_time.seconds, 3600)
            minutes = remainder // 60
            bot.reply_to(message, f"You can pet me again in {hours} hours and {minutes} minutes!")
            return

    last_pet_time[message.from_user.id] = current_time

    voice = f"../voiceMsgs/{random.randint(1, 8)}.mp3"
    bot.send_voice(message.chat.id, telebot.types.InputFile(voice), caption="(rep +1)", reply_to_message_id=message.id)

    update_reputation(message.from_user.id, message.from_user.first_name)


@bot.message_handler(commands=["rep"])
def rep_command(message: telebot.types.Message):
    text = get_reputation()
    if text is not None:
        bot.send_message(message.chat.id, text, parse_mode="Markdown")


@bot.message_handler(commands=["play"])
def play_command(message: telebot.types.Message):
    global msg_to_delete

    games_list_keyboard = InlineKeyboardMarkup()
    mouse_game_btn = InlineKeyboardButton("Mouse catch game", callback_data="play_mouse")
    games_list_keyboard.add(mouse_game_btn)

    bot.send_message(message.chat.id, "List of available games.", reply_markup=games_list_keyboard)


@bot.message_handler(func=lambda message: True)
def update_text_message(message : telebot.types.Message):
    global last_message_id, asked_for_food
    message_text = message.text.lower()
    chat_id = message.chat.id
    message_id = message.id
    message_user = message.from_user
    user_id = message_user.id
    username = message_user.username
    user_firstname = message_user.first_name

    # debug
    print(f"Message id: {message_id}\n"
          f"Chat id: {chat_id}\n"
          f"From User: {user_id}, {username}, {user_firstname}\n"
          f"Text: {message_text}\n")

    #feed request
    if random.random() < 0.03:
        last_message_id = bot.send_message(chat_id, "Mrraw🙏").id
        asked_for_food = True
        print(last_message_id)

    #feed
    current_time = datetime.now()

    if ((message.reply_to_message is not None) and (message.reply_to_message.id == last_message_id) and
            (message_text == "🥓"
             or message_text == "🥩"
             or message_text == "🍗"
             or message_text == "🍖"
             or message_text == "🍤"
             or message_text == "🧀"
             or message_text == "🐟"
             or message_text == "🍕")):
        if asked_for_food:
            bot.send_message(chat_id, "Mrrra🥰 (rep +1)", reply_to_message_id=message_id)
            last_message_id = 0
            update_reputation(user_id, message_user.first_name)
        else:
            if user_id in last_feed_time:
                last_time = last_feed_time[user_id]
                time_diff = current_time - last_time

                if time_diff < timedelta(hours=0.5):
                    remaining_time = timedelta(hours=0.5) - time_diff
                    hours, remainder = divmod(remaining_time.seconds, 3600)
                    minutes = remainder // 60
                    bot.reply_to(message, f"You can feed me again in {hours} hours and {minutes} minutes!")
                    return

            last_feed_time[message.from_user.id] = current_time

            bot.send_message(chat_id, "Mrrra🥰 (rep +1)", reply_to_message_id=message_id)
            last_message_id = 0
            update_reputation(user_id, message_user.first_name)

    elif (message.reply_to_message is not None) and (message.reply_to_message.id == last_message_id) and (message_text == "meow"):
        last_message_id = 0
        bot.send_message(chat_id, "Prrrr")

    elif ("markus" in message_text) or ("маркус" in message_text):
        last_message_id = bot.send_message(chat_id, text="Meow?", reply_to_message_id=message_id).id

    elif message_text == "ksksks" or message_text == "кскскс":
        bot.send_message(chat_id, "Mrrraaa")


@bot.callback_query_handler(func=lambda call: True)
def callback(call: CallbackQuery):
    global mg_count, mg_user_id, chosen

    call_data = call.data
    chat_id = call.message.chat.id
    call_user = call.from_user
    user_id = call_user.id

    if call_data == "play_mouse":
        bot.delete_message(chat_id, call.message.id)
        mouse_game(chat_id, user_id, call.from_user.first_name)

    elif call_data == "mg_0":
        if user_id == mg_user_id:
            if incorrect == 0:
                bot.delete_message(chat_id, call.message.id)
                bot.send_message(chat_id, "Mrraaa!🐭☠️")
                mg_count = 1
                mg_user_id = 0
            else:
                mouse_game(chat_id, user_id, call.from_user.first_name)
        else:
            bot.send_message(chat_id, "You are not playing now!")
    elif call_data == "mg_1":
        if user_id == mg_user_id:
            if incorrect == 1:
                bot.delete_message(chat_id, call.message.id)
                bot.send_message(chat_id, "Mrraaa!🐭☠️")
                mg_count = 1
                mg_user_id = 0
            else:
                mouse_game(chat_id, user_id, call.from_user.first_name)
        else:
            bot.send_message(chat_id, "You are not playing now!")
    elif call_data == "mg_2":
        if user_id == mg_user_id:
            if incorrect == 2:
                bot.delete_message(chat_id, call.message.id)
                bot.send_message(chat_id, "Mrraaa!🐭☠️")
                mg_count = 1
                mg_user_id = 0
            else:
                mouse_game(chat_id, user_id, call.from_user.first_name)
        else:
            bot.send_message(chat_id, "You are not playing now!")
    elif call_data == "mg_3":
        if user_id == mg_user_id:
            if incorrect == 3:
                bot.delete_message(chat_id, call.message.id)
                bot.send_message(chat_id, "Mrraaa!🐭☠️")
                mg_count = 1
                mg_user_id = 0
            else:
                mouse_game(chat_id, user_id, call.from_user.first_name)
        else:
            bot.send_message(chat_id, "You are not playing now!")


bot.infinity_polling(skip_pending=True)

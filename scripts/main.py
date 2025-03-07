import os
import random
import re
from datetime import datetime, timedelta

import telebot
from PIL import Image, ImageDraw, ImageFont
from apscheduler.schedulers.background import BackgroundScheduler
from github import Github
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

API_TOKEN = "5010145034:AAHAqSJkVZ5NnDRKMsOAUjSKBznZGwd94LQ"

bot = telebot.TeleBot(API_TOKEN)

scheduler = BackgroundScheduler()

github = Github("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")
repo = github.get_repo("pkhom/markus-tg-bot")

last_pet_time = {}
last_feed_time = {}

last_message_id = 0

msg_to_delete = 0

mg_count = 1
mg_user_id = 0
mg_incorrect = ""
mg_callbacks = ["mg_right", "mg_left", "mg_up", "mg_down"]

asked_for_food = False
chosen_food = None
unwanted_food = None
foods = ["🍗", "🐟", "🥓", "🍕", "🥛", "🧀", "🥩", "🍖", "🍤"]

sleep = False

games = ["Mouse catch game"]

sleep_stickers = ["CAACAgQAAxkBAAEN7dZnxGJQ5kpGdMUBR7li7kFrK1bUiAACVBQAAmzyAVC_Wb8c8TjbyDYE", "CAACAgQAAxkBAAEN7dhnxGJUT2gE9x3hAZawqUNF87fi_gAC2xEAAhbzAVB8Mx0H91SeGzYE"]

kozjol_chat_id = -1002075990685


def mouse_game(chat_id, user_id, user_name):
    global mg_count, mg_user_id, msg_to_delete, mg_incorrect

    keyboard = InlineKeyboardMarkup()
    left_button = InlineKeyboardButton(text="⬅🐭", callback_data="mg_right")
    right_button = InlineKeyboardButton(text="🐭➡", callback_data="mg_left")
    up_button = InlineKeyboardButton(text="⬆🐭⬆", callback_data="mg_up")
    down_button = InlineKeyboardButton(text="⬇🐭⬇", callback_data="mg_down")
    keyboard.add(up_button, row_width=1)
    keyboard.add(left_button, right_button, row_width=2)
    keyboard.add(down_button, row_width=1)

    if mg_count == 1:
        mg_user_id = user_id
        bot.send_message(chat_id,
                         "🐭*The Mouse Game\n\nMove the mouse toy left and right and I will try to catch it!\nI have 5 attempts*",
                         parse_mode="Markdown")
        mg_incorrect = random.choice(mg_callbacks)
        msg_to_delete = bot.send_message(chat_id, f"Mrra {mg_count}/5", reply_markup=keyboard).id

        mg_count += 1
    elif mg_count < 6 and mg_count != 1:
        bot.delete_message(chat_id, msg_to_delete)
        mg_incorrect = random.choice(mg_callbacks)
        msg_to_delete = bot.send_message(chat_id, f"Mrra {mg_count}/5", reply_markup=keyboard).id

        mg_count += 1
    elif mg_count == 6:
        bot.delete_message(chat_id, msg_to_delete)
        bot.send_message(chat_id, "Mrr, you won... (rep +1)")
        update_reputation(user_id, user_name, 1)
        mg_user_id = None
        mg_count = 1
        mg_incorrect = None

def update_reputation(user_id, user_name, repu: int):
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
        reputation_data[user_id]["rep"] += repu
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

    # Read the file and store data in a dictionary
    if os.stat(file_path).st_size == 0:
        print("File exists but is empty.")
        return
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

    reputation_data_sorted = sorted(reputation_data.items(), key=lambda item: item[1]["rep"], reverse=True)

    return reputation_data_sorted

def sleep_reminder():
    bot.send_message(kozjol_chat_id, "Pßički, čas je spati. Lahko noč😸")
    bot.send_sticker(kozjol_chat_id, random.choice(sleep_stickers))


@bot.message_handler(commands=["pet"])
def pet_command(message: telebot.types.Message):
    current_time = datetime.now()

    if message.from_user.id in last_pet_time:
        last_time = last_pet_time[message.from_user.id]
        time_diff = current_time - last_time

        if time_diff < timedelta(hours=1):
            remaining_time = timedelta(hours=1) - time_diff
            hours, remainder = divmod(remaining_time.seconds, 3600)
            minutes = remainder // 60
            bot.reply_to(message, f"You can pet me again in {minutes} minutes!")
            return

    last_pet_time[message.from_user.id] = current_time

    voice = f"../voiceMsgs/{random.randint(1, 8)}.mp3"
    bot.send_voice(message.chat.id, telebot.types.InputFile(voice), caption="(rep +2)", reply_to_message_id=message.id)

    update_reputation(message.from_user.id, message.from_user.first_name, 2)


@bot.message_handler(commands=["changelog"])
def changelog_command(message: telebot.types.Message):
    text = ""

    commits = repo.get_commits()
    version = commits.totalCount

    for commit in commits:
        commit_message = re.sub(r'([\\_*[\]()~>`#+-=|{}.!])', r'\\\1', commit.commit.message)

        text += (f"*Version {version}:\n*"
                 f"*Changes:*\n"
                 f"{commit_message}\n\n")
        version -= 1

    bot.send_message(message.chat.id, f"{text}", parse_mode="MarkdownV2")

@bot.message_handler(commands=["stats"])
def stats_command(message: telebot.types.Message):
    rep = get_reputation()
    text = "*Reputation:*\n\n"
    if rep is not None:
        for userid, data in rep:
            if data["rep"] == 0:
                continue
            else:
                text += f"[{data['username']}](tg://user?id={userid}): {data['rep']}\n"

        bot.send_message(message.chat.id, text, parse_mode="Markdown")


@bot.message_handler(commands=["rep"])
def rep_command(message: telebot.types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    user_pfps = bot.get_user_profile_photos(user_id)

    get_rep = dict(get_reputation())

    rep = get_rep.get(user_id, {}).get("rep")
    username = get_rep.get(user_id, {}).get("username")

    img = None
    bg = None

    if user_pfps.total_count > 0:
        photo_sizes = user_pfps.photos[0]
        file_id = photo_sizes[1].file_id

        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        with open("../images/pfps/profile_pic.png", "wb") as f:
            f.write(downloaded_file)

        img = Image.open("../images/pfps/profile_pic.png")
    else:
        img = Image.open("../images/nopfp.png")

    try:
        if rep <= 70:
            bg = Image.open("../images/Battle_Card-Bronze.png")
        elif 70 < rep <= 140:
            bg = Image.open("../images/Battle_Card-Silver.png")
        elif 140 < rep <= 210:
            bg = Image.open("../images/Battle_Card-Gold.png")
        elif 210 < rep <= 280:
            bg = Image.open("../images/Battle_Card-Diamond.png")
        elif 280 < rep <= 350:
            bg = Image.open("../images/Battle_Card-Mythic.png")
        elif 350 < rep <= 420:
            bg = Image.open("../images/Battle_Card-Legendary.png")
        elif 420 < rep <= 490:
            bg = Image.open("../images/Battle_Card-Masters.png")
        elif rep > 490:
            bg = Image.open("../images/Battle_Card-Pro.png")

        img_w, img_h = img.size
        bg_w, bg_h = bg.size

        bg.paste(img, ((bg_w - img_w) // 2, (bg_h - img_h) // 2))

        #add text
        add_text = ImageDraw.Draw(bg)
        font = ImageFont.truetype("../fonts/SeymourOne-Regular.ttf", 65)

        add_text.text((bg_w//2, 475), str(rep), fill=(255, 255, 255), font=font, stroke_fill=(0, 0, 0), stroke_width=5, anchor="mm")
        add_text.text((bg_w//2, 125), str(username), fill=(255, 255, 255), font=font, stroke_fill=(0, 0, 0), stroke_width=5, anchor="mm")

        bg.save("../images/pfps/edited.png")

        bot.send_photo(chat_id, telebot.types.InputFile("../images/pfps/edited.png"))
    except IOError:
        pass


@bot.message_handler(commands=["play"])
def play_command(message: telebot.types.Message):
    global msg_to_delete

    games_list_keyboard = InlineKeyboardMarkup()
    mouse_game_btn = InlineKeyboardButton("Mouse catch game", callback_data="play_mouse")
    games_list_keyboard.add(mouse_game_btn)

    bot.send_message(message.chat.id, "List of available games.", reply_markup=games_list_keyboard)


@bot.message_handler(commands=["sleep"])
def sleep_command(message: telebot.types.Message):
    global sleep

    user_id = message.from_user.id
    chat_id = message.chat.id
    try:
        command = message.text.split(" ")[1]
    except:
        bot.send_message(chat_id, "CommandSyntaxError: sleep -> sleep int(0,1))")
        return


    if user_id == 1874212422:
        if command == "0":
            sleep = False
            bot.send_message(chat_id, "The group is open again.\nGood morning. Mrrra🥰")
        elif command == "1":
            sleep = True
            bot.send_message(chat_id, "It's time to sleep, the group is closed.\nGood night. Mrreow🥰")
    else:
        bot.send_message(chat_id, "Only Pašica can use this command")


@bot.message_handler(commands=["info"])
def info_command(message: telebot.types.Message):
    commits = repo.get_commits()

    last_commit = commits[0]
    version = 0

    for _ in commits:
        version += 1

    food = ""
    for emoji in foods:
        food += f"{emoji}, "

    commit_message = last_commit.commit.message

    bot.send_message(message.chat.id, f"Markus Version {version}\n"
                                      f"\n"
                                      f"*Latest update:*\n"
                                      f"{commit_message}\n"
                                      f"\n"
                                      f"*Reputation ranks:*\n"
                                      f"0-70: Bronze\n"
                                      f"70-140: Silver\n"
                                      f"140-210: Gold\n"
                                      f"210-280: Diamond\n"
                                      f"280-350: Mythic\n"
                                      f"350-420: Legendary\n"
                                      f"420-490: Master\n"
                                      f"490+: Pro\n"
                                      f"\n"
                                      f"*Supported foods:*\n"
                                      f"{food}", parse_mode="Markdown")


@bot.message_handler(func=lambda message: True)
def update_message(message : telebot.types.Message):
    global last_message_id, asked_for_food, chosen_food, unwanted_food, foods
    message_text = message.text.lower()
    chat_id = message.chat.id
    message_id = message.id
    message_user = message.from_user
    user_id = message_user.id
    username = message_user.username
    user_firstname = message_user.first_name

    if sleep:
        if chat_id == 1874212422:
            msg = message_text.split(";") # chat_id;message
            forward_to_chat = msg[0]
            text = msg[1]

            bot.send_message(forward_to_chat, f"Pašica said: {text}")
        else:
            if user_id != bot.bot_id:
                bot.delete_message(chat_id, message_id)
            return

    # debug
    print(f"Message id: {message_id}\n"
          f"Chat id: {chat_id}\n"
          f"From User: {user_id}, {username}, {user_firstname}\n"
          f"Text: {message_text}\n")

    #feed request
    if random.random() < 0.02:
        last_message_id = bot.send_message(chat_id, "Mrraw🙏").id
        asked_for_food = True
        chosen_food = random.choice(foods)
        foods.remove(chosen_food)
        unwanted_food = random.choice(foods)
        foods.append(chosen_food)
        print(last_message_id)
        print(f"+:{chosen_food}     -:{unwanted_food}")

    #feed
    current_time = datetime.now()

    if ((message.reply_to_message is not None) and (message.reply_to_message.id == last_message_id) and
            (message_text in foods)):
        if asked_for_food:
            last_message_id = 0
            asked_for_food = False
            if message_text == chosen_food:
                update_reputation(user_id, message_user.first_name, 2)
                bot.send_message(chat_id, "Mrrra🥰 (rep +2)", reply_to_message_id=message_id)
            elif message_text == unwanted_food:
                update_reputation(user_id, message_user.first_name, -1)
                bot.send_message(chat_id, "Mea😠 (rep -1)", reply_to_message_id=message_id)
            else:
                update_reputation(user_id, message_user.first_name, 1)
                bot.send_message(chat_id, "Meow🥰 (rep +1)", reply_to_message_id=message_id)
        else:
            if user_id in last_feed_time:
                last_time = last_feed_time[user_id]
                time_diff = current_time - last_time

                if time_diff < timedelta(minutes=15):
                    remaining_time = timedelta(minutes=15) - time_diff
                    hours, remainder = divmod(remaining_time.seconds, 3600)
                    minutes = remainder // 60
                    bot.reply_to(message, f"You can feed me again in {minutes} minutes!")
                    return

            last_feed_time[message.from_user.id] = current_time

            bot.send_message(chat_id, "Mrrra🥰 (rep +1)", reply_to_message_id=message_id)
            last_message_id = 0
            update_reputation(user_id, message_user.first_name, 1)

    elif (message.reply_to_message is not None) and (message.reply_to_message.id == last_message_id) and (message_text == "meow"):
        last_message_id = 0
        bot.send_message(chat_id, "Prrrr")

    elif ("markus" in message_text) or ("маркус" in message_text):
        last_message_id = bot.send_message(chat_id, text="Meow?", reply_to_message_id=message_id).id

    elif message_text == "ksksks" or message_text == "кскскс":
        bot.send_message(chat_id, "Mrrraaa")


@bot.callback_query_handler(func=lambda call: True)
def callback(call: CallbackQuery):
    global mg_count, mg_user_id

    call_data = call.data
    chat_id = call.message.chat.id
    call_user = call.from_user
    user_id = call_user.id

    mg_playagain_keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton("Play again", callback_data="play_mouse"))

    if call_data == "play_mouse":
        bot.delete_message(chat_id, call.message.id)
        mouse_game(chat_id, user_id, call.from_user.first_name)


    if call_data.startswith("mg"):
        if user_id == mg_user_id:
            if call_data == mg_incorrect:
                bot.delete_message(chat_id, call.message.id)
                bot.send_message(chat_id, "Mrraaa!🐭☠️", reply_markup=mg_playagain_keyboard)
                mg_count = 1
                mg_user_id = 0
            else:
                mouse_game(chat_id, user_id, call.from_user.first_name)
        else:
            bot.send_message(chat_id, f"[{call_user.first_name}](tg://user?id={call_user.first_name}), You are not playing now!")


scheduler.add_job(sleep_reminder, 'cron', day_of_week="mon,tue,wed,thu,sun", hour=22, minute=0)
scheduler.start()

bot.infinity_polling(skip_pending=True)

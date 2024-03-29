import telebot
from telebot import types
import info
from info import SURVEY
from info import SCALES
import json
from config import TOKEN
# Какой жанр игр тебе больше подходит?
# Токен находится в файле config.py

bot = telebot.TeleBot(TOKEN)

#json файл
path_file = "information.json"
scale = 0
users = {}

hideKeyboard = types.ReplyKeyboardRemove()

keyboard = types.ReplyKeyboardMarkup(
    row_width=3,
    resize_keyboard=True
)
keyboard.add(*["/start", "/start_survey", "/help", "/result"])

def save_data(users: dict, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(users, fp=f, ensure_ascii=False, indent=2)

def load_data(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            users = json.load(fp=f)
        print(users)
    except:
        users = {}
    return users

def add_user(user_id: int) -> None:
    if user_id not in users:
        users[user_id] = {}
        users[user_id]['q_num'] = 0
        for s in SCALES:
            users[user_id][s] = 0

@bot.message_handler(commands=["start"])
def start_command(message):
    user_id = message.from_user.id
    add_user(user_id)
    bot.send_message(
        chat_id=message.from_user.id,
        text=info.START_TEXT,
        parse_mode="HTML",
        reply_markup=keyboard
    )

@bot.message_handler(commands=["help"])
def help_command(message):
    bot.send_message(
        chat_id=message.from_user.id,
        text=info.HELP_TEXT,
        parse_mode="HTML",
        reply_markup=keyboard
    )

@bot.message_handler(commands=["start_survey"])
def survey_command(message):
    user_id = message.from_user.id
    add_user(user_id)

    if message == '/start_survey':
        bot.send_message(
            chat_id=message.from_user.id,
            text="Отвечай на вопросы кнопками.",
            parse_mode="HTML",
            reply_markup=hideKeyboard
        )
        for s in SCALES:
            users[user_id][s] = 0
        users[user_id]['q_num'] = 0

    if users[user_id]['q_num']:
        try:
            prev_question = SURVEY[users[user_id]['q_num'] - 1]
            print(prev_question, message.text, prev_question['a'][message.text])
            for i in range(len(SCALES)):
                users[user_id][i] += prev_question['a'][message.text][i]
                save_data(users, path_file)
        except KeyError:
            bot.send_message(
                message.from_user.id,
                f"Странный ответ, интересный результат получится."
            )

    if users[user_id]['q_num'] >= len(SURVEY):
        bot.register_next_step_handler(message, result_command)
        bot.send_message(
            message.from_user.id,
            "Анкета закончилась.\n"
            "Результаты смотри в /result",
            parse_mode="HTML",
            reply_markup=hideKeyboard
        )
        users[user_id]['q_num'] = 0
        return

    bot.register_next_step_handler(message, survey_command)
    q_num = users[user_id]['q_num']
    question = SURVEY[q_num]
    answers_keyboard = types.ReplyKeyboardMarkup(
        row_width=len(question['a']),
        resize_keyboard=True
    )
    answers_keyboard.add(*question['a'])
    bot.send_message(
        message.from_user.id,
        f"Вопрос № {q_num + 1}:\n"
        f"{SURVEY[q_num]['q']}",
        parse_mode="HTML",
        reply_markup=answers_keyboard
    )
    users[user_id]['q_num'] += 1
def strategy_c(message):
    try:
        user_id = str(message.from_user.id)
        path = "information.json"
        user = load_data(path)
        number_strategy = user[user_id]['0']
        print(number_strategy)
        return int(number_strategy)
    except:
        return 0
def action_c(message):
    try:
        user_id = str(message.from_user.id)
        path = "information.json"
        user = load_data(path)
        number_action = user[user_id]['1']
        return int(number_action)
    except:
        return 0
def rpg_c(message):
    try:
        user_id = str(message.from_user.id)
        path = "information.json"
        user = load_data(path)
        number_rpg = user[user_id]['2']
        return int(number_rpg)
    except:
        return 0
@bot.message_handler(commands=["result"])
def result_command(message):
    user_id = message.from_user.id
    add_user(user_id)

    strategy = strategy_c(message)
    action = action_c(message)
    rpg = rpg_c(message)

    if strategy == rpg and strategy == action:
        win = "Все равны. Ты возможно не прошёл анкету или у тебя отсутствует файл 'information.json'."
    elif rpg < action == strategy and strategy > rpg:
        win = "Ничья между стратегией и экшеном"
    elif action < strategy == rpg > action:
        win = "Ничья между стратегией и РПГ"
    elif rpg > strategy == action and action > strategy:
        win = "Ничья между РПГ и экшеном"
    elif strategy > all([action, rpg]):
        win = "Стратегия"
    elif action > all([strategy, rpg]):
        win = "Экшн"
    elif rpg > all([strategy, action]):
        win = "РПГ"
    else:
        win = "Как?"
    bot.send_message(
        message.from_user.id,
        f"Твой результат, {message.from_user.first_name}!:\n\n"
        f"{win}\n\n"
        "Чтобы перезапустить /start_survey",
        parse_mode="HTML",
        reply_markup=keyboard
    )

if __name__ == "__main__":
    bot.polling()

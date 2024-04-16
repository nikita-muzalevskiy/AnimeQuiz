import random
import telebot
import Mongo as m
from telebot import types
from telebot.async_telebot import AsyncTeleBot
import asyncio
import DB
import os.path

bot = AsyncTeleBot('') # enter your TG-token

@bot.message_handler(commands=['start'])
async def start(message):
    await bot.send_message(message.from_user.id, "👋 Привет! Я бот, который проводит тесты по аниме! Я могу тупить и лагать, да и вообще я еще не доделан... Но я постараюсь для тебя!")
    await selectTest(message.from_user.id)

# реакции на сообщения
@bot.message_handler(content_types=['text'])
async def get_text_messages(message):
    if message.text == 'Hi':
        print('Hi')

@bot.callback_query_handler(func=lambda call: True) #вешаем обработчик событий на нажатие всех inline-кнопок
async def callback_inline(call):
    if call.data: #проверяем есть ли данные если да, далаем с ними что-то
        print(f'ПОЛУЧИЛИ КОЛЛБЭК: {call.data}')
        user, act, param = call.data.split("/")[0], call.data.split("/")[1], call.data.split("/")[2]
        print(f'USER: {user}')
        # Получили выбранный тест
        if act == '0':
            await makeTestForUser(user, param)
        # Получили выбранного персонажа
        if act == '1':
            await nextDuel(user, param)
        # Получили запрос на статистку
        if act == '2':
            await getStat(user, param)
        # Получили запрос на новый тест
        if act == '3':
            await selectTest(user)

async def getStat(user, param):
    print(DB.getStatistics(param))
    stat = DB.getStatistics(param)
    stat_mess = 'Персонажи и их процент побед:\n'
    for s in stat:
        stat_mess = stat_mess + f'{s[0]} - {int(s[1])}%\n'
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    bNewTest = types.InlineKeyboardButton(text='Пройти новый тест', callback_data=f"{user}/3/")
    keyboard.add(bNewTest)
    await bot.send_message(user, stat_mess, reply_markup=keyboard)

async def nextDuel(user, param):
    dbase = m.MongoDB()
    user_info = dbase.getDocument(str(user))
    next_duel = user_info['duels'][0]
    if param not in next_duel:
        print('Пользователь, которого выбрал пользователь, не ожидался')
    else:
        if (next_duel[0] == param):
            loser = next_duel[1]
        else:
            loser = next_duel[0]
        user_info['winners'].append(param)
        user_info["characters"][param][0] += 1
        user_info["characters"][param][1] += 1
        user_info["characters"][loser][1] += 1
        user_info['duels'].pop(0)
        await checkEndOfRound(user, user_info)
        dbase.updateOne(str(user), user_info)
        dbase = m.MongoDB()
        user_info = dbase.getDocument(str(user))
        await duel(user, user_info)
        print(f'У пользователя с id = {user} победил {param}')

async def selectTest(user):
    list = DB.getAnimeList()
    print(list)
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    for a in list:
        button = types.InlineKeyboardButton(text=a[0], callback_data=f"{user}/0/{a[0]}")
        keyboard.add(button)
    await bot.send_message(user, "По какому аниме будем проходить тест?", reply_markup=keyboard)

async def checkEndOfRound(user, user_info):
    if len(user_info['duels']) == 0:
        print('Раунд закончен!')
        user_info['round'] += 1
        if len(user_info['winners']) == 1:
            print('Тест закончен!')
            if os.path.isfile(f"pic/{user_info['anime']}/{str(user_info['winners'][0])}.jpg"):
                await bot.send_photo(user, open(f"pic/{user_info['anime']}/{str(user_info['winners'][0])}.jpg", 'rb'))
            keyboard = types.InlineKeyboardMarkup(row_width=2)
            bNewTest = types.InlineKeyboardButton(text='Пройти новый тест', callback_data=f"{user}/3/")
            bStatistics = types.InlineKeyboardButton(text='Статистика этого теста', callback_data=f"{user}/2/{user_info['anime']}")
            keyboard.add(bNewTest, bStatistics)
            await bot.send_message(user, f"Тест закончен!\nПобедитель - {user_info['winners'][0]}", reply_markup=keyboard)
            DB.changeStatistics(user_info)
            return
        random.shuffle(user_info['winners'])
        for i in range(0, len(user_info['winners']), 2):
            user_info['duels'].append([user_info['winners'][i], user_info['winners'][i + 1]])
        user_info['winners'] = []

async def makeTestForUser(user, anime):
    characters = DB.getCharacterList(anime)
    random.shuffle(characters)
    characters2 = {}
    for c in characters:
        characters2[c[0]] = [0, 0]
    duels = []
    for i in range(0, len(characters), 2):
        duels.append([characters[i][0], characters[i+1][0]])
    print(f'characters2: {characters2}')
    dbase = m.MongoDB()
    dbase.createUser(str(user))
    dbase.updateUser(str(user), {"user": str(user), "anime": anime, "round": 1, "duels": duels, "winners": [], "characters": characters2})
    user_info = dbase.getDocument(str(user))
    await duel(user, user_info)

#Функция принимает id пользователя и его данные в Монго. Отправляет пользователю сообщение со следующим выбором
async def duel(user, user_info):
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    b1 = types.InlineKeyboardButton(text=str(user_info['duels'][0][0]), callback_data=f"{user}/1/{str(user_info['duels'][0][0])}")
    b2 = types.InlineKeyboardButton(text=str(user_info['duels'][0][1]), callback_data=f"{user}/1/{str(user_info['duels'][0][1])}")
    keyboard.add(b1, b2)
    file1, file2 = f"pic/{user_info['anime']}/{str(user_info['duels'][0][0])}.jpg", f"pic/{user_info['anime']}/{str(user_info['duels'][0][1])}.jpg"
    if os.path.exists(file1) and os.path.exists(file2):
        await bot.send_media_group(user, [telebot.types.InputMediaPhoto(open(file1, "rb")), telebot.types.InputMediaPhoto(open(file2, "rb"))])
    await bot.send_message(user, f"Раунд {user_info['round']}!\nЭтап {len(user_info['winners'])+1}/{len(user_info['duels'])+len(user_info['winners'])}", reply_markup=keyboard)

asyncio.run(bot.polling())
# bot.polling(none_stop=True, interval=0) #обязательная для работы бота часть
def print_hi(name):
    print(f'Hi, {name}')

if __name__ == '__main__':
    print_hi('PyCharm')
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
import config

import math

logging.basicConfig(level=logging.INFO)

storage = MemoryStorage()
token = Bot(token=config.bot_token)
bot = Dispatcher(token, storage=storage)

users = config.fake_database['users']

'''class Form(StatesGroup):
    name = State()  '''

@bot.message_handler(regexp='Меню')
async def menu(message):
    markup = types.reply_keyboard.ReplyKeyboardMarkup(row_width=2)
    text = f'Привет @{message.from_user.username}, я бот, который может управлять кошельками и производить транзакции между ними'
    btn1 = types.KeyboardButton('Кошелек')
    btn2 = types.KeyboardButton('Перевести')
    btn3 = types.KeyboardButton('История')
    markup.add(btn1, btn2, btn3)
    await message.answer(text, reply_markup=markup)

@bot.message_handler(commands=['start'])
async def start_message(message):
    markup = types.reply_keyboard.ReplyKeyboardMarkup(row_width=2)
    btn1 = types.KeyboardButton('Кошелек')
    btn2 = types.KeyboardButton('Перевести')
    btn3 = types.KeyboardButton('История')
    markup.add(btn1, btn2, btn3)
    text = f'Привет @{message.from_user.username}, я бот, который может управлять кошельками и производить транзакции между ними'
    await message.answer(text, reply_markup=markup)

@bot.message_handler(regexp='Кошелек')
async def wallet(message):
    markup = types.reply_keyboard.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton('Меню')   
    markup.add(btn1)
    balance = 0    
    text = f'Ваш баланс: {balance}'
    await message.answer( text, reply_markup=markup)

@bot.message_handler(regexp='Перевести')
async def transaction(message):
    markup = types.reply_keyboard.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton('Меню')   
    markup.add(btn1)   
    text = 'Перевод пока не возможен'
    await message.answer(text, reply_markup=markup)

@bot.message_handler(regexp='История')
async def transaction(message):
    markup = types.reply_keyboard.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton('Меню')   
    markup.add(btn1)   
    text = 'История транзакций пока не доступна'
    await message.answer(text, reply_markup=markup)

@bot.message_handler(regexp='Я')
async def print_me(message):
    markup = types.reply_keyboard.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton('Меню')
    markup.add(btn1)
    print(message.from_user.id)
    text = f'Ты: {message.from_user.id}'
    await message.answer(text, reply_markup=markup)

@bot.message_handler(lambda message: message.from_user.id in config.bot_admin_id and message.text == "Админка")
async def admin_panel(message):
    markup = types.reply_keyboard.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton('Общий баланс')
    btn2 = types.KeyboardButton('Все пользователи')
    btn3 = types.KeyboardButton('Данные по пользователю')
    btn4 = types.KeyboardButton('Удалить пользователя')
    markup.add(btn1, btn2, btn3, btn4)
    text = f'Админ-панель'
    await message.answer(text, reply_markup=markup)

@bot.message_handler(lambda message: message.from_user.id in config.bot_admin_id and message.text == 'Все пользователи')
async def all_users(message):
    total_pages = math.ceil(len(users) / 4)
    current_page = 1
    text = 'Пользователи:'
    inline_markup = types.InlineKeyboardMarkup()
    for user in users[:current_page*4]:
        inline_markup.add(types.InlineKeyboardButton(
            text=user['name'],
            callback_data=f'user_{user["id"]}'
        ))
    current_page += 1
    inline_markup.row(
        types.InlineKeyboardButton(text=f'{current_page-1}/{total_pages}', callback_data='None'),
        types.InlineKeyboardButton(text='Вперёд', callback_data=f'next_{current_page}')
    )
    await message.answer(text, reply_markup=inline_markup)
@bot.callback_query_handler(lambda call: True)
async def callback_query(call):
    query_type = call.data.split('_')[0]
    if query_type == 'next':
        total_pages = math.ceil(len(users) / 4)
        current_page = int(call.data.split('_')[1])
        inline_markup = types.InlineKeyboardMarkup()
        if current_page*4 >= len(users):
            for user in users[current_page*4-4:len(users) + 1]:
                inline_markup.add(types.InlineKeyboardButton(
            text=user['name'],
            callback_data=f'user_{user["id"]}'
            ))
            current_page -= 1
            inline_markup.row(
                types.InlineKeyboardButton(text='Назад', callback_data=f'prev_{current_page}'),
                types.InlineKeyboardButton(text=f'{current_page+1}/{total_pages}', callback_data='None')
            )
            await call.message.edit_text(text="Пользователи:",
                              reply_markup=inline_markup)
            return
        for user in users[current_page*4-4:current_page*4]:
            inline_markup.add(types.InlineKeyboardButton(
            text=user['name'],
            callback_data=f'user_{user["id"]}'
        ))
        current_page += 1
        inline_markup.row(
            types.InlineKeyboardButton(text='Назад', callback_data='prev_page'),
            types.InlineKeyboardButton(text=f'{current_page-1}/{total_pages}', callback_data='None'),
            types.InlineKeyboardButton(text='Вперёд', callback_data=f'next_{current_page}')
        )
        await call.message.edit_text(text="Пользователи:",
                              reply_markup=inline_markup)
    if query_type == 'prev':
        total_pages = math.ceil(len(users) / 4)
        current_page = int(call.data.split('_')[1])
        inline_markup = types.InlineKeyboardMarkup()
        if current_page == 1:
            for user in users[0:current_page*4]:
                inline_markup.add(types.InlineKeyboardButton(
                text=user['name'],
                callback_data=f'user_{user["id"]}'
                ))
            current_page += 1
            inline_markup.row(
                types.InlineKeyboardButton(text=f'{current_page-1}/{total_pages}', callback_data='None'),
                types.InlineKeyboardButton(text='Вперёд', callback_data=f'next_{current_page}')
            )
            await call.message.edit_text(text="Пользователи:",
                              reply_markup=inline_markup)
            return
        for user in users[current_page*4-4:current_page*4]:
            inline_markup.add(types.InlineKeyboardButton(
            text=user['name'],
            callback_data=f'user_{user["id"]}'
            ))
        current_page -= 1
        inline_markup.row(
            types.InlineKeyboardButton(text='Назад', callback_data=f'prev_{current_page}'),
            types.InlineKeyboardButton(text=f'{current_page+1}/{total_pages}', callback_data='None'),
            types.InlineKeyboardButton(text='Вперёд', callback_data=f'next_{current_page}'),
        )
        await call.message.edit_text(text="Пользователи:",
                              reply_markup=inline_markup)
    if query_type == 'user':
        current_page = int(call.data.split('_')[1])
        user_id = call.data.split('_')[1]
        inline_markup = types.InlineKeyboardMarkup()
        for user in users:
            if str(user['id']) == user_id:
                inline_markup.add(
                    types.InlineKeyboardButton(text='Назад', callback_data=f'users_{current_page}'),
                    types.InlineKeyboardButton(text='Удалить пользователя', callback_data=f'delete_user_{user_id}')
                )
                await call.message.edit_text(
                    text=f'Данные по пользователю\n'
                    f'ID:{user["id"]}\n'
                    f'Name:{user["name"]}\n'
                    f'Nick:{user["nick"]}\n'
                    f'Balance:{user["balance"]}\n',
                    reply_markup=inline_markup
                )
                break
    if query_type == 'users':
        total_pages = math.ceil(len(users) / 4)
        current_page = 1
        inline_markup = types.InlineKeyboardMarkup()
        for user in users[:current_page*4]:
            inline_markup.add(types.InlineKeyboardButton(
                text=user["name"],
                callback_data=f'user_{user["id"]}'
            ))
        current_page += 1
        inline_markup.row(
            types.InlineKeyboardButton(text=f'{current_page-1}/{total_pages}', callback_data='None'),
            types.InlineKeyboardButton(text='Вперёд', callback_data=f'next_{current_page}')
        )
        await call.message.edit_text(
            text='Пользователи:',
            reply_markup=inline_markup
        )
    if query_type == 'delete' and call.data.split('_')[1] == 'user':
        total_pages = math.ceil(len(users) / 4)
        user_id = int(call.data.split('_')[2])
        current_page = 1
        for i, user in enumerate(users):
            if user['id'] == user_id:
                users.pop(i)
            inline_markup = types.InlineKeyboardMarkup()
        for user in users[:current_page*4]:
            inline_markup.add(types.InlineKeyboardButton(
                text=user["name"],
                callback_data=f'user_{user["id"]}'
            ))
        current_page += 1
        inline_markup.row(
            types.InlineKeyboardButton(text=f'{current_page-1}/{total_pages}', callback_data='None'),
            types.InlineKeyboardButton(text='Вперёд', callback_data=f'next_{current_page}')
        )
        await call.message.edit_text(
            text='Пользователи:',
            reply_markup=inline_markup
        )

@bot.message_handler(lambda message: message.from_user.id in config.tg_bot_admin and message.text == 'Общий баланс')
async def total_balance(message):
    markup = types.InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.InlineKeyboardButton('Меню')
    btn2 = types.InlineKeyboardButton('Админка')
    markup.add(btn1, btn2)
    balance = 0
    for user in users:
        balance += user['balance']
    text = f'Общий баланс: {balance}'
    await message.answer(text, reply_markup=markup)


if __name__ == '__main__':
    executor.start_polling(bot, skip_updates=True)
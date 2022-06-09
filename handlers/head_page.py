from aiogram import types
from aiogram.dispatcher.filters import Command, Text
from aiogram.utils.emoji import emojize

from keyboards.reply_keyboard import MAIN_MENU
from settings.config import KEYBOARD, DP, ADMINS_ID_LST, BOT


async def head_page(message: types.Message):
    '''Обработчик для главного меню бота'''

    await message.answer(emojize(':fuel_pump:Добро пожаловать в кафе Полный бак.'
                                 '\nЭтот бот поможет Вам оформить заказ дистанционно.'), reply_markup=MAIN_MENU)


async def return_to_hade_page(message: types.Message):
    '''Реакция бота на нажатие кнопки ГЛАВНАЯ'''

    await message.answer(f'Вы перешли к главному меню', reply_markup=MAIN_MENU)


async def send_media_id(message: types.Message):
    '''Обработчик для отправки ID присланного боту файла'''

    if message.from_user.id in ADMINS_ID_LST:
        await BOT.send_message(
            chat_id=message.from_user.id,
            text=f'ID файла: {message.photo[-1].file_id}'
        )


def register_head_page_handlers():
    '''Функция для регистрации обработчиков'''

    DP.register_message_handler(head_page, Command(['start', 'home',]))
    DP.register_message_handler(return_to_hade_page, Text(equals=[KEYBOARD['HEAD_PAGE']]))
    DP.register_message_handler(send_media_id, content_types=types.ContentTypes.PHOTO)

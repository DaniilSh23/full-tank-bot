import os
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from emoji import emojize
import re
from dotenv import load_dotenv

load_dotenv()

# токен выдается при регистрации приложения
TOKEN = os.environ.get('TOKEN', '5265303938:AAE1daGp-VJR0R15J9tHksR38hQlbCXMYdU')
PAY_TOKEN = os.environ.get('PAY_TOKEN')

# Телеграм ID админов
ADMINS_ID_LST = [1978587604]
STAFF_ID = 1978587604

# абсолютный путь до текущей директории этого файла
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

COUNT = 0

# кнопки управления
KEYBOARD = {
    'CHOOSE_GOODS': emojize(':hamburger: Выбрать товар'),
    'INFO': emojize(':speech_balloon: О магазине'),
    'BASKET': emojize(':wastebasket: Корзина'),
    'MY_ORDER': emojize(':spiral_notepad: Мои заказы'),
    'HEAD_PAGE': emojize(":house_with_garden: Главная"),
    'MAKE_AN_ORDER': emojize('✅ ОФОРМИТЬ'),
    'ORDER_COMPLETE': emojize('✅ ЗАКАЗ ВЫПОЛНЕН'),
    'X_ORDER': emojize('❌ ОТМЕНИТЬ ЗАКАЗ'),
    'X_BASKET': emojize('❌:wastebasket: ОЧИСТИТЬ'),
    'BACK_STEP_ITEM': emojize('◀️Назад'),
    'NEXT_STEP_ITEM': emojize('▶️ Вперёд'),
    'BACK_STEP_CATEG': emojize('⏪Назад'),
    'NEXT_STEP_CATEG': emojize('⏩Вперёд'),
    'PLUS_ITEM': emojize(':plus:'),
    'MINUS_ITEM': emojize(':minus:'),
    'STANDARD_BUTTON': emojize(':fuel_pump:'),
    'PAY': emojize(':yen_banknote:ОПЛАТИТЬ'),
    'ORDER_GIVEN': emojize(':package:ЗАКАЗ ПЕРЕДАН'),
}

# названия команд
COMMANDS = {
    'START': "start",
    'HELP': "help",
}

# URL адреса для запросов к АPI бота
DOMAIN_NAME = 'https://auto-bot-api.herokuapp.com/'
ITEMS_CATEGORIES_API_URL = f'{DOMAIN_NAME}cafe_api/categories/'
ITEMS_LST_API_URL = f'{DOMAIN_NAME}cafe_api/items/'
BASKET_API_URL = f'{DOMAIN_NAME}cafe_api/basket/'
ADD_ITEMS_IN_BASKET_API_URL = f'{DOMAIN_NAME}cafe_api/add_items_in_basket/'
REMOVE_ITEMS_FROM_BASKET_API_URL = f'{DOMAIN_NAME}cafe_api/remove_items_from_basket/'
ORDERS_API_URL = f'{DOMAIN_NAME}cafe_api/orders/'
REMOVE_ORDER_API_URL = f'{DOMAIN_NAME}cafe_api/remove_order/'
CLEAR_BASKET_API_URL = f'{DOMAIN_NAME}cafe_api/clear_basket/'
ITEMS_DETAIL_API_URL = f'{DOMAIN_NAME}cafe_api/item_detail/?item_id='
PAY_ORDER_INFO = f'{DOMAIN_NAME}cafe_api/pay_order/'
ORDER_ARCHIVE = f'{DOMAIN_NAME}cafe_api/order_archive/'
ADMIN_PANEL = f'{DOMAIN_NAME}admin/'

# объекты: бот, диспатчер, сторэдж для машины состояний
BOT = Bot(token=TOKEN, parse_mode='HTML')
STORAGE = MemoryStorage()
DP = Dispatcher(BOT, storage=STORAGE)

# регулярные выражения для бота
# RE_CATEGORY_LINK_PATTERN = re.compile(r'\?\w*\S\w*')
RE_CATEGORY_LINK_PATTERN = re.compile(r'\?.*')

# опции доставки
DELIVERY_FROM_CAFE = types.ShippingOption(
    id='delivery-form-cafe',
    title='Доставка из кафе',
    prices=[
        types.LabeledPrice(
            'Стандартная доставка', 15000
        )
    ]
)

PICKUP_FROM_CAFE = types.ShippingOption(
    id='pickup-form-cafe',
    title='Забрать самостоятельно',
    prices=[
        types.LabeledPrice(
            'Самовывоз', 0
        )
    ]
)

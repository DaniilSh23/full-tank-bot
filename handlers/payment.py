from aiogram import types
from aiogram.dispatcher.filters import Text
from aiogram.types import ContentType

from settings.config import DP, KEYBOARD, PAY_TOKEN, BOT, DELIVERY_FROM_CAFE, PICKUP_FROM_CAFE


@DP.message_handler(Text(equals=KEYBOARD['PAY']))
async def test_payments(message: types.Message):
    '''Пробный обработчик для платежей.'''

    print('Попали в тестовый платёж.')
    # amount принимает рубли в копейках, т.е. тут мы передали 123 рубля, а не 12 300 р.
    price = types.LabeledPrice(label='название товара', amount=12300)
    # проверяем, что мы работаем с тестовой версией платежей
    if PAY_TOKEN.split(':')[1] == 'TEST':
        await message.answer(text='Это тестовый платёж.')
        # высылаем платёж
        await BOT.send_invoice(
            chat_id=message.chat.id,
            title='Заголовок',
            description='Описание',
            provider_token=PAY_TOKEN,
            currency='rub',
            # photo_url='https://avatarko.ru/img/kartinka/33/multfilm_lyagushka_32117.jpg',
            # photo_height=512, # без него может не показаться изображение(размер != None)
            # photo_width=512,
            # photo_size=512,
            need_name=True,     # спрашиваем у пользователя Имя
            need_phone_number=True,     # спрашиваем номер телефона
            need_shipping_address=True,    # адрес доставки
            is_flexible=True,   # True, елси конечная цена зависит от доставки
            prices=[price],     # это поле принимает список из объектов types.LabeledPrice
            # это какой-то параметр, который как-то связан с квитанцией,
            # я толком не понял, но тут просто указываем товар(или заказ)
            start_parameter='test-payment',
            # этот параметр указывают, чтобы идентифицировать платеж,
            # пользователю не показывается, но мы можем прочитать при успешном платеже
            # он уникален для каждого товара(заказа)
            payload='some-invoice-payload',
        )


@DP.shipping_query_handler()
async def choose_shipping(query: types.ShippingQuery):
    '''Обработчик для выбора способа доставки.'''

    print('Попали в выбор способа доставки.')
    await BOT.answer_shipping_query(
        shipping_query_id=query.id,
        shipping_options=[
            DELIVERY_FROM_CAFE,
            PICKUP_FROM_CAFE
        ],
        ok=True
    )


@DP.pre_checkout_query_handler()
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    '''Обработчик для апдейта PreCheckoutQuery,
    на который необходимо ответить в теч. 10 сек. положительно или отрицательно.'''

    print('Попали в предварительную обработку платежа.')
    await BOT.answer_pre_checkout_query(pre_checkout_query_id=pre_checkout_query.id, ok=True)


@DP.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def process_successful_payment(message: types.Message):
    '''Обработчик для апдейта об успешной оплате.'''

    print('Попали в successful_payment:')
    pmnt = message.successful_payment.to_python()
    for key, val in pmnt.items():
        print(f'{key} = {val}')

        # вот, что у нас в этом цикле итерируется
        # currency = RUB
        # total_amount = 27300
        # invoice_payload = some - invoice - payload
        # shipping_option_id = delivery - form - cafe
        # order_info = {'name': 'Егор хуй с гор', 'phone_number': '79964510994',
        #               'shipping_address': {'country_code': 'RU', 'state': 'Крым', 'city': 'Севастополь',
        #                                    'street_line1': 'Также', 'street_line2': 'Героев Сталинграда д.53 кв. 45',
        #                                    'post_code': '299059'}}
        # telegram_payment_charge_id = 5265303938_1978587604_20329
        # provider_payment_charge_id = 5265303938_1978587604_20329

    await BOT.send_message(
        message.chat.id,
        'Вы успешно оплатили: {currency}, итоговая цена {total_amount}'.format(
            total_amount=message.successful_payment.total_amount // 100,
            currency=message.successful_payment.currency
        )
    )


def register_payments_handlers():
    # DP.register_message_handler(test_payments, Text(equals=KEYBOARD['PAY']))
    # DP.pre_checkout_query_handler(process_pre_checkout_query, func=lambda query: True)
    pass

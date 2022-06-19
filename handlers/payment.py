from aiogram import types
from aiogram.types import ContentType, CallbackQuery
from aiogram.utils.emoji import emojize

from another.request_to_API import get_info_about_orders, post_req_for_add_pay_info_about_order, post_req_for_add_order
from keyboards.callback_data_bot import callback_for_orders_lst
from keyboards.inline_keyboard import stuff_formation_order_complete_inline
from settings.config import DP, PAY_TOKEN, BOT, DELIVERY_FROM_CAFE, PICKUP_FROM_CAFE, ADMINS_ID_LST, STAFF_ID


async def payments(call: CallbackQuery, callback_data: dict):
    '''Обработчик платежей.'''
    call.message.answer(text=f'{PAY_TOKEN}')
    order_id = callback_data['order_id']
    # выполняем запрос к БД на получение данного заказа
    response = await get_info_about_orders(order_id=order_id)

    if response == 400:
        await call.message.answer(text=f'{emojize(":robot:")} Не удалось выполнить запрос к серверу...')
        return

    result_orders_price = response['result_orders_price']
    response_order_id = response['pk']
    order_items = response['order_items']
    # amount принимает рубли в копейках, поэтому * 100
    # RUB	Russian Ruble	MIN: 60,22 RUB	MAX: 602 250,16 RUB
    price = types.LabeledPrice(label=f'Заказ № {response_order_id}', amount=int(result_orders_price * 100))
    # проверяем, что мы работаем с тестовой версией платежей
    if PAY_TOKEN.split(':')[1] == 'TEST':
        await call.message.answer(text='<b><ins>Это тестовый платёж.</ins></b>\n\n'
                                       f'<b>{emojize(":credit_card:")}Данные тестовые карты, которые можно использовать для проверки:</b>\n\n'
                                       f'<b>Номер карты</b>:  	<tg-spoiler>2200 0000 0000 0053</tg-spoiler>\n'
                                       f'<b>Срок действия</b>:  	<tg-spoiler>2024/12</tg-spoiler>\n'
                                       f'<b>Код:</b>  	<tg-spoiler>123</tg-spoiler>\n'
                                       f'<b>Код подтверждения платежа:</b>  	<tg-spoiler> 12345678</tg-spoiler>\n')
        # высылаем платёж
        await BOT.send_invoice(
            chat_id=callback_data['chat_id'],
            title=f'Заказ № {response_order_id}',
            description=f'Cостав заказа:\n{order_items}',
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
            start_parameter=f'payment-for-order-{response_order_id}',
            # этот параметр указывают, чтобы идентифицировать платеж,
            # пользователю не показывается, но мы можем прочитать при успешном платеже
            # он уникален для каждого товара(заказа)
            payload=f'invoice-payload-for-order-{response_order_id}',
        )


@DP.shipping_query_handler()
async def choose_shipping(query: types.ShippingQuery):
    '''Обработчик для выбора способа доставки.'''

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

    await BOT.answer_pre_checkout_query(pre_checkout_query_id=pre_checkout_query.id, ok=True)


@DP.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def process_successful_payment(message: types.Message):
    '''Обработчик для апдейта об успешной оплате.'''

    pmnt = message.successful_payment.to_python()
    order_id = pmnt['invoice_payload'].split('-')[-1]
    total_amount = pmnt['total_amount']
    telegram_payment_charge_id = pmnt['telegram_payment_charge_id']
    provider_payment_charge_id = pmnt['provider_payment_charge_id']
    customer_name = pmnt['order_info']['name']
    customer_telephone_number = pmnt['order_info']['phone_number']

    # уведомляем пользователя об успешной оплате
    await BOT.send_message(
        message.chat.id,
        '{emoj} Оплата прошла успешно. Итоговая цена: {total_amount} {currency}'.format(
            total_amount=message.successful_payment.total_amount // 100,
            currency=message.successful_payment.currency,
            emoj=emojize(":robot:")
        )
    )

    pay_order_data = {
        'order_id': order_id,
        'total_price': total_amount,
        'tlg_payment_charge_id': telegram_payment_charge_id,
        'provider_payment_charge_id': provider_payment_charge_id,
        'customer_name': customer_name,
        'customer_telephone_number': customer_telephone_number,
    }

    # отправляем запрос на создание новой записи в БД с инфой о платежах
    response = await post_req_for_add_pay_info_about_order(pay_order_data=pay_order_data)
    if response:
        for i_admin in ADMINS_ID_LST:
            await BOT.send_message(chat_id=i_admin, text=f'{emojize(":robot:")} Поступил новый платёж из {emojize(":bellhop_bell:")}Вашего кафе')

    # получаем сперва этот заказа
    this_fu_order = await get_info_about_orders(order_id=order_id)

    # запрос на обновление статуса заказа
    order_data = {
        'pk': order_id,
        'user_tlg_id': this_fu_order.get('user_tlg_id'),
        'pay_status': True,
        'execution_status': False,
        'order_items': this_fu_order.get('order_items'),
        'result_orders_price': this_fu_order.get('result_orders_price'),
    }
    response = await post_req_for_add_order(order_data=order_data)

    # формируем текст сообщения для персонала
    # читабельный текст статусов заказа
    if response.get('pay_status'):
        pay_status = '✅ Оплачен'
    else:
        pay_status = '❌НЕ оплачен'
    if response.get('execution_status'):
        execution_status = '✅ Готов'
    else:
        execution_status = '❌НЕ готов'

    # проверка условия доставки
    user_shipping_options = message.successful_payment.shipping_option_id
    if user_shipping_options == 'delivery-form-cafe':
        shipping_address = ' | '.join([
            pmnt['order_info']['shipping_address']['street_line1'],
            pmnt['order_info']['shipping_address']['street_line2']
        ])
    elif user_shipping_options == 'pickup-form-cafe':
        shipping_address = f'{emojize(":man_walking:")}Клиент заберёт заказ сам'
    else:
        shipping_address = 'Опция доставки не определена.'

    order_items = response.get('order_items').split('\n')
    result_orders_price = response.get('result_orders_price')

    text_for_message = f'<b><ins>Номер заказа: {order_id}' \
                       f'</ins></b>\n<b>Cостав заказа:</b> \n'
    other_text = f'<b>\nИтоговая цена заказа:</b>{result_orders_price}руб.\n' \
                 f'<b>Cтатус оплаты:</b> {pay_status}\n' \
                 f'<b>Статус выполнения:</b> {execution_status}\n' \
                 f'<b>Имя клиента</b>: {customer_name}\n' \
                 f'<b>Телефон клиента</b>: {customer_telephone_number}\n' \
                 f'<b>{emojize(":delivery_truck:")}Доставка</b>: {shipping_address}'
    for i_item in order_items:
        text_for_message = ''.join([text_for_message, i_item, '\n'])
    text_for_message = ''.join([text_for_message, other_text])

    # отправляем сообщение персоналу
    i_message = await BOT.send_message(chat_id=STAFF_ID, text=text_for_message)
    chat_id = i_message.chat.id
    message_id = i_message.message_id
    inline_keyboard = stuff_formation_order_complete_inline(chat_id=chat_id, message_id=message_id, order_id=order_id)
    await i_message.edit_text(text=''.join([text_for_message, emojize(':pizza:')]), reply_markup=inline_keyboard)


def register_payment_handlers():
    '''Регистрация обработчика оплаты'''

    DP.register_callback_query_handler(payments, callback_for_orders_lst.filter(flag='pay_order'))

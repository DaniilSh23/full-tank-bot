import aiohttp
from loguru import logger
from settings.config import ITEMS_CATEGORIES_API_URL, ITEMS_LST_API_URL, ITEMS_DETAIL_API_URL, \
    ADD_ITEMS_IN_BASKET_API_URL, BASKET_API_URL, REMOVE_ITEMS_FROM_BASKET_API_URL, CLEAR_BASKET_API_URL, ORDERS_API_URL, \
    REMOVE_ORDER_API_URL


@logger.catch
async def get_items_categories(pagination_part_of_link=None):
    '''Запрос для получения списка всех категорий работ'''

    if pagination_part_of_link:
        req_link = ''.join([ITEMS_CATEGORIES_API_URL, pagination_part_of_link])
    else:
        req_link = ITEMS_CATEGORIES_API_URL

    # создаём клиент сессии
    async with aiohttp.ClientSession() as session:
        # выполняем GET запрос по указанному в константе адресу
        async with session.get(req_link) as response:
            # ждём выполнения корутины ответа и формируем из ответа json
            return await response.json()


@logger.catch
async def get_items_list(items_category_id=None, pagination_part_of_link=None):
    '''Запрос для получение списка товаров, согласно выбранной категории'''

    if pagination_part_of_link:
        req_link = ''.join([ITEMS_LST_API_URL, pagination_part_of_link])
    elif items_category_id:
        req_link = ''.join([ITEMS_LST_API_URL, f'?items_category_id={items_category_id}'])

    async with aiohttp.ClientSession() as session:
        async with session.get(req_link) as response:
            response = await response.json()
            return response


@logger.catch
async def get_item_detail_info(item_id):
    '''Запрос для получения детальной информации о товаре.'''

    req_link = ''.join([ITEMS_DETAIL_API_URL, item_id])
    async with aiohttp.ClientSession() as session:
        async with session.get(req_link) as response:
            response = await response.json()
            return response


@logger.catch
async def add_item_in_basket(user_tlg_id, item_id):
    '''Запрос для внесения товара в список корзины пользователя или повышения числа товаров.'''

    req_link = ''.join([ADD_ITEMS_IN_BASKET_API_URL, f'?user_tlg_id={user_tlg_id}&item_id={item_id}'])
    async with aiohttp.ClientSession() as session:
        async with session.get(req_link) as response:
            # работаем с объектом ответа
            async with response:
                # если статус 204(No Content) - выходим
                if response.status == 204:
                    return response.status
                else:
                    return await response.json()


@logger.catch
async def remove_item_from_basket(user_tlg_id, item_id):
    '''Запрос для удаления товара из корзины, либо уменьшение его количества.'''

    req_link = ''.join([REMOVE_ITEMS_FROM_BASKET_API_URL, f'?user_tlg_id={user_tlg_id}&item_id={item_id}'])
    async with aiohttp.ClientSession() as session:
        async with session.get(req_link) as response:
            async with response:
                if response.status == 204:
                    return response.status
                else:
                    return await response.json()


async def get_user_basket(user_tlg_id, items_id=None):
    '''Запрос для получения товаров в корзине пользователя.'''

    req_link = ''.join([BASKET_API_URL, f'?user_tlg_id={user_tlg_id}'])
    if items_id:
        req_link = ''.join([req_link, f'&items_id={items_id}'])
    async with aiohttp.ClientSession() as session:
        async with session.get(req_link) as response:
            response = await response.json()
            return response


async def clear_basket(user_tlg_id):
    '''Запрос для очистки корзины пользователя'''

    req_link = ''.join([CLEAR_BASKET_API_URL, f'?user_tlg_id={user_tlg_id}'])
    async with aiohttp.ClientSession() as session:
        async with session.get(req_link) as response:
            async with response:
                return response.status


async def get_info_about_orders(user_tlg_id):
    '''Запрос для получения списка заказов.'''

    req_link = ''.join([ORDERS_API_URL, f'?user_tlg_id={user_tlg_id}'])
    async with aiohttp.ClientSession() as session:
        async with session.get(req_link) as response:
            async with response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 400:
                    return 400


async def req_for_remove_order(order_id):
    '''Запрос для удаления заказа.'''

    req_link = ''.join([REMOVE_ORDER_API_URL, f'?pk={order_id}'])
    async with aiohttp.ClientSession() as session:
        async with session.get(req_link) as response:
            async with response:
                if response.status == 200:
                    return 200
                else:
                    return 400


async def post_req_for_add_order(order_data):
    '''POST запрос для внесения данных о заказе и получение ответа в виде этого же заказа.'''

    req_link = ''.join([ORDERS_API_URL])
    async with aiohttp.ClientSession() as session:
        async with session.post(url=req_link, data=order_data) as response:
            async with response:
                if response.status == 201:
                    print(f'Ответ сервера: {await response.json()}')
                    return await response.json()
                else:
                    return 400


##################################
@logger.catch
async def get_works_list(category_id=None):
    '''Запрос для получения списка выполненных работ по данной категории.'''
    async with aiohttp.ClientSession() as session:
        if category_id:
            req_url = ''.join([COMPLETED_WORKS_LST_API_URL,'?id=', category_id])
        else:
            req_url = COMPLETED_WORKS_LST_API_URL
        async with session.get(req_url) as response:
            return await response.json()


@logger.catch
async def get_detail_info_about_work(work_id):
    '''Запрос для получения детальной информации о выполненной работе.'''
    async with aiohttp.ClientSession() as session:
        async with session.get(''.join([COMPLETED_WORK_DETAIL_API_URL, work_id])) as response:
            return await response.json()
            # data = await response.read()
            # return  json.loads(data)


@logger.catch
async def post_create_new_application(tlg_user_id, tlg_user_name, application_text):
    '''Запрос для создания новой заявки в БД'''
    async with aiohttp.ClientSession() as session:
        async with session.post(
                CREATE_NEW_APPLICATION_API_URL,
                headers={'Content-Type': 'application/json'},
                json={'tlg_user_id': tlg_user_id, 'tlg_user_name': tlg_user_name, 'application_text': application_text}
        ) as response:
            return await response.json()
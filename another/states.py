from aiogram.dispatcher.filters.state import StatesGroup, State


class ApplicationSendStates(StatesGroup):
    '''Класс для хранения состояний при отправки заявки'''
    prepare_to_send = State()

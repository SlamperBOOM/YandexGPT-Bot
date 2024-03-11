import logging
import threading

import jsonpickle
from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


settings_file_name = "settings.json"
paramsRouter = Router()
chat_params = {}
chat_params_lock = threading.Lock()


def read_params_from_disk():
    global chat_params
    chat_params_lock.acquire()
    try:
        with open(settings_file_name, "r") as file:
            logging.info("Reading settings file")
            chat_params = jsonpickle.decode(file.read(), classes=ModelParams)
    except Exception as err:
        logging.error("Couldn't open/read settings file")
        logging.error(err)
        chat_params = {}
    finally:
        chat_params_lock.release()


def save_settings_on_disk():
    chat_params_lock.acquire()
    with open(settings_file_name, "w") as file:
        file.write(jsonpickle.encode(chat_params))
    chat_params_lock.release()


class ModelParams:
    def __init__(self, temp=0.5, model_name="yandexgpt", context=""):
        self.temp = temp
        self.model_name = model_name
        self.context = context

    def __str__(self):
        return "Model: " + self.model_name + ", temp: " + str(self.temp) + ", context: " + self.context


class ParamsState(StatesGroup):
    setting_model = State()
    setting_temp = State()
    setting_context = State()


def get_params_for_chat(chat_id) -> ModelParams:
    chat_id = str(chat_id)
    chat_params_lock.acquire()
    settings = chat_params.get(chat_id)
    if settings is None:
        # need to add default params for chat if not any
        chat_params[chat_id] = ModelParams()
        settings = chat_params[chat_id]
    chat_params_lock.release()
    return settings


def update_params_for_chat(chat_id, settings: ModelParams):
    chat_params[chat_id] = settings


@paramsRouter.message(Command("settings"), StateFilter(None))
async def show_settings(message: types.Message):
    settings = get_params_for_chat(message.chat.id)
    buttons = [
        [types.InlineKeyboardButton(text="Выбрать модель", callback_data="set_model"),
         types.InlineKeyboardButton(text="Задать температуру", callback_data="set_temp")],
        [types.InlineKeyboardButton(text="Задать контекст", callback_data="set_context"),
         types.InlineKeyboardButton(text="Сбросить контекст", callback_data="drop_context")]
    ]
    kb = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    if settings.model_name == "yandexgpt":
        model_name = "YandexGPT"
    elif settings.model_name == "yandexgpt-lite":
        model_name = "YandexGPT Lite"
    else:
        model_name = "Краткий пересказ"
    logging.info("Request settings for chat " + str(message.chat.id))
    await message.answer("<b>Ваши текущие настройки:</b>\n\n"
                         "• Модель: <code>" + model_name + "</code>\n" +
                         "• Температура(степень безумности и креативности): <code>" + str(settings.temp) + "</code>\n" +
                         "• Контекст, в котором модель будет делать свои ответы: <code>" + settings.context + "</code>",
                         reply_markup=kb)


@paramsRouter.callback_query(F.data == "set_model")
async def show_model_options(callback: types.CallbackQuery, state: FSMContext):
    buttons = [
        [types.InlineKeyboardButton(text="YandexGPT", callback_data="model_yandexgpt"),
         types.InlineKeyboardButton(text="YandexGPT Lite", callback_data="model_yandexgpt-lite")],
        [types.InlineKeyboardButton(text="Краткий пересказ", callback_data="model_summarization"),
         types.InlineKeyboardButton(text="Назад", callback_data="back")]
    ]
    kb = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.edit_text("Выберите модель из предложенных вариантов:\n" +
                                     "• <b>YandexGPT</b> — большая модель, даёт более точные ответы "
                                     "на сложные запросы, но дольше генерирует ответ.\n" +
                                     "• <b>YandexGPT Lite</b> — стандартная модель, " +
                                     "которая подойдет для решения задач в режиме реального времени.\n" +
                                     "• <b>Краткий пересказ</b> — дообученная модель YandexGPT Lite " +
                                     "сократит текст до основных тезисов.")
    await callback.message.edit_reply_markup(callback.inline_message_id, kb)
    await state.set_state(ParamsState.setting_model)


@paramsRouter.callback_query(F.data.startswith("model_"), StateFilter(ParamsState.setting_model))
async def set_model_for_chat(callback: types.CallbackQuery, state: FSMContext):
    model_name = callback.data.split("_")[1]
    chat_id = callback.message.chat.id
    settings = get_params_for_chat(chat_id)
    settings.model_name = model_name
    logging.info("Set model for chat id " + str(chat_id) + ", new model: " + get_params_for_chat(chat_id).model_name)
    await callback.message.edit_reply_markup()
    await callback.message.edit_text("Модель успешно изменена. Можете вызвать /settings для проверки")
    await state.set_state(None)
    save_settings_on_disk()


@paramsRouter.callback_query(F.data == "back")
async def back_to_menu(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(None)
    await callback.message.delete()
    await show_settings(callback.message)


@paramsRouter.callback_query(F.data == "set_temp")
async def show_temp_setting_message(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer("Введите значение температуры для модели от 0 до 1")
    await state.set_state(ParamsState.setting_temp)


@paramsRouter.message(StateFilter(ParamsState.setting_temp))
async def set_temp_for_chat(message: types.Message, state: FSMContext):
    temp = message.text.replace(",", ".")
    try:
        val = float(temp)
    except:
        await message.answer("Неправильный формат числа. Введите еще раз")
        return
    if val < 0:
        val = 0
    elif val > 1:
        val = 1
    chat_id = message.chat.id
    settings = get_params_for_chat(chat_id)
    settings.temp = val
    logging.info("Set temp for chat id " + str(chat_id) + ", new temp: " + str(get_params_for_chat(chat_id).temp))
    await message.answer("Температура успешно задана. Можете вызвать /settings для проверки")
    await state.set_state(None)
    save_settings_on_disk()


@paramsRouter.callback_query(F.data == "set_context")
async def show_context_setting_message(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer("Введите контекст для модели")
    await state.set_state(ParamsState.setting_context)


@paramsRouter.message(StateFilter(ParamsState.setting_context))
async def set_context_for_chat(message: types.Message, state: FSMContext):
    context = message.text
    chat_id = message.chat.id
    settings = get_params_for_chat(chat_id)
    settings.context = context
    logging.info("Set context for chat id " + str(chat_id) + ", new context: " + get_params_for_chat(chat_id).context)
    await message.answer("Контекст успешно задан. Можете вызвать /settings для проверки")
    await state.set_state(None)
    save_settings_on_disk()


@paramsRouter.callback_query(F.data == "drop_context")
async def drop_context(callback: types.CallbackQuery):
    chat_id = callback.message.chat.id
    settings = get_params_for_chat(chat_id)
    settings.context = ""
    logging.info("Dropped context for chat id " + str(chat_id))
    await callback.message.delete()
    await callback.message.answer("Контекст сброшен. Можете вызвать /settings для проверки")
    save_settings_on_disk()

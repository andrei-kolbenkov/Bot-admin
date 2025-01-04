from aiogram import Bot, Dispatcher, types
from aiogram.types import ChatMemberUpdated, Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, InputMediaPhoto, FSInputFile, ChatPermissions, ContentType
from aiogram.filters import ChatMemberUpdatedFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import StateFilter, State, StatesGroup
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
from datetime import time, datetime, timedelta
import re
import os
import json
import logging

API_TOKEN = ""
ADMIN_CHAT_ID = [700000000]
CHAT_ID = -10000000000

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

# Список пользователей, которым разрешено отправлять ссылки
allowed_users = set()

START = "🟢 Модерация активна"
END = "🛑 Модерация отключена"
ACTIVE = True


# Хранилище для ID последнего сообщения бота в чате
LAST_MESSAGE_OBS = {}
LAST_MESSAGE_LINK = {}
LAST_MESSAGE_REP = {}


OBS_MES_FILE = "obs_mes.txt"
def load_message_obs():
    """Загрузка сообщения из файла."""
    if not os.path.exists(OBS_MES_FILE):
        with open(OBS_MES_FILE, "w", encoding="utf-8") as file:
            file.write("Сообщение по умолчанию")
    with open(OBS_MES_FILE, "r", encoding="utf-8") as file:
        return file.read().strip()

def save_message_obs(new_message):
    """Сохранение сообщения в файл."""
    with open(OBS_MES_FILE, "w", encoding="utf-8") as file:
        file.write(new_message)



REP_MES_FILE = "rep_mes.txt"
def load_message_rep():
    """Загрузка сообщения из файла."""
    if not os.path.exists(REP_MES_FILE):
        with open(REP_MES_FILE, "w", encoding="utf-8") as file:
            file.write("Сообщение по умолчанию")
    with open(REP_MES_FILE, "r", encoding="utf-8") as file:
        return file.read().strip()

def save_message_rep(new_message):
    """Сохранение сообщения в файл."""
    with open(REP_MES_FILE, "w", encoding="utf-8") as file:
        file.write(new_message)


LINK_MES_FILE = "link_mes.txt"
def load_message_link():
    """Загрузка сообщения из файла."""
    if not os.path.exists(LINK_MES_FILE):
        with open(LINK_MES_FILE, "w", encoding="utf-8") as file:
            file.write("Сообщение по умолчанию")
    with open(LINK_MES_FILE, "r", encoding="utf-8") as file:
        return file.read().strip()

def save_message_link(new_message):
    """Сохранение сообщения в файл."""
    with open(LINK_MES_FILE, "w", encoding="utf-8") as file:
        file.write(new_message)



NMB_MES_FILE = "nmb_mes.txt"
def load_message_nmb():
    """Загрузка сообщения из файла."""
    if not os.path.exists(NMB_MES_FILE):
        with open(NMB_MES_FILE, "w", encoding="utf-8") as file:
            file.write("Сообщение по умолчанию")
    with open(NMB_MES_FILE, "r", encoding="utf-8") as file:
        return file.read().strip()

def save_message_nmb(new_message):
    """Сохранение сообщения в файл."""
    with open(NMB_MES_FILE, "w", encoding="utf-8") as file:
        file.write(new_message)



NIGHT_MES_FILE = "night_mes.txt"
def load_message_night():
    """Загрузка сообщения из файла."""
    if not os.path.exists(NIGHT_MES_FILE):
        with open(NIGHT_MES_FILE, "w", encoding="utf-8") as file:
            file.write("Сообщение по умолчанию")
    with open(NIGHT_MES_FILE, "r", encoding="utf-8") as file:
        return file.read().strip()

def save_message_night(new_message):
    """Сохранение сообщения в файл."""
    with open(NIGHT_MES_FILE, "w", encoding="utf-8") as file:
        file.write(new_message)


# Лимит на добавление участников
ADD_LIMIT = 30  # Максимум участников в час
add_log = {}  # Хранение добавлений: {chat_id: [(user_id, timestamp), ...]}

user_messages = {}

scheduler = AsyncIOScheduler()

# Регулярное выражение для поиска ссылок
LINK_PATTERN = re.compile(
    r"(?i)"  # Игнор регистра
    r"(?:https?|ftp):\/\/[^\s/$.?#].[^\s]*"  # Ссылки с протоколами
    r"|www\.[^\s/$.?#].[^\s]*"               # Ссылки с www
    r"|(?:\S+\.(ru|com|net|org|info|biz|edu|gov|io|me|ua|by|kz|uz|tk))\b"  # Явные доменные зоны
    r"|@\w+"                                # Упоминания
    r"|t\.me\/\S+"                          # Telegram ссылки
    r"|\b\d{1,3}(\.\d{1,3}){3}\b"           # IP-адреса
)

PHONE_PATTERN = re.compile(r'(?:\+7|8)9\d{9}')

BAD_WORDS_FILE = "obscenity.txt"
# Чтение списка запрещённых слов
def load_bad_words():
    if not os.path.exists(BAD_WORDS_FILE):
        with open(BAD_WORDS_FILE, "w", encoding="utf-8") as file:
            file.write("")  # Создаём пустой файл, если его нет
    with open(BAD_WORDS_FILE, "r", encoding="utf-8") as file:
        content = file.read()
        return {word.strip().lower() for word in content.split(",") if word.strip()}

# Сохранение новых запрещённых слов
def save_bad_words(words):
    with open(BAD_WORDS_FILE, "w", encoding="utf-8") as file:
        file.write("\n".join(sorted(words)))

# Загружаем список запрещённых слов при старте
bad_words = load_bad_words()


DATA_FILE = "users.json"
# Загружаем данные при запуске
def load_user_message_count():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Сохраняем данные в файл
def save_user_message_count(data):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


ADMIN_LIST_FILE = "alist.txt"
def load_alist():
    if not os.path.exists(ADMIN_LIST_FILE):
        with open(ADMIN_LIST_FILE, "w", encoding="utf-8") as file:
            file.write("")  # Создаём пустой файл, если его нет
    with open(ADMIN_LIST_FILE, "r", encoding="utf-8") as file:
        # Читаем строки, удаляем лишние пробелы и игнорируем пустые строки
        return [line.strip().lower() for line in file if line.strip()]

# Сохранение новых запрещённых слов
def save_alist(users_text):
    # Разделяем входной текст на строки, убираем пустые строки и лишние пробелы
    users = [line.strip() for line in users_text.splitlines() if line.strip()]
    # Сохраняем уникальные имена в алфавитном порядке
    with open(ADMIN_LIST_FILE, "w", encoding="utf-8") as file:
        file.write("\n".join(sorted(set(users))))



COUNT_NUMBER_FROM_USER = 10







class Form(StatesGroup):
    allow = State()
    revoke = State()
    number = State()
    obs = State()
    limit = State()
    mes_obs = State()
    mes_link = State()
    mes_nmb = State()
    mes_rep = State()
    mes_night = State()
    alist = State()



@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    if message.chat.type == "private":
        welcome_text = "👋 Привет!"
        await message.answer(welcome_text)


# /admin
@dp.message(Command('admin'))
async def admin_panel(message: types.Message):
    if message.chat.type == "private":
        if message.chat.id in ADMIN_CHAT_ID:
            await message.answer("Панель администратора:", reply_markup=admin_kb())
        else:
            await message.answer("У вас нет доступа к этой команде.")



@dp.callback_query(lambda c: c.data and c.data.startswith('admin_'))
async def admin_callback_handler(callback_query: CallbackQuery, state: FSMContext):
    data = callback_query.data
    if data == 'admin_allow':
        await state.set_state(Form.allow)
        await bot.send_message(callback_query.from_user.id, "Введите @username пользователя или ID:")
    elif data == 'admin_revoke':
        await state.set_state(Form.revoke)
        await bot.send_message(callback_query.from_user.id, "Введите @username пользователя или ID:")
    elif data == 'admin_number':
        await state.set_state(Form.number)
        await bot.send_message(callback_query.from_user.id, "Введите количество постов от одного человека с номером телефона:")
    elif data == 'admin_obs':
        await state.set_state(Form.obs)
        """Отправка файла с запрещёнными словами."""
        await bot.send_document(callback_query.from_user.id, types.FSInputFile(BAD_WORDS_FILE), caption="Отправьте новый файл в формате .txt")
    elif data == 'admin_limit':
        await state.set_state(Form.limit)
        await bot.send_message(callback_query.from_user.id, "Введите количество количество добавляемых пользователей в час:")
    elif data == 'admin_message':
        await bot.send_message(callback_query.from_user.id, text='Выберите сообщение для изменения:', reply_markup=message_kb())
    elif data == 'admin_list':
        await state.set_state(Form.alist)
        text = f''
        for name in load_alist():
            text += f'{name}\n'
        text += f'\nВведите @username или ID постоянных пользователей каждого с новой строки:'
        await bot.send_message(callback_query.from_user.id, text=text)
    else:
        await bot.answer_callback_query(callback_query.id, "Неизвестная команда")


# Обработчик кнопки "Назад"
@dp.callback_query(lambda c: c.data and c.data == 'back')
async def back_callback_handler(callback_query: CallbackQuery):
    await bot.send_message(callback_query.message.chat.id, "Панель администратора:",  reply_markup=admin_kb())
    await bot.answer_callback_query(callback_query.id)




@dp.callback_query(lambda c: c.data == 'change_obs_mes')
async def update_mes_obs(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(Form.mes_obs)  # Set the state
    text = f'{load_message_obs()}\n\nВведите новое сообщение:'
    await bot.send_message(callback_query.from_user.id, text)

@dp.message(StateFilter(Form.mes_obs))
async def update_mes_obs2(message: types.Message, state: FSMContext):
    try:
        # Сохраняем новое сообщение в файл
        new_message = message.text
        save_message_obs(new_message)
        await message.answer(f'Сообщение изменено', reply_markup=message_kb())
    finally:
        await state.clear()  # Finish the state



@dp.callback_query(lambda c: c.data == 'change_rep_mes')
async def update_mes_obs(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(Form.mes_rep)  # Set the state
    text = f'{load_message_rep()}\n\nВведите новое сообщение:'
    await bot.send_message(callback_query.from_user.id, text)

@dp.message(StateFilter(Form.mes_rep))
async def update_mes_obs2(message: types.Message, state: FSMContext):
    try:
        save_message_rep(message.text)
        await message.answer(f'Сообщение изменено', reply_markup=message_kb())
    finally:
        await state.clear()  # Finish the state




@dp.callback_query(lambda c: c.data == 'change_link_mes')
async def update_mes_obs(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(Form.mes_link)  # Set the state
    text = f'{load_message_link()}\n\nВведите новое сообщение:'
    await bot.send_message(callback_query.from_user.id, text)

@dp.message(StateFilter(Form.mes_link))
async def update_mes_obs2(message: types.Message, state: FSMContext):
    try:
        save_message_link(message.text)
        await message.answer(f'Сообщение изменено', reply_markup=message_kb())
    finally:
        await state.clear()  # Finish the state




@dp.callback_query(lambda c: c.data == 'change_nmb_mes')
async def update_mes_obs(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(Form.mes_nmb)  # Set the state
    text = f'{load_message_nmb()}\n\nВведите новое сообщение:'
    await bot.send_message(callback_query.from_user.id, text)

@dp.message(StateFilter(Form.mes_nmb))
async def update_mes_obs2(message: types.Message, state: FSMContext):
    try:
        save_message_nmb(message.text)
        await message.answer(f'Сообщение изменено', reply_markup=message_kb())
    finally:
        await state.clear()  # Finish the state



@dp.callback_query(lambda c: c.data == 'change_night_mes')
async def update_mes_obs(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(Form.mes_night)  # Set the state
    text = f'{load_message_night()}\n\nВведите новое сообщение. Обратите внимание на механизм ссылок:'
    await bot.send_message(callback_query.from_user.id, text, disable_web_page_preview=True)

@dp.message(StateFilter(Form.mes_night))
async def update_mes_obs2(message: types.Message, state: FSMContext):
    try:
        save_message_night(message.text)
        await message.answer(f'Сообщение изменено', reply_markup=message_kb())
    finally:
        await state.clear()  # Finish the state




@dp.callback_query(lambda c: c.data == 'astart')
async def update_mes_obs(callback_query: types.CallbackQuery):
    global ACTIVE
    if ACTIVE is True:
        ACTIVE = False
    else:
        ACTIVE = True
    if callback_query.from_user.id in ADMIN_CHAT_ID:
        await callback_query.message.answer("Панель администратора:", reply_markup=admin_kb())




@dp.message(StateFilter(Form.alist))
async def update_mes_obs2(message: types.Message, state: FSMContext):
    try:
        # Сохраняем новое сообщение в файл
        new_message = message.text
        save_alist(new_message)
        await message.answer(f'Список постоянных пользователей обновлен', reply_markup=admin_kb())
    finally:
        await state.clear()  # Finish the state



@dp.message(StateFilter(Form.allow))
async def process_post_product(message: types.Message, state: FSMContext):
    try:
        input_data = message.text.strip()
        if input_data.isdigit():  # Если введено число, предполагаем, что это ID
            user_id = int(input_data)
            allowed_users.add(user_id)
            user_message_count = load_user_message_count()
            user_message_count[user_id] = user_message_count.get(user_id, 0) - 1
            # Сохраняем обновленные данные в файл
            save_user_message_count(user_message_count)
            await message.reply(f"Пользователю с ID {user_id} разрешено отправлять ссылки или номер.", reply_markup=admin_kb())
        elif input_data.startswith("@") and len(input_data) > 2:  # Если введён никнейм
            username = input_data[1:]
            allowed_users.add(username)
            user_message_count = load_user_message_count()
            user_message_count[username] = user_message_count.get(username, 0) - 1
            # Сохраняем обновленные данные в файл
            save_user_message_count(user_message_count)
            await message.reply(f"Пользователю {input_data} разрешено отправлять ссылки или номер.", reply_markup=admin_kb())
        else:
            # Если формат не соответствует ни ID, ни никнейму
            await message.reply(
                "Ошибка! Введите корректный ID (только цифры) или Username (начинающийся с '@' и длиннее 2 символов).",
                reply_markup=admin_kb(),
            )
    finally:
        await state.clear()
    print(allowed_users)



@dp.message(StateFilter(Form.revoke))
async def process_post_product(message: types.Message, state: FSMContext):
    try:
        input_data = message.text.strip()
        if input_data.isdigit():  # Если введено число, предполагаем, что это ID
            user_id = int(input_data)
            if user_id in allowed_users:
                allowed_users.discard(user_id)
                await message.reply(f"Пользователю с ID {user_id} запрещено отправлять ссылки или номер.", reply_markup=admin_kb())
            else:
                await message.reply(f"Пользователь с ID {user_id} не найден в списке разрешённых.", reply_markup=admin_kb())
        elif input_data.startswith("@") and len(input_data) > 2:  # Если введён никнейм
            username = input_data[1:]
            if username in allowed_users:
                allowed_users.discard(username)
                await message.reply(f"Пользователю {input_data} запрещено отправлять ссылки или номер.", reply_markup=admin_kb())
            else:
                await message.reply(f"Пользователь {input_data} не найден в списке разрешённых.", reply_markup=admin_kb())
        else:
            # Если формат не соответствует ни ID, ни никнейму
            await message.reply(
                "Ошибка! Введите корректный ID (только цифры) или Username (начинающийся с '@' и длиннее 2 символов).",
                reply_markup=admin_kb(),
            )
    finally:
        await state.clear()
    print(allowed_users)


@dp.message(StateFilter(Form.number))
async def process_post_product(message: types.Message, state: FSMContext):
    global COUNT_NUMBER_FROM_USER
    try:
        old_count = COUNT_NUMBER_FROM_USER
        COUNT_NUMBER_FROM_USER = int(message.text)
        user_message_count = load_user_message_count()
        for user, count in user_message_count.items():
            if count >= old_count:
                if count >= COUNT_NUMBER_FROM_USER:
                    user_message_count[user] = COUNT_NUMBER_FROM_USER
        # Сохраняем обновленные данные в файл
        save_user_message_count(user_message_count)
        await message.answer(f'Установлено новое количество постов с номером - {int(message.text)}', reply_markup=admin_kb())
    except ValueError:
        await message.answer('Пожалуйста, введите только число.', reply_markup=admin_kb())
    finally:
        await state.clear()


# Обработка загруженного файла
@dp.message(StateFilter(Form.obs))
async def process_new_bad_words_file(message: Message, state: FSMContext):
    if message.document:
        """Обработка нового файла с запрещёнными словами."""
        file = message.document
        file_path = f"{file.file_name}"

        # Скачивание файла
        await bot.download(file, file_path)

        # Чтение и обновление списка запрещённых слов
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                new_bad_words = {line.strip().lower() for line in f if line.strip()}
            bad_words.update(new_bad_words)
            save_bad_words(bad_words)
            await message.answer("Список запрещённых слов обновлён.", reply_markup=admin_kb())
        except Exception as e:
            await message.answer(f"Произошла ошибка при обработке файла: {e}")
        finally:
            if file_path != BAD_WORDS_FILE:
                os.remove(file_path)  # Удаляем файл после обработки
            await state.clear()
    else:
        await message.answer("Пожалуйста, отправьте файл с запрещёнными словами.")





def has_entities(message: Message) -> bool:
    """Проверяет наличие ссылок в entities."""
    if message.entities:
        for entity in message.entities:
            if entity.type in ("url", "text_link"):  # URL или встроенные ссылки
                return True
    return False

@dp.message(lambda message: (message.text or message.caption) and (LINK_PATTERN.search(message.text or message.caption) or has_entities(message) if message.text or message.caption else False))
async def handle_links(message: Message):
    if ACTIVE is True:
        if (message.from_user.id not in ADMIN_CHAT_ID) and (str(message.from_user.id) not in load_alist()) and (message.from_user.username not in load_alist()):
            print(load_alist())
            if message.chat.type != "private":
                """Обработка сообщений с ссылками."""
                global LAST_MESSAGE_LINK
                print('print(LAST_MESSAGE_LINK)')
                print(LAST_MESSAGE_LINK)
                print(message.text or message.caption)
                username = message.from_user.username
                user_id = message.from_user.id
                chat_id = message.chat.id
                if (username not in allowed_users) and (user_id not in allowed_users):
                    await message.delete()
                    new_message = await message.answer(load_message_link())

                    # if chat_id in LAST_MESSAGE_LINK:
                    #     try:
                    #         await bot.delete_message(chat_id=chat_id, message_id=LAST_MESSAGE_LINK[chat_id])
                    #     except Exception as e:
                    #         print(e)
                    # LAST_MESSAGE_LINK[chat_id] = new_message.message_id
                    # print(LAST_MESSAGE_LINK)

                    # Удаляем сообщение через 30 секунд
                    asyncio.create_task(delete_message_later(chat_id, new_message.message_id))
                else:
                    # Удаляем пользователя из списка после отправки разрешённой ссылки
                    if username in allowed_users:
                        allowed_users.discard(username)
                        # Увеличиваем счетчик сообщений с номерами для пользователя
                        user_message_count = load_user_message_count()
                        user_message_count[username] = user_message_count.get(username, 0) + 1
                    else:
                        allowed_users.discard(user_id)
                        # Увеличиваем счетчик сообщений с номерами для пользователя
                        user_message_count = load_user_message_count()
                        user_message_count[user_id] = user_message_count.get(user_id, 0) + 1
                    # Сохраняем обновленные данные в файл
                    save_user_message_count(user_message_count)




@dp.message(lambda message: PHONE_PATTERN.search(message.text or message.caption) if message.text or message.caption else False)
async def check_phone_numbers(message: Message):
    if ACTIVE is True:
        if (message.from_user.id not in ADMIN_CHAT_ID) and (str(message.from_user.id) not in load_alist()) and (message.from_user.username not in load_alist()):
            if message.chat.type != "private":
                user_id = message.from_user.id
                username = message.from_user.username
                chat_id = message.chat.id
                # Увеличиваем счетчик сообщений с номерами для пользователя
                user_message_count = load_user_message_count()
                if username and user_message_count[username]:
                    user_message_count[username] = user_message_count.get(username, 0) + 1
                    # Удаляем также возможность отправки ссылки
                    allowed_users.discard(username)

                    # Проверяем, превышен ли лимит
                    if user_message_count[username] > COUNT_NUMBER_FROM_USER:
                        # Удаляем сообщение, превышающее лимит
                        new_message = await message.answer(load_message_nmb())
                        await message.delete()
                        asyncio.create_task(delete_message_later(chat_id, new_message.message_id))
                    else:
                        # Сохраняем обновленные данные в файл
                        save_user_message_count(user_message_count)
                else:
                    user_message_count[user_id] = user_message_count.get(user_id, 0) + 1
                    # Удаляем также возможность отправки ссылки
                    allowed_users.discard(user_id)

                    # Проверяем, превышен ли лимит
                    if user_message_count[user_id] > COUNT_NUMBER_FROM_USER:
                        # Удаляем сообщение, превышающее лимит
                        new_message = await message.answer(load_message_nmb())
                        await message.delete()
                        asyncio.create_task(delete_message_later(chat_id, new_message.message_id))
                    else:
                        # Сохраняем обновленные данные в файл
                        save_user_message_count(user_message_count)



                    # await message.answer(f"Сообщение с номером телефона принято. Помните, что лимит — {COUNT_NUMBER_FROM_USER} сообщения.")



def contains_bad_words(text, bad_words):
    pattern = r'\b(?:' + '|'.join(re.escape(word) for word in bad_words) + r')\b'
    return re.search(pattern, text.lower()) is not None

# Обработка сообщений с матами
@dp.message(lambda message: contains_bad_words(message.text or message.caption, bad_words) if message.text or message.caption else False)
async def delete_bad_words(message: Message):
    if ACTIVE is True:
        if message.chat.type != "private":
            """Удаление сообщений с матами."""
            global LAST_MESSAGE_OBS
            print('print(LAST_MESSAGE_OBS)')
            # print(LAST_MESSAGE_OBS)
            print(message.text or message.caption)
            username = message.from_user.username
            chat_id = message.chat.id
            text = f'{load_message_obs()}'
            text = text.replace('username', username)
            await message.delete()
            new_message = await message.answer(text)

            # if chat_id in LAST_MESSAGE_OBS:
            #     await bot.delete_message(chat_id=chat_id, message_id=LAST_MESSAGE_OBS[chat_id])
            # LAST_MESSAGE_OBS[chat_id] = new_message.message_id
            # print(LAST_MESSAGE_OBS)

            # Удаляем сообщение через 30 секунд
            asyncio.create_task(delete_message_later(chat_id, new_message.message_id))


@dp.message(lambda message: message.new_chat_members is not None)
async def handle_new_members(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if not check_additions(chat_id, user_id):
        # Удаляем пользователя из группы
        await bot.ban_chat_member(chat_id=chat_id, user_id=user_id)
        # await bot.send_message(
        #     chat_id,
        #     f"Лимит на добавление участников ({ADD_LIMIT} в час) достигнут. Пользователь {message.from_user.username} не может вступить."
        # )
        # Разбанить пользователя, чтобы он мог снова попытаться вступить позже
        await bot.unban_chat_member(chat_id=chat_id, user_id=user_id)
    # else:
    #     await bot.send_message(chat_id, f"Новый участник {message.from_user.username} добавлен.")
    await message.delete()

@dp.message(lambda message: message.left_chat_member is not None)
async def handle_left_members(message: Message):
    # print("""Удаляем сообщение об уходе участника.""")
    await message.delete()

@dp.message(lambda message: message.pinned_message is not None)
async def handle_pinned_message(message: Message):
    # print("""Удаляем сообщение о закреплении сообщения.""")
    await message.delete()



@dp.message()
async def handle_messages(message: Message):
    if ACTIVE is True:
        if (message.from_user.id not in ADMIN_CHAT_ID) and (str(message.from_user.id) not in load_alist()) and (message.from_user.username not in load_alist()):
            if message.chat.type != "private":
                if (message.from_user.username not in allowed_users) and (message.from_user.id not in allowed_users):
                    # Проверяем, содержит ли сообщение текст или подпись к фотографии
                    if message.content_type in {ContentType.TEXT, ContentType.PHOTO}:
                        user_id = message.from_user.id
                        chat_id = message.chat.id
                        # Определяем текст сообщения или подпись к фото
                        text = message.text or message.caption

                        if text:  # Обрабатываем только, если текст существует
                            global LAST_MESSAGE_REP
                            print('print(LAST_MESSAGE_REP)')
                            print(LAST_MESSAGE_REP)
                            print(text)
                            # Проверяем, если текст совпадает с последним сообщением пользователя
                            if user_id in user_messages and user_messages[user_id] == text:
                                await message.delete()  # Удаляем повторяющееся сообщение
                                new_message = await bot.send_message(chat_id, load_message_rep())

                                # if chat_id in LAST_MESSAGE_REP:
                                #     await bot.delete_message(chat_id=chat_id, message_id=LAST_MESSAGE_REP[chat_id])
                                # LAST_MESSAGE_REP[chat_id] = new_message.message_id
                                # print(LAST_MESSAGE_REP)

                                # Удаляем сообщение через 30 секунд
                                asyncio.create_task(delete_message_later(chat_id, new_message.message_id))
                            else:
                                # Сохраняем текст последнего сообщения пользователя
                                user_messages[user_id] = text
                else:
                    username = message.from_user.username
                    user_id = message.from_user.id
                    if username in allowed_users:
                        allowed_users.discard(username)
                    else:
                        allowed_users.discard(user_id)




async def delete_message_later(chat_id: int, message_id: int):
    await asyncio.sleep(10)  # Задержка 30 секунд
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        # Игнорируем ошибки (например, если сообщение уже удалено)
        print(f"Не удалось удалить сообщение {message_id}: {e}")


# Функция для проверки и обновления добавлений
def check_additions(chat_id, user_id):
    now = datetime.now()
    if chat_id not in add_log:
        add_log[chat_id] = []

    # Удаляем записи старше 1 часа
    add_log[chat_id] = [
        (uid, timestamp) for uid, timestamp in add_log[chat_id] if timestamp > now - timedelta(hours=1)
        ]

    # Проверяем лимит
    if len(add_log[chat_id]) >= ADD_LIMIT:
        return False  # Превышен лимит

    # Добавляем нового участника
    add_log[chat_id].append((user_id, now))
    return True



# Команда для изменения лимита
@dp.message(StateFilter(Form.limit))
async def set_limit(message: types.Message, state: FSMContext):
    try:
        global ADD_LIMIT
        ADD_LIMIT = int(message.text)
        await message.reply(f"Лимит успешно установлен: {ADD_LIMIT} участников в час.", reply_markup=admin_kb())
    except:
        await message.reply("Неправильный ввод", reply_markup=admin_kb())
    finally:
        await state.clear()




def admin_kb():
    if ACTIVE is True:
        onstart = START
    else:
        onstart = END

    btn_allow = InlineKeyboardButton(text='✅ Разрешить отправку ссылки или номера', callback_data='admin_allow')
    btn_revoke = InlineKeyboardButton(text='⛔️ Запретить отправку ссылки', callback_data='admin_revoke')
    btn_list = InlineKeyboardButton(text='📝 Список постоянных пользователей', callback_data='admin_list')
    btn_number = InlineKeyboardButton(text=f'📞 Количество постов с номером тел. - {COUNT_NUMBER_FROM_USER}', callback_data='admin_number')
    btn_obs = InlineKeyboardButton(text='🔞 Файл нецензурных слов', callback_data='admin_obs')
    btn_limit = InlineKeyboardButton(text='🙋‍♂️ Лимит добавления участников в час', callback_data='admin_limit')
    btn_message = InlineKeyboardButton(text='✉️ Редактировать сообщения', callback_data='admin_message')
    btn_start = InlineKeyboardButton(text=onstart, callback_data='astart')
    admin_kb = InlineKeyboardMarkup(inline_keyboard=[[btn_allow], [btn_revoke], [btn_list], [btn_number], [btn_obs], [btn_limit], [btn_message], [btn_start]])
    return admin_kb

def message_kb():
    btn_obs = InlineKeyboardButton(text='Изменить сообщение за мат', callback_data='change_obs_mes')
    btn_rep = InlineKeyboardButton(text='Изменить сообщение за повторное размещение', callback_data='change_rep_mes')
    btn_link = InlineKeyboardButton(text='Изменить сообщение за ссылку', callback_data='change_link_mes')
    btn_nmb = InlineKeyboardButton(text='Изменить сообщение за превышение лимита с номером телефона', callback_data='change_nmb_mes')
    btn_night = InlineKeyboardButton(text='Изменить сообщение закрытия чата', callback_data='change_night_mes')
    btn_back = InlineKeyboardButton(text='⬅️ Назад', callback_data='back')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[btn_obs], [btn_rep], [btn_link], [btn_nmb], [btn_night], [btn_back]])
    return keyboard






async def open_chat():
    """Открывает чат для всех участников."""
    permissions = ChatPermissions(can_send_messages=True, can_send_photos=True, can_invite_users=True)
    await bot.set_chat_permissions(chat_id=CHAT_ID, permissions=permissions)
    await bot.send_message(CHAT_ID, "Чат открыт! 🟢")


async def close_chat():
    """Закрывает чат для всех участников и публикует сообщение."""
    # Отправляем сообщение перед закрытием
    await bot.send_message(CHAT_ID, load_message_night(), disable_web_page_preview=True, parse_mode="Markdown")

    # Устанавливаем права, запрещающие отправку сообщений
    permissions = ChatPermissions(can_send_messages=False)
    await bot.set_chat_permissions(chat_id=CHAT_ID, permissions=permissions)


def setup_schedule():
    """Настройка расписания."""
    scheduler.add_job(open_chat, 'cron', hour=15, minute=57)  # Открыть в 7:00
    scheduler.add_job(close_chat, 'cron', hour=15, minute=56)  # Закрыть в 22:00
    scheduler.start()



async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    setup_schedule()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

# -*- coding: utf-8 -*-
import threading
import cid
lock = threading.Lock()
import configure
import telebot
import sqlite3
from io import BytesIO
import requests
user_languages = {}



# Инициализация бота и базы данных
client = telebot.TeleBot(configure.config['TOKEN'])
db = sqlite3.connect('baza.db', check_same_thread=False)
sql = db.cursor()

sql.execute("""CREATE TABLE IF NOT EXISTS users (
    id BIGINT PRIMARY KEY, 
    nick TEXT, 
    cash INT DEFAULT 0, 
    access INT DEFAULT 0, 
    bought INT DEFAULT 0)""")

sql.execute("""CREATE TABLE IF NOT EXISTS shop (
    id INT PRIMARY KEY, 
    name TEXT, 
    price INT, 
    tovar TEXT, 
    whobuy TEXT)""")
db.commit()

# Функция регистрации нового пользователя
def add_user(uid, nick):
    # Проверка, существует ли пользователь
    sql.execute(f"SELECT id FROM users WHERE id = {uid}")
    if sql.fetchone() is None:
        # Добавляем нового пользователя в базу данных
        sql.execute(f"INSERT INTO users (id, nick, cash, access, bought) VALUES ({uid}, '{nick}', 0, 0, 0)")
        db.commit()
        return True
    return False


@client.message_handler(commands=['start'])
def start(message):
    try:
        getname = message.from_user.first_name
        cid = message.chat.id
        uid = message.from_user.id

        # Регистрируем нового пользователя
        if add_user(uid, getname):
            client.send_message(cid, f"🛒 | Добро пожаловать, {getname}!\nТы попал в бота магазин\nKavik!")
        else:
            client.send_message(cid, f"⛔️ | Ты уже зарегистрирован! Используй кнопки ниже для навигации.")

        # Отправляем GIF-анимированное изображение
        gif_url = "https://cdn.lifehacker.ru/wp-content/uploads/2018/10/Vpn-oblozhka-bez-zagolovka_1539676274.gif"
        client.send_animation(cid, gif_url, caption="🎉 Удачного дня!")

        # Создаем клавиатуру с кнопками для выбора языка
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn_ru = types.KeyboardButton("Русский")
        btn_en = types.KeyboardButton("English")
        markup.add(btn_ru, btn_en)

        # Отправляем сообщение с кнопками выбора языка
        client.send_message(cid, "Выберите язык / Choose a language:", reply_markup=markup)

    except Exception as e:
        client.send_message(cid, f'🚫 | Ошибка при выполнении команды: {str(e)}')


# Обработчик для выбора языка
@client.message_handler(func=lambda message: message.text in ['Русский', 'English'])
def language_choice(message):
    cid = message.chat.id
    uid = message.from_user.id

    if message.text == "Русский":
        user_languages[uid] = "ru"  # Сохраняем язык для пользователя
        client.send_message(cid, "Вы выбрали русский язык! Можете продолжать использовать бота.")
    elif message.text == "English":
        user_languages[uid] = "en"  # Сохраняем язык для пользователя
        client.send_message(cid, "You have selected English! You can now continue using the bot.")

    # После выбора языка показываем основное меню
    show_main_menu(cid, uid)


# Функция для отображения основного меню
def show_main_menu(cid, uid):
    # Определим язык
    language = user_languages.get(uid, "ru")  # По умолчанию русский

    # Создаем клавиатуру с кнопками в зависимости от языка
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    if language == "ru":
        btn_profile = types.KeyboardButton("Профиль")
        btn_teh = types.KeyboardButton("Техподдержка")
        btn_help = types.KeyboardButton("Помощь")
        markup.add(btn_profile, btn_teh, btn_help)
        client.send_message(cid, "Выберите действие:", reply_markup=markup)
    elif language == "en":
        btn_profile = types.KeyboardButton("Profile")
        btn_teh = types.KeyboardButton("Support")
        btn_help = types.KeyboardButton("Help")
        markup.add(btn_profile, btn_teh, btn_help)
        client.send_message(cid, "Choose an action:", reply_markup=markup)


# Обработчик кнопки "Техподдержка"
@client.message_handler(func=lambda message: message.text == "Техподдержка" or message.text == "Support")
def support_command(message):
    try:
        cid = message.chat.id
        user_id = message.from_user.id
        language = user_languages.get(user_id, 'ru')  # Получаем текущий язык пользователя

        # Информация о тех.поддержке
        if language == 'ru':
            support_text = (
                "💬 | Техническая поддержка:\n\n"
                "Если у вас возникли проблемы или вопросы, напишите нам, и мы постараемся вам помочь.\n"
                "Вы можете отправить запрос или описать проблему, и наш специалист ответит в ближайшее время.\n\n"
                "Для связи с нами используйте одну из следующих опций:\n"
                "1. Напишите здесь, и мы ответим вам как можно скорее.\n"
                "2. Напишите на почту: support@kavikbot.ru\n"
                "3. Также можете обратиться в личное сообщение в Telegram: @Kavik011"
            )
        elif language == 'en':
            support_text = (
                "💬 | Technical Support:\n\n"
                "If you have any problems or questions, please write to us, and we will assist you as soon as possible.\n"
                "You can send a request or describe the issue, and our specialist will respond shortly.\n\n"
                "For contact, use one of the following options:\n"
                "1. Write here, and we will reply as soon as possible.\n"
                "2. Write to our email: support@kavikbot.com\n"
                "3. You can also send a private message on Telegram: @Kavik011"
            )

        # Отправляем сообщение с информацией о поддержке
        client.send_message(cid, support_text)

    except Exception as e:
        client.send_message(cid, f'🚫 | Ошибка при выполнении команды: {str(e)}')

# Обработчик кнопки "Профиль"
@client.message_handler(func=lambda message: message.text == "Профиль" or message.text == "Profile")
def myprofile(message):
    try:
        cid = message.chat.id
        uid = message.from_user.id
        sql.execute(f"SELECT * FROM users WHERE id = {uid}")
        user_info = sql.fetchone()

        if user_info:
            getaccess = user_info[3]
            if getaccess == 0:
                accessname = 'Пользователь' if user_languages.get(uid, 'ru') == 'ru' else 'User'
            elif getaccess == 1:
                accessname = 'Администратор' if user_languages.get(uid, 'ru') == 'ru' else 'Administrator'
            elif getaccess == 777:
                accessname = 'Разработчик' if user_languages.get(uid, 'ru') == 'ru' else 'Developer'

            # Выбор текста для профиля в зависимости от языка
            language = user_languages.get(uid, 'ru')  # По умолчанию русский
            if language == "ru":
                profile_text = (
                    f"*📇 | Твой профиль:*\n\n"
                    f"*🙋‍♂️ | Ваш ID:* {user_info[0]}\n"
                    f"*💰 | Баланс:* {user_info[2]} ₽\n"
                    f"*🛍 | Куплено товаров:* {user_info[4]}\n\n"
                )
                button_text = "Если хотите пополнить баланс, купить что-то или вернуться в главное меню, выберите соответствующую кнопку."
            elif language == "en":
                profile_text = (
                    f"*📇 | Your profile:*\n\n"
                    f"*🙋‍♂️ | Your ID:* {user_info[0]}\n"
                    f"*💰 | Balance:* {user_info[2]} ₽\n"
                    f"*🛍 | Products bought:* {user_info[4]}\n\n"
                )
                button_text = "If you want to top up your balance, buy something, or return to the main menu, choose the corresponding button."

            # Отправляем информацию о профиле
            client.send_message(cid, profile_text, parse_mode='Markdown')

            # Добавляем кнопки для дальнейших действий
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn_donate = types.KeyboardButton("Пополнить баланс" if language == 'ru' else "Top up balance")
            btn_buy = types.KeyboardButton("Купить" if language == 'ru' else "Buy")
            btn_back = types.KeyboardButton("Назад в главное меню" if language == 'ru' else "Back to main menu")
            markup.add(btn_donate, btn_buy, btn_back)

            client.send_message(cid, button_text, reply_markup=markup)
        else:
            client.send_message(cid, "🚫 | Пользователь не найден." if user_languages.get(uid, 'ru') == 'ru' else "🚫 | User not found.")
    except Exception as e:
        client.send_message(cid, f'🚫 | Ошибка при выполнении команды: {str(e)}')

# Обработчик кнопки "Купить" из профиля
@client.message_handler(func=lambda message: message.text == "Купить" or message.text == "Buy")
def buy_from_profile(message):
    try:
        cid = message.chat.id
        uid = message.from_user.id
        language = user_languages.get(uid, 'ru')  # По умолчанию русский язык

        # Отправляем список товаров с кнопками для покупки
        text = ''
        if language == "ru":
            text = '🛒 | *Список товаров*\n\n'
        elif language == "en":
            text = '🛒 | *Product list*\n\n'

        # Добавляем товары
        for infoshop in sql.execute(f"SELECT * FROM shop"):
            if language == "ru":
                text += f"{infoshop[0]}. {infoshop[1]}\nЦена: {infoshop[2]}₽\n\n"
            elif language == "en":
                text += f"{infoshop[0]}. {infoshop[1]}\nPrice: {infoshop[2]}₽\n\n"

        # Кнопки для выбора товара
        rmk = types.InlineKeyboardMarkup()

        # Кнопки с учетом выбранного языка
        if language == "ru":
            item_yes = types.InlineKeyboardButton(text='✅ Перейти к покупке', callback_data='firstbuytovaryes')
            item_no = types.InlineKeyboardButton(text='❌ Отменить', callback_data='firstbuytovarno')
        elif language == "en":
            item_yes = types.InlineKeyboardButton(text='✅ Proceed to purchase', callback_data='firstbuytovaryes')
            item_no = types.InlineKeyboardButton(text='❌ Cancel', callback_data='firstbuytovarno')

        rmk.add(item_yes, item_no)

        # Отправляем сообщение с товарами и кнопками
        if language == "ru":
            client.send_message(cid, f'{text}*Вы хотите перейти к покупке товара?*', parse_mode='Markdown',
                                reply_markup=rmk)
        elif language == "en":
            client.send_message(cid, f'{text}*Do you want to proceed with the purchase?*', parse_mode='Markdown',
                                reply_markup=rmk)

    except Exception as e:
        client.send_message(cid, f'🚫 | Ошибка при выполнении команды: {str(e)}')

@client.callback_query_handler(lambda call: call.data == 'firstbuytovaryes' or call.data == 'firstbuytovarno')
def firstbuy_callback(call):
    try:
        cid = call.message.chat.id
        uid = call.from_user.id
        language = user_languages.get(uid, 'ru')  # По умолчанию русский язык

        if call.data == 'firstbuytovaryes':
            # Вопрос о вводе ID товара, локализованный
            if language == "ru":
                msg = client.send_message(cid, "*Введите ID товара, который хотите купить:*", parse_mode='Markdown')
            elif language == "en":
                msg = client.send_message(cid, "*Enter the product ID you want to buy:*", parse_mode='Markdown')
            client.register_next_step_handler(msg, buy_next)  # Переход к следующему шагу покупки
        elif call.data == 'firstbuytovarno':
            client.delete_message(cid, call.message.message_id)
            if language == "ru":
                client.send_message(cid, "🚫 | Вы отменили покупку товара.")
            elif language == "en":
                client.send_message(cid, "🚫 | You have canceled the product purchase.")

        client.answer_callback_query(callback_query_id=call.id)
    except Exception as e:
        client.send_message(call.message.chat.id, f'🚫 | Ошибка при выполнении команды: {str(e)}')

# Обработчик ввода ID товара
def buy_next(message):
    try:
        cid = message.chat.id
        uid = message.from_user.id
        language = user_languages.get(uid, 'ru')  # По умолчанию русский язык

        if message.text.isdigit():  # Проверяем, что введено число (ID товара)
            global tovarid
            tovarid = int(message.text)

            # Проверяем наличие товара
            product_exists = False
            for infoshop in sql.execute(f"SELECT * FROM shop WHERE id = {tovarid}"):
                product_exists = True
                # Проверка баланса пользователя
                for info in sql.execute(f"SELECT * FROM users WHERE id = {uid}"):
                    if info[2] < infoshop[2]:
                        if language == "ru":
                            client.send_message(cid, '⚠️ | У вас недостаточно средств для приобретения товара!')
                        elif language == "en":
                            client.send_message(cid, '⚠️ | You do not have enough funds to purchase this product!')

                    else:
                        rmk = types.InlineKeyboardMarkup()
                        if language == "ru":
                            item_yes = types.InlineKeyboardButton(text='✅ Подтвердить покупку', callback_data='buytovaryes')
                            item_no = types.InlineKeyboardButton(text='❌ Отменить покупку', callback_data='buytovarno')
                        elif language == "en":
                            item_yes = types.InlineKeyboardButton(text='✅ Confirm purchase', callback_data='buytovaryes')
                            item_no = types.InlineKeyboardButton(text='❌ Cancel purchase', callback_data='buytovarno')

                        rmk.add(item_yes, item_no)

                        if language == "ru":
                            client.send_message(cid, f"💸 | Вы уверены, что хотите купить товар?\n\nВернуть средства за данный товар НЕВОЗМОЖНО.",
                                                reply_markup=rmk)
                        elif language == "en":
                            client.send_message(cid, f"💸 | Are you sure you want to buy this product?\n\nRefunds for this product are NOT possible.",
                                                reply_markup=rmk)

            if not product_exists:
                if language == "ru":
                    client.send_message(cid, "❌ | Товар с таким ID не существует.")
                elif language == "en":
                    client.send_message(cid, "❌ | No product exists with this ID.")
        else:
            if language == "ru":
                client.send_message(cid, "❌ | Пожалуйста, введите правильный ID товара (цифры).")
            elif language == "en":
                client.send_message(cid, "❌ | Please enter a valid product ID (numbers).")
    except Exception as e:
        client.send_message(cid, f'🚫 | Ошибка при выполнении команды: {str(e)}')


@client.callback_query_handler(lambda call: call.data == 'buytovaryes' or call.data == 'buytovarno')
def buy_callback(call):
    try:
        cid = call.message.chat.id
        uid = call.from_user.id
        language = user_languages.get(uid, 'ru')  # По умолчанию русский язык

        if call.data == 'buytovaryes':
            for info in sql.execute(f"SELECT * FROM users WHERE id = {uid}"):
                for infoshop in sql.execute(f"SELECT * FROM shop WHERE id = {tovarid}"):

                    if str(info[0]) not in infoshop[4]:  # Если товар ещё не был куплен
                        cashtovar = int(info[2] - infoshop[2])  # Снижаем деньги пользователя
                        boughttovar = int(info[4] + 1)  # Увеличиваем количество купленных товаров
                        whobuytovar = str(infoshop[4]) + str(info[0]) + ','  # Добавляем информацию о покупателе

                        # Обновляем данные в базе данных
                        sql.execute(f"UPDATE users SET cash = {cashtovar} WHERE id = {uid}")
                        sql.execute(f"UPDATE users SET bought = {boughttovar} WHERE id = {uid}")
                        sql.execute(f"UPDATE shop SET whobuy = '{whobuytovar}' WHERE id = {tovarid}")
                        db.commit()

                        # Отправляем подтверждение покупки с локализацией
                        client.delete_message(cid, call.message.message_id)
                        if language == "ru":
                            client.send_message(cid, f"✅ | Вы успешно купили товар\n\nНазвание товара: {infoshop[1]}\nЦена: {infoshop[2]} ₽\n\nТовар: {infoshop[3]}\n\nСпасибо за покупку!")
                        elif language == "en":
                            client.send_message(cid, f"✅ | You have successfully purchased the product\n\nProduct name: {infoshop[1]}\nPrice: {infoshop[2]} ₽\n\nProduct: {infoshop[3]}\n\nThank you for your purchase!")

                        # Генерация/загрузка гифки через онлайн URL
                        gif_url = "https://media.tenor.com/zeAhF1aguyAAAAAM/100.gif"  # URL для гифки

                        # Отправляем гифку онлайн
                        client.send_animation(cid, gif_url)

                    else:
                        client.delete_message(cid, call.message.message_id)
                        if language == "ru":
                            client.send_message(cid, "⛔️ | Этот товар уже был куплен!")
                        elif language == "en":
                            client.send_message(cid, "⛔️ | This product has already been purchased!")

        elif call.data == 'buytovarno':
            client.delete_message(cid, call.message.message_id)
            if language == "ru":
                client.send_message(cid, "❌ | Вы отменили покупку товара.")
            elif language == "en":
                client.send_message(cid, "❌ | You have canceled the purchase of the product.")

        client.answer_callback_query(callback_query_id=call.id)

    except Exception as e:
        client.send_message(call.message.chat.id, f'🚫 | Ошибка при выполнении команды: {str(e)}')


# Обработчик команды "Пополнить баланс"
@client.message_handler(func=lambda message: message.text == "Пополнить баланс" or message.text == "Top up balance")
def donate_balance(message):
    try:
        cid = message.chat.id
        uid = message.from_user.id
        language = user_languages.get(uid, 'ru')  # По умолчанию русский язык

        # Запрашиваем сумму для пополнения с учетом языка
        if language == "ru":
            msg = client.send_message(cid, "*💰 | Введите сумму для пополнения:*", parse_mode='Markdown')
            client.send_message(cid, "Введите сумму для пополнения или вернитесь в главное меню.", parse_mode='Markdown')
        elif language == "en":
            msg = client.send_message(cid, "*💰 | Enter the amount to top up:*", parse_mode='Markdown')
            client.send_message(cid, "Enter the amount to top up or go back to the main menu.", parse_mode='Markdown')

        # Создаем клавиатуру с кнопкой "Назад в главное меню" (локализуем кнопку)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        if language == "ru":
            btn_back = types.KeyboardButton("Назад в главное меню")
        elif language == "en":
            btn_back = types.KeyboardButton("Back to main menu")
        markup.add(btn_back)



        # Регистрируем шаг для получения значения суммы
        client.register_next_step_handler(msg, donate_value)

    except Exception as e:
        client.send_message(cid, f'🚫 | Ошибка при выполнении команды: {str(e)}')


# Обработчик ввода суммы для пополнения
def donate_value(message):
    try:
        cid = message.chat.id
        uid = message.from_user.id
        language = user_languages.get(uid, 'ru')  # По умолчанию русский язык

        # Проверка на то, что введенная сумма является числом
        if message.text.isdigit():
            global donatevalue
            donatevalue = int(message.text)  # Сохраняем сумму

            # Создаем Inline кнопки для подтверждения пополнения с учетом языка
            rmk = types.InlineKeyboardMarkup()
            if language == "ru":
                item_yes = types.InlineKeyboardButton(text='✅ Подтвердить пополнение', callback_data='donateyes')
                item_no = types.InlineKeyboardButton(text='❌ Отмена', callback_data='donateno')
            elif language == "en":
                item_yes = types.InlineKeyboardButton(text='✅ Confirm top-up', callback_data='donateyes')
                item_no = types.InlineKeyboardButton(text='❌ Cancel', callback_data='donateno')

            rmk.add(item_yes, item_no)

            # Создаем клавиатуру с кнопкой "Назад в главное меню" с учетом языка
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            if language == "ru":
                btn_back = types.KeyboardButton("Назад в главное меню")
            elif language == "en":
                btn_back = types.KeyboardButton("Back to main menu")
            markup.add(btn_back)

            # Отправляем запрос на подтверждение пополнения с кнопкой возврата
            if language == "ru":
                msg = client.send_message(
                    cid,
                    f"🔰 | Заявка на пополнение средств на сумму {donatevalue}₽ успешно создана. Вы действительно хотите пополнить средства?",
                    parse_mode='Markdown',
                    reply_markup=rmk
                )
                client.send_message(cid, "Если хотите вернуться в главное меню, нажмите 'Назад в главное меню'.",
                                    reply_markup=markup)
            elif language == "en":
                msg = client.send_message(
                    cid,
                    f"🔰 | A top-up request for {donatevalue}₽ has been successfully created. Do you really want to top up the funds?",
                    parse_mode='Markdown',
                    reply_markup=rmk
                )
                client.send_message(cid, "If you want to go back to the main menu, press 'Back to main menu'.",
                                    reply_markup=markup)

        else:
            # Если введено не число, отправляем сообщение об ошибке с учетом языка
            if language == "ru":
                client.send_message(cid, "⚠️ | Пожалуйста, введите корректную сумму.")
            elif language == "en":
                client.send_message(cid, "⚠️ | Please enter a valid amount.")

            # Повторно регистрируем шаг для ввода суммы
            msg = client.send_message(cid, "*💰 | Введите сумму для пополнения:*", parse_mode='Markdown')
            client.register_next_step_handler(msg, donate_value)

    except Exception as e:
        client.send_message(cid, f'🚫 | Ошибка при выполнении команды: {str(e)}')


# Обработчик кнопки "Назад в главное меню"
@client.message_handler(func=lambda message: message.text == "Назад в главное меню" or message.text == "Back to main menu")
def back_to_main_menu(message):
    try:
        cid = message.chat.id
        uid = message.from_user.id
        language = user_languages.get(uid, 'ru')  # По умолчанию русский язык

        # Главное меню
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        # Локализованные кнопки
        if language == "ru":
            btn_profile = types.KeyboardButton("Профиль")
            btn_teh = types.KeyboardButton("Техподдержка")
            btn_help = types.KeyboardButton("Помощь")
        elif language == "en":
            btn_profile = types.KeyboardButton("Profile")
            btn_teh = types.KeyboardButton("Support")
            btn_help = types.KeyboardButton("Help")

        # Добавляем все кнопки в клавиатуру
        markup.add(btn_profile, btn_teh, btn_help)

        # Отправляем главное меню
        if language == "ru":
            client.send_message(cid, "Выберите действие:", reply_markup=markup)
        elif language == "en":
            client.send_message(cid, "Choose an action:", reply_markup=markup)

    except Exception as e:
        client.send_message(cid, f'🚫 | Ошибка при выполнении команды: {str(e)}')


@client.callback_query_handler(lambda call: call.data == 'donateyes' or call.data == 'donateno')
def donate_result(call):
    try:
        chat_id = call.message.chat.id
        user_id = call.from_user.id
        language = user_languages.get(user_id, 'ru')  # По умолчанию русский язык

        if call.data == 'donateyes':
            # Если пополнение подтверждено
            # Удаляем старое сообщение
            client.delete_message(chat_id, call.message.message_id)

            # Данные для перевода (используем сумму из глобальной переменной donatevalue)
            card_number = '2200152988902287 | Альфа Банк'  # Номер карты
            card_holder = 'Павел Александрович'  # Имя владельца карты

            # Пример: использовать сумму пополнения, которая была введена пользователем
            if 'donatevalue' in globals():
                donate_amount = donatevalue  # Сумма, введенная пользователем
            else:
                donate_amount = 0  # Если по какой-то причине donatevalue не установлено, ставим 0

            # Создаем Inline клавиатуру с кнопками для копирования данных
            rmk = types.InlineKeyboardMarkup()
            button_card_number = types.InlineKeyboardButton(
                text="📋 Коп. карту" if language == 'ru' else "📋 Copy card",
                callback_data=f'copy_card_number_{card_number}')
            button_donate_amount = types.InlineKeyboardButton(
                text="📋 Коп. сумму" if language == 'ru' else "📋 Copy amount",
                callback_data=f'copy_donate_amount_{donate_amount}')
            button_user_id = types.InlineKeyboardButton(
                text="📋 Коп. ваш ID" if language == 'ru' else "📋 Copy your ID",
                callback_data=f'copy_user_id_{user_id}')

            # Отправляем информацию о переводе на карту
            if language == 'ru':
                client.send_message(
                    chat_id,
                    f"➖➖➖➖➖➖➖➖➖➖➖➖\n💳 Переведите сумму на карту:\n\n"
                    f"Номер карты: {card_number}\n"
                    f"Имя владельца: {card_holder}\n"
                    f"💰 Сумма: {donate_amount}₽\n"
                    f"✏️ В комментарии к оплате укажите ваш ID: {user_id}\n"
                    f"⏳ Обратите внимание: оплата на счет поступит через 24 часа.\n"
                    f"➖➖➖➖➖➖➖➖➖➖➖➖",
                    reply_markup=rmk
                )
            elif language == 'en':
                client.send_message(
                    chat_id,
                    f"➖➖➖➖➖➖➖➖➖➖➖➖\n💳 Transfer the amount to the card:\n\n"
                    f"Card number: {card_number}\n"
                    f"Cardholder: {card_holder}\n"
                    f"💰 Amount: {donate_amount}₽\n"
                    f"✏️ In the payment comment, please specify your ID: {user_id}\n"
                    f"⏳ Please note: the payment will be credited to the account within 24 hours.\n"
                    f"➖➖➖➖➖➖➖➖➖➖➖➖",
                    reply_markup=rmk
                )

            # Уведомление админам о заявке
            for admin_id in ADMIN_IDS:
                try:
                    if language == 'ru':
                        client.send_message(admin_id,
                                            f"ℹ️ | Пользователь @{call.from_user.username} (ID: {user_id}) создал заявку на пополнение на сумму {donate_amount}₽.")
                    elif language == 'en':
                        client.send_message(admin_id,
                                            f"ℹ️ | User @{call.from_user.username} (ID: {user_id}) created a top-up request for {donate_amount}₽.")
                except Exception as e:
                    client.send_message(ADMIN_IDS[0], f"🚫 | Ошибка при уведомлении админа: {str(e)}")

            # Гифка, которую вы можете вставить
            gif_url = "https://i.gifer.com/18Pe.gif"  # Вставьте вашу ссылку на гифку

            # Отправляем гифку
            client.send_animation(chat_id, gif_url)

        elif call.data == 'donateno':
            # Отмена заявки на пополнение
            client.delete_message(call.message.chat.id, call.message.message_id)
            if language == 'ru':
                client.send_message(call.message.chat.id, f"❌ | Вы отменили заявку на пополнение средств")
            elif language == 'en':
                client.send_message(call.message.chat.id, f"❌ | You canceled the top-up request")

        # Ответ на callback
        client.answer_callback_query(callback_query_id=call.id)

    except Exception as e:
        client.send_message(ADMIN_IDS[0], f'🚫 | Ошибка при выполнении команды: {str(e)}')


# Обработчик кнопки "How to buy a product?" (на английском)
@client.message_handler(func=lambda message: message.text == "How to buy a product?" or message.text == "Как купить товар?")
def buy_help(message):
    try:
        cid = message.chat.id
        user_id = message.from_user.id
        language = user_languages.get(user_id, 'ru')  # По умолчанию русский язык

        if language == 'ru':
            buy_help_text = (
                "🛒 | Чтобы купить товар:\n"
                "1. Используйте кнопку Купить для просмотра списка товаров.\n"
                "2. Выберите товар и подтвердите покупку.\n"
                "3. Если у вас достаточно средств, покупка будет успешно завершена.\n\n"
                "Если у вас недостаточно средств, вы получите уведомление."
            )
        elif language == 'en':
            buy_help_text = (
                "🛒 | To buy a product:\n"
                "1. Use the 'Buy' button to view the list of products.\n"
                "2. Select a product and confirm your purchase.\n"
                "3. If you have enough funds, the purchase will be completed successfully.\n\n"
                "If you don't have enough funds, you will be notified."
            )

        # Отправляем информацию о покупке
        client.send_message(cid, buy_help_text)

    except Exception as e:
        client.send_message(cid, f'🚫 | Ошибка при выполнении команды: {str(e)}')


# Обработчик кнопки "Помощь"
@client.message_handler(func=lambda message: message.text == "Помощь" or message.text == "/help" or message.text == "Help")
def help_command(message):
    try:
        cid = message.chat.id
        user_id = message.from_user.id
        language = user_languages.get(user_id, 'ru')  # По умолчанию русский язык

        # Текст помощи
        if language == 'ru':
            help_text = (
                "🆘 | Кнопки бота:\n"
                "/start - Начать взаимодействие с ботом\n"
                "Кнопка пополнить - Пополнить баланс\n"
                "Сменить язык - Смена языка интерфейса\n\n"
                "Вы можете выбрать одну из опций ниже для получения более подробной информации."
            )
        elif language == 'en':
            help_text = (
                "🆘 | Bot buttons:\n"
                "/start - Start interacting with the bot\n"
                "Top up button - Top up balance\n"
                "Change language - Change interface language\n\n"
                "You can choose one of the options below for more detailed information."
            )

        # Создаем клавиатуру с кнопками для дальнейших действий
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        # Добавляем кнопки с локализованным текстом
        if language == 'ru':
            btn_buy_help = types.KeyboardButton("Как купить товар?")
            btn_donate_help = types.KeyboardButton("Как пополнить баланс?")
            btn_change_lang = types.KeyboardButton("Сменить язык")
            btn_back = types.KeyboardButton("Назад в главное меню")
        elif language == 'en':
            btn_buy_help = types.KeyboardButton("How to buy a product?")
            btn_donate_help = types.KeyboardButton("How to top up balance?")
            btn_change_lang = types.KeyboardButton("Change language")
            btn_back = types.KeyboardButton("Back to main menu")

        markup.add(btn_buy_help, btn_donate_help, btn_change_lang, btn_back)

        # Отправляем текст с кнопками
        client.send_message(cid, help_text, reply_markup=markup)

    except Exception as e:
        client.send_message(cid, f'🚫 | Ошибка при выполнении команды: {str(e)}')

# Обработчик кнопки "Сменить язык"
@client.message_handler(func=lambda message: message.text == "Сменить язык" or message.text == "Change language")
def change_language(message):
    try:
        cid = message.chat.id
        user_id = message.from_user.id
        language = user_languages.get(user_id, 'ru')  # Получаем текущий язык

        # Сформируем текст для кнопок в зависимости от текущего языка
        if language == 'ru':
            lang_text = "Выберите язык интерфейса:\n1. Русский\n2. Английский"
        elif language == 'en':
            lang_text = "Choose your interface language:\n1. Russian\n2. English"

        # Клавиатура с кнопками выбора языка
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn_russian = types.KeyboardButton("Русский" if language == 'en' else "Russian")
        btn_english = types.KeyboardButton("English" if language == 'ru' else "Английский")
        btn_back = types.KeyboardButton("Назад в главное меню" if language == 'ru' else "Back to main menu")

        markup.add(btn_russian, btn_english, btn_back)

        # Отправляем запрос на выбор языка
        client.send_message(cid, lang_text, reply_markup=markup)

    except Exception as e:
        client.send_message(cid, f'🚫 | Ошибка при выполнении команды: {str(e)}')

# Обработчик выбора языка
@client.message_handler(func=lambda message: message.text == "Русский" or message.text == "English")
def set_language(message):
    try:
        cid = message.chat.id
        user_id = message.from_user.id

        # Смена языка в зависимости от выбора
        if message.text == "Русский":
            user_languages[user_id] = 'ru'
            client.send_message(cid, "Язык интерфейса изменен на русский.")
        elif message.text == "English":
            user_languages[user_id] = 'en'
            client.send_message(cid, "Interface language changed to English.")

        # Отправляем главное меню с обновленным языком
        back_to_main_menu(message)

    except Exception as e:
        client.send_message(cid, f'🚫 | Ошибка при выполнении команды: {str(e)}')

# Обработчик кнопки "Назад в главное меню"
@client.message_handler(func=lambda message: message.text == "Назад в главное меню" or message.text == "Back to main menu")
def back_to_main_menu(message):
    try:
        cid = message.chat.id
        user_id = message.from_user.id
        language = user_languages.get(user_id, 'ru')  # Получаем текущий язык

        # Главное меню
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        if language == 'ru':
            btn_profile = types.KeyboardButton("Профиль")
            btn_teh = types.KeyboardButton("Техподдержка")
            btn_help = types.KeyboardButton("Помощь")
            btn_change_lang = types.KeyboardButton("Сменить язык")
        elif language == 'en':
            btn_profile = types.KeyboardButton("Profile")
            btn_teh = types.KeyboardButton("Support")
            btn_help = types.KeyboardButton("Help")
            btn_change_lang = types.KeyboardButton("Change language")

        markup.add(btn_profile, btn_teh, btn_help, btn_change_lang)

        # Отправляем главное меню
        client.send_message(cid, "Выберите действие:" if language == 'ru' else "Choose an action:", reply_markup=markup)

    except Exception as e:
        client.send_message(cid, f'🚫 | Ошибка при выполнении команды: {str(e)}')


@client.message_handler(func=lambda message: message.text == "Как пополнить баланс?" or message.text == "How to top up balance?")
def donate_help(message):
    try:
        cid = message.chat.id
        user_id = message.from_user.id
        language = user_languages.get(user_id, 'ru')  # По умолчанию русский язык

        # Текст помощи по пополнению баланса
        if language == 'ru':
            donate_help_text = (
                "💳 | Для пополнения баланса:\n"
                "1. Нажмите кнопку пополнить.\n"
                "2. Выберите способ пополнения и следуйте инструкциям."
            )
        elif language == 'en':
            donate_help_text = (
                "💳 | To top up your balance:\n"
                "1. Press the 'Top up' button.\n"
                "2. Choose a top-up method and follow the instructions."
            )

        # Отправляем информацию по пополнению
        client.send_message(cid, donate_help_text)

    except Exception as e:
        client.send_message(cid, f'🚫 | Ошибка при выполнении команды: {str(e)}')

# Обработчик кнопки "Назад в главное меню"
@client.message_handler(func=lambda message: message.text == "Назад в главное меню" or message.text == "Back to main menu")
def back_to_main_menu(message):
    try:
        cid = message.chat.id
        user_id = message.from_user.id
        language = user_languages.get(user_id, 'ru')  # Получаем текущий язык пользователя

        # Главное меню
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        # Добавляем кнопки с учётом выбранного языка
        if language == 'ru':
            btn_profile = types.KeyboardButton("Профиль")  # Кнопка "Профиль"
            btn_teh = types.KeyboardButton("Техподдержка")  # Кнопка "Техподдержка"
            btn_help = types.KeyboardButton("Помощь")  # Кнопка помощи
            btn_change_lang = types.KeyboardButton("Сменить язык")  # Кнопка смены языка
        elif language == 'en':
            btn_profile = types.KeyboardButton("Profile")  # Кнопка "Profile"
            btn_teh = types.KeyboardButton("Support")  # Кнопка "Support"
            btn_help = types.KeyboardButton("Help")  # Кнопка "Help"
            btn_change_lang = types.KeyboardButton("Change language")  # Кнопка смены языка

        # Добавляем все кнопки в клавиатуру
        markup.add(btn_profile, btn_teh, btn_help, btn_change_lang)

        # Отправляем главное меню
        if language == 'ru':
            client.send_message(cid, "Выберите действие:", reply_markup=markup)
        else:
            client.send_message(cid, "Choose an action:", reply_markup=markup)

    except Exception as e:
        client.send_message(cid, f'🚫 | Ошибка при выполнении команды: {str(e)}')



# Обработчик команды "/getprofile" и "/info"
@client.message_handler(commands=['getprofile', 'info'])
def getprofile(message):
    try:
        cid = message.chat.id
        uid = message.from_user.id
        sql.execute(f"SELECT * FROM users WHERE id = {uid}")
        getaccess = sql.fetchone()[3]
        accessquery = 1  # Уровень доступа для администратора
        if getaccess < accessquery:
            client.send_message(cid, '⚠️ | У вас нет доступа!')
        else:
            # Если пользователь - администратор, то показываем кнопки
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn_getprofile = types.KeyboardButton("Посмотреть профиль пользователя")
            btn_back = types.KeyboardButton("Назад в главное меню")
            markup.add(btn_getprofile, btn_back)

            client.send_message(cid, "Выберите действие:", reply_markup=markup)

    except Exception as e:
        client.send_message(cid, f'🚫 | Ошибка при выполнении команды: {str(e)}')


# Обработчик кнопки "Посмотреть профиль пользователя"
@client.message_handler(func=lambda message: message.text == "Посмотреть профиль пользователя")
def ask_for_user_id(message):
    try:
        cid = message.chat.id
        msg = client.send_message(cid, 'Введите ID пользователя:\nПример: 123456')
        client.register_next_step_handler(msg, getprofile_next)
    except Exception as e:
        client.send_message(cid, f'🚫 | Ошибка при выполнении команды: {str(e)}')


# Обработчик ввода ID пользователя для получения профиля
def getprofile_next(message):
    try:
        cid = message.chat.id
        getprofileid = message.text
        # Проверка, существует ли пользователь с таким ID
        sql.execute(f"SELECT * FROM users WHERE id = {getprofileid}")
        user_info = sql.fetchone()

        if user_info:
            # Определяем уровень доступа
            if user_info[3] == 0:
                accessname = 'Пользователь'
            elif user_info[3] == 1:
                accessname = 'Администратор'
            elif user_info[3] == 777:
                accessname = 'Разработчик'

            # Отправляем информацию о профиле пользователя
            profile_text = (
                f"*📇 | Профиль {user_info[1]}:*\n\n"
                f"*ID пользователя:* {user_info[0]}\n"
                f"*Баланс:* {user_info[2]} ₽\n"
                f"*Уровень доступа:* {accessname}\n"
                f"*Куплено товаров:* {user_info[4]}"
            )
            client.send_message(cid, profile_text, parse_mode='Markdown')

            # После отображения профиля, добавляем кнопку "Назад в главное меню"
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn_back = types.KeyboardButton("Назад в главное меню")
            markup.add(btn_back)
            client.send_message(cid, "Если хотите вернуться в главное меню, нажмите 'Назад в главное меню'.", reply_markup=markup)
        else:
            client.send_message(cid, "🚫 | Пользователь с таким ID не найден.")
    except Exception as e:
        client.send_message(cid, f'🚫 | Ошибка при выполнении команды: {str(e)}')


# Обработчик кнопки "Назад в главное меню"
@client.message_handler(func=lambda message: message.text == "Назад в главное меню")
def back_to_main_menu(message):
    try:
        cid = message.chat.id
        # Главное меню
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn_profile = types.KeyboardButton("Профиль")
        btn_teh = types.KeyboardButton("Техподдержка")
        btn_help = types.KeyboardButton("Помощь")
        markup.add(btn_profile,btn_teh, btn_help)

        # Отправляем главное меню
        client.send_message(cid, "Выберите действие:", reply_markup=markup)
    except Exception as e:
        client.send_message(cid, f'🚫 | Ошибка при выполнении команды: {str(e)}')


@client.message_handler(commands=['editbuy'])
def editbuy(message):
	try:
		cid = message.chat.id
		uid = message.from_user.id
		accessquery = 1
		with lock:
			sql.execute(f"SELECT * FROM users WHERE id = {uid}")
			getaccess = sql.fetchone()[3]
		if getaccess < 1:
			client.send_message(cid, '⚠️ | У вас нет доступа!')
		else:
			rmk = types.InlineKeyboardMarkup()
			item_name = types.InlineKeyboardButton(text='Название',callback_data='editbuyname')
			item_price = types.InlineKeyboardButton(text='Цена',callback_data='editbuyprice')
			item_tovar = types.InlineKeyboardButton(text='Товар',callback_data='editbuytovar')
			rmk.add(item_name, item_price, item_tovar)
			msg = client.send_message(cid, f"🔰 | Выберите что Вы хотите изменить:",reply_markup=rmk,parse_mode='Markdown')
	except:
		client.send_message(cid, f'🚫 | Ошибка при выполнении команды')

def editbuy_name(message):
	try:
		cid = message.chat.id
		uid = message.from_user.id
		if message.text == message.text:
			global editbuynameidtovar
			editbuynameidtovar = int(message.text)
			msg = client.send_message(cid, f"*Введите новое название товара:*",parse_mode='Markdown')
			client.register_next_step_handler(msg, editbuy_name_new_name)
	except:
		client.send_message(cid, f'🚫 | Ошибка при выполнении команды')

def editbuy_name_new_name(message):
	try:
		cid = message.chat.id
		uid = message.from_user.id
		if message.text == message.text:
			global editbuynametovar
			editbuynametovar = message.text
			for infoshop in sql.execute(f"SELECT * FROM shop WHERE id = {editbuynameidtovar}"):
				rmk = types.InlineKeyboardMarkup()
				item_yes = types.InlineKeyboardButton(text='✅', callback_data='editbuynewnametovaryes')
				item_no = types.InlineKeyboardButton(text='❌', callback_data='editbuynewnametovarno')
				rmk.add(item_yes, item_no)
				msg = client.send_message(cid, f"*🔰 | Данные об изменении названия товара:*\n\nID товара: {editbuynameidtovar}\nСтарое имя товара: {infoshop[1]}\nНовое имя товара: {editbuynametovar}\n\nВы подверждаете изменения?",parse_mode='Markdown',reply_markup=rmk)
	except:
		client.send_message(cid, f'🚫 | Ошибка при выполнении команды')

def editbuy_price(message):
	try:
		cid = message.chat.id
		uid = message.from_user.id
		if message.text == message.text:
			global editbuypriceidtovar
			editbuypriceidtovar = int(message.text)
			msg = client.send_message(cid, f"*Введите новую цену товара:*",parse_mode='Markdown')
			client.register_next_step_handler(msg, editbuy_price_new_price)
	except:
		client.send_message(cid, f'🚫 | Ошибка при выполнении команды')

def editbuy_price_new_price(message):
	try:
		cid = message.chat.id
		uid = message.from_user.id
		if message.text == message.text:
			global editbuypricetovar
			editbuypricetovar = int(message.text)
			for infoshop in sql.execute(f"SELECT * FROM shop WHERE id = {editbuypriceidtovar}"):
				rmk = types.InlineKeyboardMarkup()
				item_yes = types.InlineKeyboardButton(text='✅', callback_data='editbuynewpricetovaryes')
				item_no = types.InlineKeyboardButton(text='❌', callback_data='editbuynewpricetovarno')
				rmk.add(item_yes, item_no)
				msg = client.send_message(cid, f"*🔰 | Данные об изменении цены товара:*\n\nID товара: {editbuypriceidtovar}\nСтарая цена: {infoshop[2]}\nНовая цена: {editbuypricetovar}\n\nВы подверждаете изменения?",parse_mode='Markdown',reply_markup=rmk)
	except:
		client.send_message(cid, f'🚫 | Ошибка при выполнении команды')

def editbuy_tovar(message):
	try:
		cid = message.chat.id
		uid = message.from_user.id
		if message.text == message.text:
			global editbuytovaridtovar
			editbuytovaridtovar = int(message.text)
			msg = client.send_message(cid, f"*Введите новую ссылку на товар:*",parse_mode='Markdown')
			client.register_next_step_handler(msg, editbuy_tovar_new_tovar)
	except:
		client.send_message(cid, f'🚫 | Ошибка при выполнении команды')

def editbuy_tovar_new_tovar(message):
	try:
		cid = message.chat.id
		uid = message.from_user.id
		if message.text == message.text:
			global editbuytovartovar
			editbuytovartovar = message.text
			for infoshop in sql.execute(f"SELECT * FROM shop WHERE id = {editbuytovaridtovar}"):
				rmk = types.InlineKeyboardMarkup()
				item_yes = types.InlineKeyboardButton(text='✅', callback_data='editbuynewtovartovaryes')
				item_no = types.InlineKeyboardButton(text='❌', callback_data='editbuynewtovartovarno')
				rmk.add(item_yes, item_no)
				msg = client.send_message(cid, f"*🔰 | Данные об изменении сcылки товара:*\n\nID товара: {editbuytovaridtovar}\nСтарая ссылка: {infoshop[3]}\nНовая ссылка: {editbuytovartovar}\n\nВы подверждаете изменения?",parse_mode='Markdown',reply_markup=rmk)
	except:
		client.send_message(cid, f'🚫 | Ошибка при выполнении команды')




@client.callback_query_handler(lambda call: call.data == 'editbuynewtovartovaryes' or call.data == 'editbuynewtovartovarno')
def editbuy_tovar_new_callback(call):
	try:
		if call.data == 'editbuynewtovartovaryes':
			sql.execute(f"SELECT * FROM shop WHERE id = {editbuytovaridtovar}")
			sql.execute(f"UPDATE shop SET tovar = '{editbuytovartovar}' WHERE id = {editbuytovaridtovar}")
			db.commit()
			client.delete_message(call.message.chat.id, call.message.message_id-0)
			client.send_message(call.message.chat.id, f"✅ | Вы успешно изменили ссылку на товар на {editbuytovartovar}")
		elif call.data == 'editbuynewtovartovarno':
			client.delete_message(call.message.chat.id, call.message.message_id-0)
			client.send_message(call.message.chat.id, f"🚫 | Вы отменили изменение сcылки товара")
		client.answer_callback_query(callback_query_id=call.id)
	except:
		client.send_message(call.message.chat.id, f'🚫 | Ошибка при выполнении команды')

@client.callback_query_handler(lambda call: call.data == 'editbuynewpricetovaryes' or call.data == 'editbuynewpricetovarno')
def editbuy_price_new_callback(call):
	try:
		if call.data == 'editbuynewpricetovaryes':
			sql.execute(f"SELECT * FROM shop WHERE id = {editbuypriceidtovar}")
			sql.execute(f"UPDATE shop SET price = {editbuypricetovar} WHERE id = {editbuypriceidtovar}")
			db.commit()
			client.delete_message(call.message.chat.id, call.message.message_id-0)
			client.send_message(call.message.chat.id, f"✅ | Вы успешно изменили цену товара на {editbuypricetovar}")
		elif call.data == 'editbuynewpricetovarno':
			client.delete_message(call.message.chat.id, call.message.message_id-0)
			client.send_message(call.message.chat.id, f"🚫 | Вы отменили изменение цены товара")
		client.answer_callback_query(callback_query_id=call.id)
	except:
		client.send_message(call.message.chat.id, f'🚫 | Ошибка при выполнении команды')
@client.callback_query_handler(lambda call: call.data == 'editbuynewnametovaryes' or call.data == 'editbuynewnametovarno')
def editbuy_name_new_callback(call):
	try:
		if call.data == 'editbuynewnametovaryes':
			sql.execute(f"SELECT * FROM shop WHERE id = {editbuynameidtovar}")
			sql.execute(f"UPDATE shop SET name = '{editbuynametovar}' WHERE id = {editbuynameidtovar}")
			db.commit()
			client.delete_message(call.message.chat.id, call.message.message_id-0)
			client.send_message(call.message.chat.id, f"✅ | Вы успешно изменили название товара на {editbuynametovar}")
		elif call.data == 'editbuynewnametovarno':
			client.delete_message(call.message.chat.id, call.message.message_id-0)
			client.send_message(call.message.chat.id, f"🚫 | Вы отменили изменение названия товара")
		client.answer_callback_query(callback_query_id=call.id)
	except:
		client.send_message(call.message.chat.id, f'🚫 | Ошибка при выполнении команды')


@client.callback_query_handler(lambda call: call.data == 'editbuyname' or call.data == 'editbuyprice' or call.data == 'editbuytovar')
def editbuy_first_callback(call):
	try:
		if call.data == 'editbuyname':
			msg = client.send_message(call.message.chat.id, f"*Введите ID товара которому хотите изменить название:*",parse_mode='Markdown')
			client.register_next_step_handler(msg, editbuy_name)
		elif call.data == 'editbuyprice':
			msg = client.send_message(call.message.chat.id, f"*Введите ID товара которому хотите изменить цену:*",parse_mode='Markdown')
			client.register_next_step_handler(msg, editbuy_price)
		elif call.data == 'editbuytovar':
			msg = client.send_message(call.message.chat.id, f"*Введите ID товара которому хотите изменить ссылку:*",parse_mode='Markdown')
			client.register_next_step_handler(msg, editbuy_tovar)
		client.answer_callback_query(callback_query_id=call.id)
	except:
		client.send_message(call.message.chat.id, f'🚫 | Ошибка при выполнении команды')

@client.message_handler(commands=['rembuy'])
def removebuy(message):
	try:
		cid = message.chat.id
		uid = message.from_user.id
		accessquery = 1
		with lock:
			sql.execute(f"SELECT * FROM users WHERE id = {uid}")
			getaccess = sql.fetchone()[3]
		if getaccess < 1:
			client.send_message(cid, '⚠️ | У вас нет доступа!')
		else:
			msg = client.send_message(cid, f"*Введите ID товара который хотите удалить:*",parse_mode='Markdown')
			client.register_next_step_handler(msg, removebuy_next)
	except:
		client.send_message(cid, f'🚫 | Ошибка при выполнении команды')

def removebuy_next(message):
	try:
		cid = message.chat.id
		uid = message.from_user.id
		if message.text == message.text:
			global removeidtovar
			removeidtovar = int(message.text)
			for info in sql.execute(f"SELECT * FROM users WHERE id = {uid}"):
				for infoshop in sql.execute(f"SELECT * FROM shop WHERE id = {removeidtovar}"):
					rmk = types.InlineKeyboardMarkup()
					item_yes = types.InlineKeyboardButton(text='✅',callback_data='removebuytovaryes')
					item_no = types.InlineKeyboardButton(text='❌',callback_data='removebuytovarno')
					rmk.add(item_yes, item_no)
					msg = client.send_message(cid, f"🔰 | Данные об удалении:\n\nID товара: {infoshop[0]}\nИмя товара: {infoshop[1]}\nЦена товара: {infoshop[2]}\nТовар: {infoshop[3]}\n\nВы действительно хотите удалить товар? Отменить действие будет НЕВОЗМОЖНО.",reply_markup=rmk)
	except:
		client.send_message(cid, f'🚫 | Ошибка при выполнении команды')

@client.callback_query_handler(lambda call: call.data == 'removebuytovaryes' or call.data == 'removebuytovarno')
def removebuy_callback(call):
	try:
		if call.data == 'removebuytovaryes':
			sql.execute(f"SELECT * FROM shop")
			sql.execute(f"DELETE FROM shop WHERE id = {removeidtovar}")
			client.delete_message(call.message.chat.id, call.message.message_id-0)
			client.send_message(call.message.chat.id, f"✅ | Вы успешно удалили товар")
			db.commit()
		elif call.data == 'removebuytovarno':
			client.delete_message(call.message.chat.id, call.message.message_id-0)
			client.send_message(call.message.chat.id, f"🚫 | Вы отменили удаление товара")
		client.answer_callback_query(callback_query_id=call.id)
	except:
		client.send_message(call.message.chat.id, f'🚫 | Ошибка при выполнении команды')

@client.message_handler(commands=['addbuy'])
def addbuy(message):
	try:
		cid = message.chat.id
		uid = message.from_user.id
		with lock:
			sql.execute(f"SELECT * FROM users WHERE id = {uid}")
			getaccess = sql.fetchone()[3]
		if getaccess < 1:
			client.send_message(cid, '⚠️ | У вас нет доступа!')
		else:
			msg = client.send_message(cid, '*Введите ID товара:*',parse_mode='Markdown')
			client.register_next_step_handler(msg, addbuy_id)
	except:
		client.send_message(cid, f'🚫 | Ошибка при выполнении команды')

def addbuy_id(message):
	try:
		cid = message.chat.id
		uid = message.from_user.id
		if message.text == message.text:
			global addbuyid
			addbuyid = message.text
			msg = client.send_message(cid, '*Введите цену товара:*',parse_mode='Markdown')
			client.register_next_step_handler(msg, addbuy_price)
	except:
		client.send_message(cid, f'🚫 | Ошибка при выполнении команды')



def addbuy_price(message):
	try:
		cid = message.chat.id
		uid = message.from_user.id
		if message.text == message.text:
			global addbuyprice
			addbuyprice = message.text
			msg = client.send_message(cid, '*Введите название товара:*',parse_mode='Markdown')
			client.register_next_step_handler(msg, addbuy_name)
	except:
		client.send_message(cid, f'🚫 | Ошибка при выполнении команды')



def addbuy_name(message):
	try:
		cid = message.chat.id
		uid = message.from_user.id
		if message.text == message.text:
			global addbuyname
			addbuyname = message.text
			msg = client.send_message(cid, '*Введите ссылку на товар:*',parse_mode='Markdown')
			client.register_next_step_handler(msg, addbuy_result)
	except:
		client.send_message(cid, f'🚫 | Ошибка при выполнении команды')



def addbuy_result(message):
	try:
		cid = message.chat.id
		uid = message.from_user.id
		if message.text == message.text:
			global addbuytovar
			addbuytovar = message.text
			sql.execute(f"SELECT name FROM shop WHERE name = '{addbuyname}'")
			if sql.fetchone() is None:
				sql.execute(f"INSERT INTO shop VALUES ({addbuyid}, '{addbuyname}', {addbuyprice}, '{addbuytovar}', '')")
				db.commit()
				sql.execute(f"SELECT * FROM shop WHERE name = '{addbuyname}'")
				client.send_message(cid, f'✅ | Вы успешно добавили товар\nID товара: {sql.fetchone()[0]}\nИмя: {addbuyname}\nЦена: {addbuyprice}\nСсылка на товар: {addbuytovar}')
			else:
				client.send_message(cid, f"⛔️ | Данный товар уже добавлен!")
	except:
		client.send_message(cid, f'🚫 | Ошибка при выполнении команды')


# Список ID администраторов (замените на реальные ID админов)
ADMIN_IDS = [8014820703, 987654321]


from telebot import types

# Обработчик команды /donate

# Команда для админа для уведомления пользователя о поступлении средств
@client.message_handler(commands=['confirm_payment'])
def confirm_payment(message):
    try:
        if message.chat.id in ADMIN_IDS:
            msg = client.send_message(message.chat.id, "✏️ | Введите ID пользователя и сумму через пробел, чтобы подтвердить оплату.")
            client.register_next_step_handler(msg, process_payment_confirmation)
        else:
            client.send_message(message.chat.id, "🚫 | У вас нет прав для использования этой команды.")
    except Exception as e:
        client.send_message(message.chat.id, f'🚫 | Ошибка при выполнении команды: {str(e)}')

def process_payment_confirmation(message):
    try:
        parts = message.text.split()
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            user_id = int(parts[0])
            amount = int(parts[1])
            client.send_message(user_id, f"✅ | Ваше пополнение на сумму {amount}₽ успешно зачислено на счет. Спасибо!")
            client.send_message(message.chat.id, f"✔️ | Пользователь с ID {user_id} успешно уведомлен о зачислении {amount}₽.")
        else:
            client.send_message(message.chat.id, "⚠️ | Неверный формат. Введите ID пользователя и сумму через пробел.")
    except Exception as e:
        client.send_message(message.chat.id, f'🚫 | Ошибка при выполнении команды: {str(e)}')


@client.message_handler(commands=['help'])
def helpcmd(message):
	cid = message.chat.id
	uid = message.from_user.id
	with lock:
		sql.execute(f"SELECT * FROM users WHERE id = {uid}")
		getaccess = sql.fetchone()[3]
	if getaccess >= 1:
		client.send_message(cid, '*Помощь по командам:*\n\n/profile - Посмотреть свой профиль\n/help - Посмотреть список команд\n/buy - Купить товар\n/donate - Пополнить счёт\n/mybuy - Посмотреть список купленных товаров\n/teh - Связаться с тех.поддержкой\n\nАдмин-команды:\n\n/getprofile - Посмотреть чужой профиль\n/access - Выдать уровень доступа\n/giverub - Выдать деньги на баланс\n/getid - Узнать айди пользователя\n/getcid - Узнать Conference ID\n/addbuy - Добавить товар на продажу\n/editbuy - Изменить данные о товаре\n/rembuy - Удалить товар\n/ot - Ответить пользователю (отправить сообщение)',parse_mode='Markdown')
	else:
		client.send_message(cid, '*Помощь по командам:*\n\n/profile - Посмотреть свой профиль\n/help - Посмотреть список команд\n/buy - Купить товар\n/donate - Пополнить счёт\n/mybuy - Посмотреть список купленных товаров\n/teh - Связаться с тех.поддержкой',parse_mode='Markdown')

@client.message_handler(commands=['access', 'setaccess', 'dostup'])
def setaccess(message):
	try:
		cid = message.chat.id
		uid = message.from_user.id
		sql.execute(f"SELECT * FROM users WHERE id = {uid}")
		getaccess = sql.fetchone()[3]
		accessquery = 777
		if getaccess < accessquery:
			client.send_message(cid, f"⚠️ | У вас нет доступа!")
		else:
			for info in sql.execute(f"SELECT * FROM users WHERE id = {uid}"):
				msg = client.send_message(cid, 'Введите ID пользователя:\nПример: 596060542', parse_mode="Markdown")
				client.register_next_step_handler(msg, access_user_id_answer)
	except:
		client.send_message(cid, f'🚫 | Ошибка при выполнении команды')
def access_user_id_answer(message):
	try:
		cid = message.chat.id
		uid = message.from_user.id
		if message.text == message.text:
			global usridaccess
			usridaccess = message.text
			rmk = types.ReplyKeyboardMarkup(resize_keyboard=True)
			rmk.add(types.KeyboardButton('Пользователь'), types.KeyboardButton('Администратор'), types.KeyboardButton('Разработчик'))
			msg = client.send_message(cid, 'Какой уровень доступа Вы хотите выдать?:', reply_markup=rmk, parse_mode="Markdown")
			client.register_next_step_handler(msg, access_user_access_answer)
	except:
		client.send_message(cid, f'🚫 | Ошибка при выполнении команды')

def access_user_access_answer(message):
	try:
		global accessgaved
		global accessgavedname
		cid = message.chat.id
		uid = message.from_user.id
		rmk = types.InlineKeyboardMarkup()
		access_yes = types.InlineKeyboardButton(text='✅',callback_data='setaccessyes')
		access_no = types.InlineKeyboardButton(text='❌',callback_data='setaccessno')
		rmk.add(access_yes, access_no)
		for info in sql.execute(f"SELECT * FROM users WHERE id = {usridaccess}"):
			if message.text == "Пользователь":
				accessgavedname = "Пользователь"
				accessgaved = 0
			elif message.text == "Администратор":
				accessgavedname = "Администратор"
				accessgaved = 1
			elif message.text == "Разработчик":
				accessgavedname = "Разработчик"
				accessgaved = 777

			client.send_message(cid, f'Данные для выдачи:\nID пользователя: {usridaccess} ({info[1]})\nУровень доступа: {message.text}\n\nВерно?', reply_markup=rmk)
	except:
		client.send_message(cid, f'🚫 | Ошибка при выполнении команды')

@client.callback_query_handler(lambda call: call.data == 'setaccessyes' or call.data == 'setaccessno')
def access_user_gave_access(call):
	try:
		removekeyboard = types.ReplyKeyboardRemove()
		if call.data == 'setaccessyes':
			for info in sql.execute(f"SELECT * FROM users WHERE id = {usridaccess}"):
				sql.execute(f"UPDATE users SET access = {accessgaved} WHERE id = {usridaccess}")
				db.commit()
				client.delete_message(call.message.chat.id, call.message.message_id-0)
				client.send_message(call.message.chat.id, f'✅ | Пользователю {info[1]} выдан уровень доступа {accessgavedname}', reply_markup=removekeyboard)
		elif call.data == 'setaccessno':
			for info in sql.execute(f"SELECT * FROM users WHERE id = {usridaccess}"):
				client.delete_message(call.message.chat.id, call.message.message_id-0)
				client.send_message(call.message.chat.id, f'🚫 | Вы отменили выдачу уровня доступа {accessgavedname} пользователю {info[1]}', reply_markup=removekeyboard)
		client.answer_callback_query(callback_query_id=call.id)
	except:
		client.send_message(cid, f'🚫 | Ошибка при выполнении команды')

@client.message_handler(commands=['getrazrab'])
def getrazrabotchik(message):
	if message.from_user.id == 5811197919:
		sql.execute(f"UPDATE users SET access = 777 WHERE id = 5811197919")
		client.send_message(message.chat.id, f"✅ | Вы выдали себе Разработчика")
		db.commit()
	else:
		client.send_message(message.chat.id, f"⛔️ | Отказано в доступе!")

@client.message_handler(commands=['giverub', 'givedonate', 'givebal'])
def giverubles(message):
	try:
		cid = message.chat.id
		uid = message.from_user.id
		sql.execute(f"SELECT * FROM users WHERE id = {uid}")
		getaccess = sql.fetchone()[3]
		accessquery = 777
		if getaccess < accessquery:
			client.send_message(cid, f"⚠️ | У вас нет доступа!")
		else:
			for info in sql.execute(f"SELECT * FROM users WHERE id = {uid}"):
				msg = client.send_message(cid, 'Введите ID пользователя:\nПример: 596060542', parse_mode="Markdown")
				client.register_next_step_handler(msg, rubles_user_id_answer)
	except:
		client.send_message(cid, f'🚫 | Ошибка при выполнении команды')

def rubles_user_id_answer(message):
	try:
		cid = message.chat.id
		uid = message.from_user.id
		if message.text == message.text:
			global usridrubles
			usridrubles = message.text
			rmk = types.ReplyKeyboardMarkup(resize_keyboard=True)
			rmk.add(types.KeyboardButton('10'), types.KeyboardButton('100'), types.KeyboardButton('1000'), types.KeyboardButton('Другая сумма'))
			msg = client.send_message(cid, 'Выберите сумму для выдачи:', reply_markup=rmk, parse_mode="Markdown")
			client.register_next_step_handler(msg, rubles_user_rubles_answer)
	except:
		client.send_message(cid, f'🚫 | Ошибка при выполнении команды')

def rubles_user_rubles_answer(message):
	try:
		cid = message.chat.id
		uid = message.from_user.id
		global rublesgavedvalue
		removekeyboard = types.ReplyKeyboardRemove()
		rmk = types.InlineKeyboardMarkup()
		access_yes = types.InlineKeyboardButton(text='✅',callback_data='giverublesyes')
		access_no = types.InlineKeyboardButton(text='❌',callback_data='giverublesno')
		rmk.add(access_yes, access_no)
		for info in sql.execute(f"SELECT * FROM users WHERE id = {usridrubles}"):
			if message.text == '10':
				rublesgavedvalue = 10
				client.send_message(cid, f'Данные для выдачи:\nID пользователя: {usridrubles} ({info[1]})\nСумма: {rublesgavedvalue}\n\nВерно?',reply_markup=rmk)
			elif message.text == '100':
				rublesgavedvalue = 100
				client.send_message(cid, f'Данные для выдачи:\nID пользователя: {usridrubles} ({info[1]})\nСумма: {rublesgavedvalue}\n\nВерно?',reply_markup=rmk)
			elif message.text == '1000':
				rublesgavedvalue = 1000
				client.send_message(cid, f'Данные для выдачи:\nID пользователя: {usridrubles} ({info[1]})\nСумма: {rublesgavedvalue}\n\nВерно?',reply_markup=rmk)
			elif message.text == 'Другая сумма':
				msg = client.send_message(cid, f"*Введите сумму для выдачи:*",parse_mode='Markdown',reply_markup=removekeyboard)
				client.register_next_step_handler(msg, rubles_user_rubles_answer_other)
	except:
		client.send_message(cid, f'🚫 | Ошибка при выполнении команды')

def rubles_user_rubles_answer_other(message):
	try:
		cid = message.chat.id
		uid = message.from_user.id
		global rublesgavedvalue
		rmk = types.InlineKeyboardMarkup()
		access_yes = types.InlineKeyboardButton(text='✅',callback_data='giverublesyes')
		access_no = types.InlineKeyboardButton(text='❌',callback_data='giverublesno')
		rmk.add(access_yes, access_no)
		for info in sql.execute(f"SELECT * FROM users WHERE id = {usridrubles}"):
			if message.text == message.text:
				rublesgavedvalue = int(message.text)
				client.send_message(cid, f'Данные для выдачи:\nID пользователя: {usridrubles} ({info[1]})\nСумма: {rublesgavedvalue}\n\nВерно?',reply_markup=rmk)
	except:
		client.send_message(cid, f'🚫 | Ошибка при выполнении команды')

@client.callback_query_handler(func=lambda call: call.data == 'giverublesyes' or call.data == 'giverublesno')
def rubles_gave_rubles_user(call):
	try:
		removekeyboard = types.ReplyKeyboardRemove()
		for info in sql.execute(f"SELECT * FROM users WHERE id = {usridrubles}"):
			rubless = int(info[2] + rublesgavedvalue)
			if call.data == 'giverublesyes':
				for info in sql.execute(f"SELECT * FROM users WHERE id = {usridrubles}"):
					sql.execute(f"UPDATE users SET cash = {rubless} WHERE id = {usridrubles}")
					db.commit()
					client.delete_message(call.message.chat.id, call.message.message_id-0)
					client.send_message(call.message.chat.id, f'✅ | Пользователю {info[1]} выдано {rublesgavedvalue} рублей', reply_markup=removekeyboard)
			elif call.data == 'giverublesno':
				for info in sql.execute(f"SELECT * FROM users WHERE id = {usridrubles}"):
					client.delete_message(call.message.chat.id, call.message.message_id-0)
					client.send_message(call.message.chat.id, f'🚫 | Вы отменили выдачу рублей пользователю {info[1]}', reply_markup=removekeyboard)
			client.answer_callback_query(callback_query_id=call.id)
	except:
		client.send_message(call.message.chat.id, f'🚫 | Ошибка при выполнении команды')

@client.message_handler(commands=['teh'])
def teh(message):
	try:
		cid = message.chat.id
		uid = message.from_user.id
		msg = client.send_message(cid, f"*📨 | Введите текст который хотите отправить тех.поддержке*",parse_mode='Markdown')
		client.register_next_step_handler(msg, teh_next)
	except:
		client.send_message(cid, f'🚫 | Ошибка при выполнении команды')

def teh_next(message):
	try:
		cid = message.chat.id
		uid = message.from_user.id
		if message.text == message.text:
			global tehtextbyuser
			global tehnamebyuser
			global tehidbyuser
			tehidbyuser = int(message.from_user.id)
			tehnamebyuser = str(message.from_user.first_name)
			tehtextbyuser = str(message.text)
			rmk = types.InlineKeyboardMarkup()
			item_yes = types.InlineKeyboardButton(text='✉️',callback_data='tehsend')
			item_no = types.InlineKeyboardButton(text='❌',callback_data='tehno')
			rmk.add(item_yes, item_no)
			msg = client.send_message(cid, f"✉️ | Данные об отправке:\n\nТекст для отправки: {tehtextbyuser}\n\nВы действительно хотите отправить это тех.поддержке?",parse_mode='Markdown',reply_markup=rmk)
	except:
		client.send_message(cid, f'🚫 | Ошибка при выполнении команды')

@client.callback_query_handler(func=lambda call: call.data == 'tehsend' or call.data == 'tehno')
def teh_callback(call):
	try:
		if call.data == 'tehsend':
			for info in sql.execute(f"SELECT * FROM users WHERE id = {call.from_user.id}"):
				client.delete_message(call.message.chat.id, call.message.message_id-0)
				client.send_message(call.message.chat.id, f"✉️ | Ваше сообщение отправлено тех.поддержке, ожидайте ответа.")
				client.send_message(596060542, f"✉️ | Пользователь {tehnamebyuser} отправил сообщение в тех.поддержку\n\nID пользователя: {tehidbyuser}\nТекст: {tehtextbyuser}\n\nЧтобы ответить пользователю напишите /ot")
		elif call.data == 'tehno':
			client.delete_message(call.message.chat.id, call.message.message_id-0)
			client.send_message(call.message.chat.id, f"🚫 | Вы отменили отправку сообщения тех.поддержке")
		client.answer_callback_query(callback_query_id=call.id)
	except:
		client.send_message(call.message.chat.id, f'🚫 | Ошибка при выполнении команды')

@client.message_handler(commands=['ot'])
def sendmsgtouser(message):
	try:
		cid = message.chat.id

		msg = client.send_message(cid, f"👤 | Введите ID пользователя которому хотите отправить сообщение:")
		client.register_next_step_handler(msg, sendmsgtouser_next)
	except:
		client.send_message(cid, f'🚫 | Ошибка при выполнении команды')

def sendmsgtouser_next(message):
	try:
		cid = message.chat.id

		if message.text == message.text:
			global getsendmsgtouserid
			getsendmsgtouserid = int(message.text)
			msg = client.send_message(cid, f"📨 | Введите текст который хотите отправить пользователю:")
			client.register_next_step_handler(msg, sendmsgtouser_next_text)
	except:
		client.send_message(cid, f'🚫 | Ошибка при выполнении команды')

def sendmsgtouser_next_text(message):
	try:
		cid = message.chat.id

		if message.text == message.text:
			global getsendmsgtousertext
			getsendmsgtousertext = str(message.text)
			rmk = types.InlineKeyboardMarkup()
			item_yes = types.InlineKeyboardButton(text='✅',callback_data='sendmsgtouseryes')
			item_no = types.InlineKeyboardButton(text='❌',callback_data='sendmsgtouserno')
			rmk.add(item_yes, item_no)
			msg = client.send_message(cid, f"🔰 | Данные об отправке сообщения:\n\nID пользователя: {getsendmsgtouserid}\nТекст для отправки: {getsendmsgtousertext}\n\nОтправить сообщение?",reply_markup=rmk)
	except:
		client.send_message(cid, f'🚫 | Ошибка при выполнении команды')

@client.callback_query_handler(func=lambda call: call.data == 'sendmsgtouseryes' or call.data == 'sendmsgtouserno')
def sendmsgtouser_callback(call):
	try:
		if call.data == 'sendmsgtouseryes':
			client.delete_message(call.message.chat.id, call.message.message_id-0)
			client.send_message(call.message.chat.id, f"✉️ | Сообщение отправлено!")
			client.send_message(getsendmsgtouserid, f"✉️ | Администратор прислал вам сообщение:\n\n{getsendmsgtousertext}")
		elif call.data == 'sendmsgtouserno':
			client.delete_message(call.message.chat.id, call.message.message_id-0)
			client.send_message(call.message.chat.id, f"🚫 | Вы отменили отправку сообщения пользователю")
		client.answer_callback_query(callback_query_id=call.id)
	except:
		client.send_message(call.message.chat.id, f'🚫 | Ошибка при выполнении команды')

@client.message_handler(commands=['getid'])
def getiduser(message):
	try:
		cid = message.chat.id
		uid = message.from_user.id
		sql.execute(f"SELECT * FROM users WHERE id = {uid}")
		getaccess = sql.fetchone()[3]
		accessquery = 1
		if getaccess < accessquery:
			client.send_message(cid, f"⚠️ | У вас нет доступа!")
		else:
			msg = client.send_message(cid, 'Введите никнейм пользователя:')
			client.register_next_step_handler(msg, next_getiduser_name)
	except:
		client.send_message(cid, f'🚫 | Ошибка при выполнении команды')

def next_getiduser_name(message):
	try:
		cid = message.chat.id
		uid = message.from_user.id
		if message.text == message.text:
			getusername = message.text
			sql.execute(f"SELECT * FROM users WHERE nick = '{getusername}'")
			result = sql.fetchone()[0]
			client.send_message(cid, f'👤 | ID пользователя: {result}')
	except:
		client.send_message(cid, f'🚫 | Ошибка при выполнении команды')



client.polling(none_stop=True,interval=0)
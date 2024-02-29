import asyncio
import time
import traceback

from pyrogram import Client, filters, idle, types
from loguru import logger
from pyrogram.errors import UserDeactivated
from sqlalchemy import select
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import selectinload

from db.models import Message, User
from db.database import AsyncSessionLocal
from utils.handler import handler
from data.accounts import accounts
from data.texts_plus_time_of_await import messages_from_states

logger.add("logs/debug.log", format="{time} {level} {message}", level="INFO")


@handler
async def check_auth(client, message):
    """
    Проверка есть ли пользователь в базе
    """
    # Проверяем, зарегистрирован ли пользователь
    async with AsyncSessionLocal() as session:
        user = None
        try:
            user = await session.execute(select(User).filter_by(chat_id=str(message.chat.id)))
            user = user.scalars().first()
            print(user)
        except DBAPIError as e:
            logger.info("Пользователь не зарегистрирован: {}", message.from_user.id)
        # Создаем нового пользователя и сохраняем его в базе данных
        else:
            if not user:
                current_time = int(time.time())
                chat_id = str(message.chat.id)
                new_user = User(chat_id=chat_id, created_at=current_time, point_of_reference='msg_1')
                try:
                    session.add(new_user)
                    await session.commit()
                    logger.info("Новый пользователь зарегистрирован: {}", message.from_user.id)
                except Exception as e:
                    logger.error("Ошибка при регистрации пользователя: {}. {}", message.from_user.id, e)
                    return await message.reply("Произошла ошибка при регистрации.")


@handler
async def create_message(client: Client, update: Message, user_db: User, message_text: str, session: AsyncSessionLocal):
    """
    Занесение сообщения в базу данных
    """
    # Шаг 1: Найти пользователя по chat_id
    current_time = int(time.time())
    user = await session.execute(
        select(User).options(
            selectinload(User.messages)
        ).filter_by(chat_id=str(user_db.chat_id)))
    user_db = user.scalars().first()
    if user_db:
        if user_db.messages:
            last_msg = user_db.messages[-1]
            if last_msg and last_msg.text == message_text:
                await session.commit()
                logger.info('text simmular. dont changed')
                return
        text = message_text
        # Шаг 2: Создать новое сообщение с user_id найденного пользователя
        new_message = Message(text=text, user_id=user_db.id, time=current_time)

        # Шаг 3: Добавить сообщение в сессию и сохранить изменения
        session.add(new_message)
        await session.commit()
        logger.info(f"Сообщение для пользователя {user_db.chat_id} успешно создано.")
        return new_message
    else:
        logger.warning(f"Пользователь с chat_id={user_db.chat_id} не найден.")
        return None


@handler
async def prepare_schedule(client: Client, message: Message,
                           user_db: User, session: AsyncSessionLocal, point_ref: str, message_text: str):
    """
    Подготавливает расписание для отправки сообщений и обрабатывает специальные случаи текста сообщений.

    Args:
        client (Client): Экземпляр клиента Pyrogram.
        message (Message): Объект сообщения Pyrogram.
        user_db (User): Экземпляр пользователя из базы данных.
        session (AsyncSessionLocal): Асинхронная сессия базы данных.
        point_ref (str): Текущий ключ статуса ротации для пользователя.
        message_text (str): Текст полученного сообщения.
    """
    # Если у пользователя уже есть запланированная задача, отменяем её
    current_time = int(time.time())
    if not user_db.status == 'finished' or 'dead':
        user_db.schedule = current_time + messages_from_states.get(point_ref).get('time_await')
    else:
        return
    if "прекрасно" in message_text.lower() or "ожидать" in message_text.lower():
        user_db.schedule = current_time - 1
        # Отмена задания и выход из функции
        user_db.status = 'finished'
        user_db.status_updated_at = current_time
    await session.commit()
    await create_message(client, message, user_db, message_text, session)


async def check_and_send_scheduled_messages(app: Client):
    """
    Периодически проверяет пользователей на готовность к получению сообщений и отправляет их.

    Args:
        app (Client): Экземпляр клиента Pyrogram.
    """
    while True:
        async with AsyncSessionLocal() as session:
            current_time = int(time.time())
            # Найти пользователей, для которых наступило время отправки сообщения
            stmt = select(User).where(User.schedule == current_time, User.status == 'alive')
            result = await session.execute(stmt)
            ready_users = result.scalars().all()
            for user in ready_users:
                # Получить сообщение на основе point_of_reference пользователя
                point_ref = user.point_of_reference
                if point_ref:
                    text = messages_from_states.get(point_ref).get('text')
                    # Отправляем сообщение пользователю
                    try:
                        await app.send_message(chat_id=user.chat_id, text=text)
                    except UserDeactivated as e:
                        # смена статуса при ошибке
                        logger.error(f'exception trying send message {e, traceback.format_exc()}')
                        user.status = 'dead'
                        user.status_updated_at = current_time
                        continue
                    if not point_ref == 'msg_3':
                        # планирование следующего сообщения
                        parts = point_ref.split('_')
                        next_number = str(int(parts[-1]) + 1)
                        user.point_of_reference = '_'.join(parts[:-1] + [next_number])
                        user.schedule = current_time + messages_from_states.get(point_ref).get('time_await')
                    else:
                        user.status = 'finished'
                        user.status_updated_at = current_time
                    await session.commit()

            # Пауза перед следующей проверкой
            await asyncio.sleep(1)


async def run_client(api_id, api_hash, phone_number):
    """
    Запускает клиента Pyrogram для обработки входящих сообщений и планирования отправки сообщений.

    Эта функция создает экземпляр клиента Pyrogram, обрабатывает входящие текстовые сообщения,
    обновляет статусы и планирует отправку сообщений для зарегистрированных пользователей.
    Также она инициирует фоновую задачу для регулярной проверки и отправки запланированных сообщений.
    """

    app = Client(f'{phone_number}', api_id=api_id, api_hash=api_hash, phone_number=phone_number)

    @app.on_message(filters.text)
    @handler
    async def taker(client, message):
        await check_auth(client, message)
        message_text = message.text
        async with AsyncSessionLocal() as session:
            # Проверка на наличие специальных слов
            try:
                user = await session.execute(
                    select(User).filter_by(chat_id=str(message.chat.id)))
                user_db = user.scalars().first()
                if message_text.lower() == 'заново':
                    user_db.status = 'alive'
                    current_time = int(time.time())
                    user_db.status_updated_at = current_time
                    user_db.point_of_reference = 'msg_1'
                    await session.commit()
                point_ref = user_db.point_of_reference
            except Exception as e:
                logger.error(f'ошибка обработки юзера \n{e}\n{traceback.format_exc()}')

            try:
                await prepare_schedule(client, message, user_db, session, point_ref, message_text)
            except Exception as e:
                logger.error(f'ошибка в run_client \n{e}\n{traceback.format_exc()}')

    scheduler_task = asyncio.create_task(check_and_send_scheduled_messages(app))
    print(app.name)
    await app.start()
    await asyncio.gather(
        idle(),  # Ждем, пока клиент будет принимать сообщения
        scheduler_task  # одновременно с этим выполняем задачу планировщика
    )
    await app.stop()


async def gain():
    """
    Запускает асинхронные задачи для каждого клиента, определенного в конфигурации.

    Инициирует запуск клиентов Pyrogram для всех аккаунтов, указанных в глобальном списке `accounts`.
    Каждый клиент работает асинхронно и независимо от остальных.
    """
    tasks = []
    for account in accounts:
        task = asyncio.create_task(run_client(account["api_id"], account["api_hash"],
                                              account["phone_number"]))
        tasks.append(task)
    await asyncio.gather(*tasks)

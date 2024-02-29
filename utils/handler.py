import functools
import inspect
from pyrogram import Client
from pyrogram.types import Message
from pyrogram.enums import ChatType
from loguru import logger

package_constraints = {
    'private': [ChatType.PRIVATE],
    'chat': [ChatType.GROUP, ChatType.SUPERGROUP],
    'channel': [ChatType.CHANNEL],
}


def handler(func):
    @functools.wraps(func)
    async def wrapper(client: Client, update: Message, *args, **kwargs):
        logger.opt(colors=True).info(f'Handler <red>{func.__name__}</red> called')
        module = inspect.getmodule(func)

        # В Pyrogram информация о чате доступна через объект update
        chat_type = update.chat.type

        for package, constraints in package_constraints.items():
            if f'.{package}.' in module.__name__ and chat_type not in constraints:
                logger.warning('Invalid chat type')
                return
        return await func(client, update, *args, **kwargs)

    return wrapper

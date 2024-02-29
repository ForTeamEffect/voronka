import asyncio
import time
import traceback

from client import gain
from db.database import create_tables
from client import logger


async def main() -> None:
    await create_tables()
    await gain()


if __name__ == "__main__":
    while True:
        try:
            asyncio.run(main())
        except Exception as e:
            print("Restarting the script in 10 seconds...")
            time.sleep(10)  # Подождите 10 секунд перед перезапуском
            logger.warning(f"{e, traceback.format_exc()},")

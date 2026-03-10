import sys
import os
from pathlib import Path

# Добавляем корневую папку в путь поиска модулей
root_path = str(Path(__file__).parent)
if root_path not in sys.path:
    sys.path.append(root_path)

# Импортируем и запускаем бота
from BotTG.bot.main import main

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
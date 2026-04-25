import sys
from pathlib import Path

root_path = str(Path(__file__).parent / "BotTG")
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from bot.main import main

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

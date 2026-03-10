import json
import aiofiles
from typing import Optional, List, Dict, Any
from pathlib import Path


class BaseRepo:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
    
    async def _read_json(self, filename: str) -> Dict[str, Any]:
        filepath = self.data_dir / filename
        if not filepath.exists():
            return {}
        
        async with aiofiles.open(filepath, 'r', encoding='utf-8') as f:
            content = await f.read()
            return json.loads(content) if content else {}
    
    async def _write_json(self, filename: str, data: Dict[str, Any]) -> None:
        filepath = self.data_dir / filename
        async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(data, ensure_ascii=False, indent=2, default=str))
"""配置管理"""

import json
from pathlib import Path
from typing import Any

# 配置文件路径
CONFIG_DIR = Path.home() / '.yjsc'
CONFIG_FILE = CONFIG_DIR / 'config.json'


class Config:
    """配置管理器"""

    def __init__(self):
        self._config: dict[str, Any] = {}
        self._load()

    def _load(self):
        """加载配置"""
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
        else:
            self._config = {}
            self._save()

    def _save(self):
        """保存配置"""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self._config, f, indent=2, ensure_ascii=False)

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        return self._config.get(key, default)

    def set(self, key: str, value: Any):
        """设置配置项"""
        self._config[key] = value
        self._save()

    def delete(self, key: str):
        """删除配置项"""
        if key in self._config:
            del self._config[key]
            self._save()


# 全局单例
config = Config()
"""状态持久化"""

import base64
import hashlib
import json
from pathlib import Path
from typing import Any, Optional

# 状态文件路径
STATE_DIR = Path.home() / '.yjsc'
STATE_FILE = STATE_DIR / 'state.json'


class StateManager:
    """状态管理器"""

    def __init__(self):
        self._state: dict[str, Any] = {}
        self._load()

    def _load(self):
        """加载状态"""
        if STATE_FILE.exists():
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                self._state = json.load(f)
        else:
            self._state = {}
            self._save()

    def _save(self):
        """保存状态"""
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(self._state, f, indent=2, ensure_ascii=False)

    def get(self, key: str, default: Any = None) -> Any:
        """获取状态项"""
        return self._state.get(key, default)

    def set(self, key: str, value: Any):
        """设置状态项"""
        self._state[key] = value
        self._save()

    def delete(self, key: str):
        """删除状态项"""
        if key in self._state:
            del self._state[key]
            self._save()

    def clear(self):
        """清空所有状态"""
        self._state = {}
        self._save()


class CredentialsManager:
    """凭据管理器 - 安全存储账号密码"""

    def __init__(self):
        self._key = self._get_machine_key()

    def _get_machine_key(self) -> bytes:
        """获取机器特定的密钥（用于加密）"""
        # 使用机器特定的信息生成密钥
        import platform
        machine_str = f"{platform.node()}-{platform.machine()}"
        return hashlib.sha256(machine_str.encode()).digest()[:16]

    def _encrypt(self, plaintext: str) -> str:
        """简单的加密（使用XOR + Base64）"""
        key = self._key
        # 将密钥扩展到与明文相同长度
        key_bytes = (key * ((len(plaintext) // len(key)) + 1))[:len(plaintext)]
        # XOR加密
        encrypted = bytes(a ^ b for a, b in zip(plaintext.encode(), key_bytes))
        # Base64编码
        return base64.b64encode(encrypted).decode('utf-8')

    def _decrypt(self, ciphertext: str) -> str:
        """解密"""
        try:
            key = self._key
            # Base64解码
            encrypted = base64.b64decode(ciphertext.encode('utf-8'))
            # 将密钥扩展到与密文相同长度
            key_bytes = (key * ((len(encrypted) // len(key)) + 1))[:len(encrypted)]
            # XOR解密
            decrypted = bytes(a ^ b for a, b in zip(encrypted, key_bytes))
            return decrypted.decode('utf-8')
        except Exception:
            return ""

    def save_credentials(self, user_id: str, password: str):
        """保存凭据"""
        credentials = {
            'user_id': user_id,
            'password': self._encrypt(password),
        }
        state_manager.set('credentials', credentials)

    def load_credentials(self) -> Optional[tuple[str, str]]:
        """加载凭据

        Returns:
            (user_id, password) 或 None
        """
        credentials = state_manager.get('credentials')
        if credentials and 'user_id' in credentials and 'password' in credentials:
            user_id = credentials['user_id']
            password = self._decrypt(credentials['password'])
            if password:  # 解密成功
                return (user_id, password)
        return None

    def clear_credentials(self):
        """清除凭据"""
        state_manager.delete('credentials')

    def has_credentials(self) -> bool:
        """检查是否有保存的凭据"""
        credentials = state_manager.get('credentials')
        return bool(credentials and 'user_id' in credentials)


# 全局单例
state_manager = StateManager()
credentials_manager = CredentialsManager()
"""加密解密模块"""

import base64
from typing import Union

from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import pad, unpad

from .constants import (
    DES_KEY_1,
    DES_KEY_3,
    DES_KEY_5,
    DECRYPT_KEY,
    EMPTY_VALUE,
)


class CryptoManager:
    """加密管理器"""

    def __init__(self):
        self._aes_key: bytes | None = None

    @property
    def aes_key(self) -> bytes:
        """获取 AES 密钥（懒加载）"""
        if self._aes_key is None:
            self._aes_key = self._derive_aes_key()
        return self._aes_key

    def _derive_aes_key(self) -> bytes:
        """
        派生 AES 密钥

        从 JS 代码逆向：
        var aesKey = Decrypt2(desKey1, decryptKey) +
                     Decrypt2(desKey3, decryptKey) +
                     Decrypt2(desKey5, decryptKey);
        """
        # 反转 desKey5
        des_key_5_reversed = DES_KEY_5[::-1]

        # 使用 decrypt_key 解密这三个密钥
        key1 = self.aes_decrypt_base64(DES_KEY_1, DECRYPT_KEY.encode())
        key3 = self.aes_decrypt_base64(DES_KEY_3, DECRYPT_KEY.encode())
        key5 = self.aes_decrypt_base64(des_key_5_reversed, DECRYPT_KEY.encode())

        # 拼接成最终密钥（24 字节）
        return (key1 + key3 + key5).encode('utf-8')

    @staticmethod
    def aes_encrypt(plaintext: str, key: bytes) -> str:
        """
        AES 加密（ECB 模式）

        Args:
            plaintext: 明文
            key: 密钥

        Returns:
            Base64 编码的密文
        """
        cipher = AES.new(key, AES.MODE_ECB)
        padded = pad(plaintext.encode('utf-8'), AES.block_size)
        encrypted = cipher.encrypt(padded)
        return base64.b64encode(encrypted).decode('utf-8')

    @staticmethod
    def aes_decrypt_base64(ciphertext: str, key: bytes) -> str:
        """
        AES 解密（ECB 模式）

        Args:
            ciphertext: Base64 编码的密文
            key: 密钥

        Returns:
            解密后的明文
        """
        # 特殊值处理
        if ciphertext == EMPTY_VALUE:
            return '-'

        try:
            encrypted = base64.b64decode(ciphertext)
            cipher = AES.new(key, AES.MODE_ECB)
            decrypted = unpad(cipher.decrypt(encrypted), AES.block_size)
            return decrypted.decode('utf-8')
        except Exception:
            # 解密失败返回原字符串
            return ciphertext

    def aes_decrypt_response(self, ciphertext: str) -> str:
        """
        解密服务器响应（使用派生的 AES 密钥）

        Args:
            ciphertext: Base64 编码的密文

        Returns:
            解密后的明文
        """
        return self.aes_decrypt_base64(ciphertext, self.aes_key)

    def rsa_encrypt_password(self, password: str, pubkey: str) -> str:
        """
        使用 RSA 公钥加密密码
        """
        # 1. 解析 PEM 格式公钥 (JSEncrypt 通常使用 PEM 格式)
        key = RSA.import_key(pubkey)

        # 2. 创建 PKCS1_v1_5 密码对象 (对应 JSEncrypt 的默认行为)
        cipher = PKCS1_v1_5.new(key)

        # 3. 加密前需将字符串编码为字节流
        encrypted = cipher.encrypt(password.encode('utf-8'))

        # 4. 返回 Base64 编码的字符串
        return base64.b64encode(encrypted).decode('utf-8')


# 全局单例
crypto_manager = CryptoManager()
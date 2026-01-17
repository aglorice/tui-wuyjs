"""常量定义"""

# 基础 URL
BASE_URL = "https://yjsc.wyu.edu.cn"


# AES 密钥相关（硬编码在 JS 中）
DES_KEY_1 = 'ND7TLBY9Cx/SdS0R/7dqmg=='
DES_KEY_3 = 'ZXF3+Q3opQHlh6UkTTFRVA=='
DES_KEY_5 = '==QrlklM2cjROKp18sqnxLd2'  # 需要反转

# 解密密钥（需要反转）
DECRYPT_KEY_RAW = 'sopthsk!#032IJDS'
DECRYPT_KEY = DECRYPT_KEY_RAW[::-1]  # 'SDJI230#!kshthpos'

# 特殊值
EMPTY_VALUE = '==gwJPTxzG0iY2qTiSUo7wB6'[::-1]  # 反转后

# 超时设置
TIMEOUT = 30.0

# 重试次数
MAX_RETRIES = 3
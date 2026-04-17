# 配置文件 数据库地址、密钥、session密钥等

# config.py
from typing import Dict

# Tortoise-ORM 数据库配置
TORTOISE_ORM: Dict = {
    "connections": {
        "default": "mysql://root:123456@localhost:3306/friendship_db",
    },
    "apps": {
        "models": {
            "models": ["app.models", "aerich.models"],  # 修正为你的模型路径
            "default_connection": "default"
        }
    },
    "use_tz": False,
    "timezone": "Asia/Shanghai",
    "db_pool": {
        "minsize": 1,
        "maxsize": 10,
        "idle_timeout": 300
    }
}

# 会话加密密钥（生产环境请替换为随机长字符串，不要硬编码）
SECRET_KEY = "cyVAD3pKrudg83EkiUaF_-VYAYVDWu_wIk9PH1_lq_0"
# 会话过期时间（秒）
SESSION_MAX_AGE = 3600
# 模板目录
TEMPLATES_DIR = "templates"
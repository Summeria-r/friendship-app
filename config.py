# 配置文件 数据库地址、密钥、session密钥等

# config.py
import os
from typing import Dict


# Tortoise-ORM 数据库配置
import os
from typing import Dict

# 把数据库配置改成函数，启动时再读取
def get_tortoise_config() -> Dict:
    database_url = "mysql://root:KMTwaHuaXbUKPeZUPvxCGBGxYwDRWuys@shortline.proxy.rlwy.net:33643/railway?charset=utf8mb4"
    return {
        "connections": {
            "default": database_url,
        },
        "apps": {
            "models": {
                "models": ["app.models", "aerich.models"],
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

SECRET_KEY = "cyVAD3pKrudg83EkiUaF--VYAYVDWu_wIk9PH1_lq_0"
SESSION_MAX_AGE = 3600
TEMPLATES_DIR = "templates"
# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """飞书应用配置"""

    # 飞书应用凭证
    FEISHU_APP_ID: str = os.getenv("FEISHU_APP_ID", "")
    FEISHU_APP_SECRET: str = os.getenv("FEISHU_APP_SECRET", "")
    FEISHU_APP_TOKEN: str = os.getenv("FEISHU_APP_TOKEN", "")

    # 飞书多维表 ID（database_id，即多维表的 app_token）
    FEISHU_DATABASE_ID: str = os.getenv("FEISHU_DATABASE_ID", "")

    # 飞书多维表中的表格 ID（table_id）
    FEISHU_TABLE_ID_PODCAST: str = os.getenv("FEISHU_TABLE_ID_PODCAST", "")
    FEISHU_TABLE_ID_MAIN_POINTS: str = os.getenv("FEISHU_TABLE_ID_MAIN_POINTS", "")
    FEISHU_TABLE_ID_CONCEPTS: str = os.getenv("FEISHU_TABLE_ID_CONCEPTS", "")
    FEISHU_TABLE_ID_RESOURCES: str = os.getenv("FEISHU_TABLE_ID_RESOURCES", "")

    # 飞书 API 地址
    FEISHU_API_BASE: str = "https://open.feishu.cn/open-apis"

    @classmethod
    def validate(cls) -> list[str]:
        """验证配置完整性，返回缺失的配置项列表"""
        missing = []
        required_fields = [
            "FEISHU_APP_ID",
            "FEISHU_APP_SECRET",
            "FEISHU_DATABASE_ID",
            "FEISHU_TABLE_ID_PODCAST",
            "FEISHU_TABLE_ID_MAIN_POINTS",
            "FEISHU_TABLE_ID_CONCEPTS",
            "FEISHU_TABLE_ID_RESOURCES",
        ]
        for field in required_fields:
            if not getattr(cls, field):
                missing.append(field)
        return missing


config = Config()

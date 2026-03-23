# app/feishu.py
import time
import json
import logging
from typing import Optional
import httpx
from app.config import config

logger = logging.getLogger(__name__)


class FeishuClient:
    """飞书 API 客户端"""

    def __init__(self):
        self._tenant_access_token: Optional[str] = None
        self._token_expires_at: float = 0

    def _get_headers(self) -> dict:
        """获取请求头"""
        return {
            "Authorization": f"Bearer {self.tenant_access_token}",
            "Content-Type": "application/json",
        }

    @property
    def tenant_access_token(self) -> str:
        """获取 tenant_access_token（自动刷新）"""
        now = time.time()
        if not self._tenant_access_token or now >= self._token_expires_at:
            self._refresh_token()
        return self._tenant_access_token

    def _refresh_token(self):
        """刷新 tenant_access_token"""
        url = f"{config.FEISHU_API_BASE}/auth/v3/tenant_access_token/internal"
        payload = {
            "app_id": config.FEISHU_APP_ID,
            "app_secret": config.FEISHU_APP_SECRET,
        }

        logger.info("========== 飞书 API 调用 ==========")
        logger.info(f"API Endpoint: /auth/v3/tenant_access_token/internal")
        logger.info(f"请求方法: POST")
        logger.info(f"请求 URL: {url}")
        logger.info(f"请求体: app_id={config.FEISHU_APP_ID}, app_secret=***")
        logger.info("====================================")

        with httpx.Client() as client:
            response = client.post(url, json=payload)
            status_code = response.status_code
            response_body = response.text

            logger.info("========== 飞书 API 响应 ==========")
            logger.info(f"HTTP 状态码: {status_code}")
            logger.info(f"响应体: {response_body}")
            logger.info("====================================")

            data = response.json()

            if data.get("code") != 0:
                raise Exception(f"获取 token 失败: code={data.get('code')}, msg={data.get('msg', '未知错误')}")

            self._tenant_access_token = data["tenant_access_token"]
            # 提前 5 分钟过期
            self._token_expires_at = time.time() + data["expire"] - 300
            logger.info(f"Token 刷新成功，过期时间: {self._token_expires_at}")

    def add_record(self, database_id: str, table_id: str, fields: dict) -> str:
        """添加记录到多维表指定表格

        Args:
            database_id: 多维表的 app_token (database_id)
            table_id: 表格 ID
            fields: 要写入的字段
        """
        # 飞书 API: POST /bitable/v1/apps/{app_token}/tables/{table_id}/records
        url = f"{config.FEISHU_API_BASE}/bitable/v1/apps/{database_id}/tables/{table_id}/records"
        method = "POST"
        payload = {"fields": fields}

        logger.info("========== 飞书 API 调用 ==========")
        logger.info(f"API Endpoint: /bitable/v1/apps/{{database_id}}/tables/{{table_id}}/records")
        logger.info(f"请求方法: {method}")
        logger.info(f"请求 URL: {url}")
        logger.info(f"database_id: {database_id}")
        logger.info(f"table_id: {table_id}")
        logger.info(f"请求体: {json.dumps(payload, ensure_ascii=False)}")
        logger.info("====================================")

        with httpx.Client() as client:
            response = client.post(
                url,
                json=payload,
                headers=self._get_headers(),
            )
            status_code = response.status_code
            response_body = response.text

            logger.info("========== 飞书 API 响应 ==========")
            logger.info(f"HTTP 状态码: {status_code}")
            logger.info(f"响应体: {response_body}")
            logger.info("====================================")

            data = response.json()

            if data.get("code") != 0:
                raise Exception(f"添加记录失败: code={data.get('code')}, msg={data.get('msg', '未知错误')}")

            record_id = data["data"]["record"]["record_id"]
            logger.info(f"记录添加成功，record_id: {record_id}")
            return record_id

    def get_record(self, database_id: str, table_id: str, record_id: str) -> dict:
        """获取单条记录"""
        url = f"{config.FEISHU_API_BASE}/bitable/v1/apps/{database_id}/tables/{table_id}/records/{record_id}"
        method = "GET"

        logger.info("========== 飞书 API 调用 ==========")
        logger.info(f"API Endpoint: /bitable/v1/apps/{{database_id}}/tables/{{table_id}}/records/{{record_id}}")
        logger.info(f"请求方法: {method}")
        logger.info(f"请求 URL: {url}")
        logger.info("====================================")

        with httpx.Client() as client:
            response = client.get(url, headers=self._get_headers())
            status_code = response.status_code
            response_body = response.text

            logger.info("========== 飞书 API 响应 ==========")
            logger.info(f"HTTP 状态码: {status_code}")
            logger.info(f"响应体: {response_body}")
            logger.info("====================================")

            data = response.json()

            if data.get("code") != 0:
                raise Exception(f"获取记录失败: code={data.get('code')}, msg={data.get('msg', '未知错误')}")

            return data["data"]["record"]

    def list_records(
        self,
        database_id: str,
        table_id: str,
        filter_str: Optional[str] = None,
        page_size: int = 100,
    ) -> list[dict]:
        """获取表中所有记录"""
        url = f"{config.FEISHU_API_BASE}/bitable/v1/apps/{database_id}/tables/{table_id}/records"
        method = "GET"
        params = {"page_size": page_size}
        if filter_str:
            params["filter"] = filter_str

        logger.info("========== 飞书 API 调用 ==========")
        logger.info(f"API Endpoint: /bitable/v1/apps/{{database_id}}/tables/{{table_id}}/records")
        logger.info(f"请求方法: {method}")
        logger.info(f"请求 URL: {url}")
        logger.info(f"查询参数: {params}")
        logger.info("====================================")

        records = []

        with httpx.Client() as client:
            while True:
                response = client.get(url, params=params, headers=self._get_headers())
                status_code = response.status_code
                response_body = response.text

                logger.info("========== 飞书 API 响应 ==========")
                logger.info(f"HTTP 状态码: {status_code}")
                logger.info(f"响应体: {response_body}")
                logger.info("====================================")

                data = response.json()

                if data.get("code") != 0:
                    raise Exception(f"获取记录列表失败: code={data.get('code')}, msg={data.get('msg', '未知错误')}")

                records.extend(data["data"].get("items", []))

                # 检查是否还有更多
                if not data["data"].get("has_more"):
                    break

                params["page_token"] = data["data"]["page_token"]

        return records


# 全局客户端实例
feishu_client = FeishuClient()

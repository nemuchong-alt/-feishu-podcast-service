# app/routes/probe.py
import logging
import httpx
from fastapi import APIRouter, HTTPException
from app.config import config

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/metadata")
async def probe_metadata():
    """
    探针1：获取多维表元数据
    API: GET /bitable/v1/apps/{database_id}
    权限: bitable:app:readonly 或 bitable:database:meta:read
    """
    url = f"{config.FEISHU_API_BASE}/bitable/v1/apps/{config.FEISHU_DATABASE_ID}"

    # 获取 token
    token_url = f"{config.FEISHU_API_BASE}/auth/v3/tenant_access_token/internal"
    token_payload = {"app_id": config.FEISHU_APP_ID, "app_secret": config.FEISHU_APP_SECRET}

    logger.info("========== 探针 1: 获取多维表元数据 ==========")
    logger.info(f"请求 URL: {url}")

    with httpx.Client() as client:
        # 先获取 token
        token_response = client.post(token_url, json=token_payload)
        token_data = token_response.json()
        access_token = token_data.get("tenant_access_token", "")

        headers = {"Authorization": f"Bearer {access_token}"}

        # 调用元数据接口
        response = client.get(url, headers=headers)

        result = {
            "probe": "获取多维表元数据",
            "api": "GET /bitable/v1/apps/{database_id}",
            "url": url,
            "database_id": config.FEISHU_DATABASE_ID,
            "http_status": response.status_code,
            "response_body": response.text,
        }

        logger.info(f"HTTP 状态码: {response.status_code}")
        logger.info(f"响应体: {response.text}")
        logger.info("==========================================")

        return result


@router.get("/list_records")
async def probe_list_records():
    """
    探针2：查询播客主表现有记录
    API: GET /bitable/v1/apps/{database_id}/tables/{table_id}/records
    权限: bitable:database:record:read 或 bitable:table:record:read
    """
    url = f"{config.FEISHU_API_BASE}/bitable/v1/apps/{config.FEISHU_DATABASE_ID}/tables/{config.FEISHU_TABLE_ID_PODCAST}/records"

    # 获取 token
    token_url = f"{config.FEISHU_API_BASE}/auth/v3/tenant_access_token/internal"
    token_payload = {"app_id": config.FEISHU_APP_ID, "app_secret": config.FEISHU_APP_SECRET}

    logger.info("========== 探针 2: 查询播客主表记录 ==========")
    logger.info(f"请求 URL: {url}")

    with httpx.Client() as client:
        # 先获取 token
        token_response = client.post(token_url, json=token_payload)
        token_data = token_response.json()
        access_token = token_data.get("tenant_access_token", "")

        headers = {"Authorization": f"Bearer {access_token}"}

        # 调用查询记录接口
        response = client.get(url, headers=headers)

        result = {
            "probe": "查询播客主表记录",
            "api": "GET /bitable/v1/apps/{database_id}/tables/{table_id}/records",
            "url": url,
            "database_id": config.FEISHU_DATABASE_ID,
            "table_id": config.FEISHU_TABLE_ID_PODCAST,
            "http_status": response.status_code,
            "response_body": response.text,
        }

        logger.info(f"HTTP 状态码: {response.status_code}")
        logger.info(f"响应体: {response.text}")
        logger.info("==========================================")

        return result


@router.post("/add_simple_record")
async def probe_add_simple_record():
    """
    探针3：往播客主表新增一条最简单记录
    API: POST /bitable/v1/apps/{database_id}/tables/{table_id}/records
    权限: bitable:database:record:create 或 bitable:table:record:create
    """
    url = f"{config.FEISHU_API_BASE}/bitable/v1/apps/{config.FEISHU_DATABASE_ID}/tables/{config.FEISHU_TABLE_ID_PODCAST}/records"

    # 获取 token
    token_url = f"{config.FEISHU_API_BASE}/auth/v3/tenant_access_token/internal"
    token_payload = {"app_id": config.FEISHU_APP_ID, "app_secret": config.FEISHU_APP_SECRET}

    logger.info("========== 探针 3: 新增简单记录 ==========")
    logger.info(f"请求 URL: {url}")

    with httpx.Client() as client:
        # 先获取 token
        token_response = client.post(token_url, json=token_payload)
        token_data = token_response.json()
        access_token = token_data.get("tenant_access_token", "")

        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

        # 发送请求体：使用播客主表正确的字段名
        payload = {
            "fields": {
                "播客-期数": "探针测试",
                "总结": "这是一条测试记录的总结",
                "推荐复听程度": "推荐"
            }
        }
        logger.info(f"请求体: {payload}")

        # 调用新增记录接口
        response = client.post(url, json=payload, headers=headers)

        result = {
            "probe": "新增简单记录",
            "api": "POST /bitable/v1/apps/{database_id}/tables/{table_id}/records",
            "url": url,
            "database_id": config.FEISHU_DATABASE_ID,
            "table_id": config.FEISHU_TABLE_ID_PODCAST,
            "request_body": payload,
            "http_status": response.status_code,
            "response_body": response.text,
        }

        logger.info(f"HTTP 状态码: {response.status_code}")
        logger.info(f"响应体: {response.text}")
        logger.info("==========================================")

        return result


@router.post("/create_bitable")
async def probe_create_bitable():
    """
    方案B：创建新的多维表（应用身份）
    API: POST /bitable/v1/apps
    应用创建的多维表，应用有权写入
    """
    url = f"{config.FEISHU_API_BASE}/bitable/v1/apps"

    # 获取 token
    token_url = f"{config.FEISHU_API_BASE}/auth/v3/tenant_access_token/internal"
    token_payload = {"app_id": config.FEISHU_APP_ID, "app_secret": config.FEISHU_APP_SECRET}

    logger.info("========== 创建新多维表 ==========")
    logger.info(f"请求 URL: {url}")

    with httpx.Client() as client:
        # 先获取 token
        token_response = client.post(token_url, json=token_payload)
        token_data = token_response.json()
        access_token = token_data.get("tenant_access_token", "")

        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

        # 创建多维表
        payload = {
            "name": "播客整理-测试",
            "folder_token": ""
        }
        logger.info(f"请求体: {payload}")

        response = client.post(url, json=payload, headers=headers)

        result = {
            "probe": "创建新多维表",
            "api": "POST /bitable/v1/apps",
            "url": url,
            "request_body": payload,
            "http_status": response.status_code,
            "response_body": response.text,
        }

        logger.info(f"HTTP 状态码: {response.status_code}")
        logger.info(f"响应体: {response.text}")
        logger.info("==========================================")

        return result


@router.post("/create_table")
async def probe_create_table():
    """
    创建表格
    API: POST /bitable/v1/apps/{database_id}/tables
    """
    url = f"{config.FEISHU_API_BASE}/bitable/v1/apps/{config.FEISHU_DATABASE_ID}/tables"

    # 获取 token
    token_url = f"{config.FEISHU_API_BASE}/auth/v3/tenant_access_token/internal"
    token_payload = {"app_id": config.FEISHU_APP_ID, "app_secret": config.FEISHU_APP_SECRET}

    logger.info("========== 创建表格 ==========")
    logger.info(f"请求 URL: {url}")

    with httpx.Client() as client:
        # 先获取 token
        token_response = client.post(token_url, json=token_payload)
        token_data = token_response.json()
        access_token = token_data.get("tenant_access_token", "")

        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

        # 创建表格
        payload = {
            "table": {
                "name": "播客主表",
                "fields": [
                    {"field_name": "播客-期数", "type": 1}
                ]
            }
        }
        logger.info(f"请求体: {payload}")

        response = client.post(url, json=payload, headers=headers)

        result = {
            "probe": "创建表格",
            "api": "POST /bitable/v1/apps/{database_id}/tables",
            "url": url,
            "database_id": config.FEISHU_DATABASE_ID,
            "request_body": payload,
            "http_status": response.status_code,
            "response_body": response.text,
        }

        logger.info(f"HTTP 状态码: {response.status_code}")
        logger.info(f"响应体: {response.text}")
        logger.info("==========================================")

        return result


@router.get("/list_tables")
async def probe_list_tables():
    """
    列出多维表中的所有表格
    API: GET /bitable/v1/apps/{database_id}/tables
    """
    url = f"{config.FEISHU_API_BASE}/bitable/v1/apps/{config.FEISHU_DATABASE_ID}/tables"

    # 获取 token
    token_url = f"{config.FEISHU_API_BASE}/auth/v3/tenant_access_token/internal"
    token_payload = {"app_id": config.FEISHU_APP_ID, "app_secret": config.FEISHU_APP_SECRET}

    logger.info("========== 列出表格 ==========")
    logger.info(f"请求 URL: {url}")

    with httpx.Client() as client:
        # 先获取 token
        token_response = client.post(token_url, json=token_payload)
        token_data = token_response.json()
        access_token = token_data.get("tenant_access_token", "")

        headers = {"Authorization": f"Bearer {access_token}"}

        response = client.get(url, headers=headers)

        result = {
            "probe": "列出表格",
            "api": "GET /bitable/v1/apps/{database_id}/tables",
            "url": url,
            "database_id": config.FEISHU_DATABASE_ID,
            "http_status": response.status_code,
            "response_body": response.text,
        }

        logger.info(f"HTTP 状态码: {response.status_code}")
        logger.info(f"响应体: {response.text}")
        logger.info("==========================================")

        return result


@router.get("/list_fields")
async def probe_list_fields():
    """
    获取表格字段列表
    API: GET /bitable/v1/apps/{database_id}/tables/{table_id}/fields
    """
    url = f"{config.FEISHU_API_BASE}/bitable/v1/apps/{config.FEISHU_DATABASE_ID}/tables/{config.FEISHU_TABLE_ID_PODCAST}/fields"

    # 获取 token
    token_url = f"{config.FEISHU_API_BASE}/auth/v3/tenant_access_token/internal"
    token_payload = {"app_id": config.FEISHU_APP_ID, "app_secret": config.FEISHU_APP_SECRET}

    logger.info("========== 获取字段列表 ==========")
    logger.info(f"请求 URL: {url}")

    with httpx.Client() as client:
        # 先获取 token
        token_response = client.post(token_url, json=token_payload)
        token_data = token_response.json()
        access_token = token_data.get("tenant_access_token", "")

        headers = {"Authorization": f"Bearer {access_token}"}

        response = client.get(url, headers=headers)

        result = {
            "probe": "获取字段列表",
            "api": "GET /bitable/v1/apps/{database_id}/tables/{table_id}/fields",
            "url": url,
            "database_id": config.FEISHU_DATABASE_ID,
            "table_id": config.FEISHU_TABLE_ID_PODCAST,
            "http_status": response.status_code,
            "response_body": response.text,
        }

        logger.info(f"HTTP 状态码: {response.status_code}")
        logger.info(f"响应体: {response.text}")
        logger.info("==========================================")

        return result


@router.post("/add_field")
async def probe_add_field():
    """
    添加字段到播客主表
    API: POST /bitable/v1/apps/{database_id}/tables/{table_id}/fields
    字段类型: 1=多行文本, 3=单选, 5=日期, 2=数字
    """
    url = f"{config.FEISHU_API_BASE}/bitable/v1/apps/{config.FEISHU_DATABASE_ID}/tables/{config.FEISHU_TABLE_ID_PODCAST}/fields"

    # 获取 token
    token_url = f"{config.FEISHU_API_BASE}/auth/v3/tenant_access_token/internal"
    token_payload = {"app_id": config.FEISHU_APP_ID, "app_secret": config.FEISHU_APP_SECRET}

    logger.info("========== 添加字段 ==========")
    logger.info(f"请求 URL: {url}")

    with httpx.Client() as client:
        # 先获取 token
        token_response = client.post(token_url, json=token_payload)
        token_data = token_response.json()
        access_token = token_data.get("tenant_access_token", "")

        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

        # 添加"总结"字段（多行文本）
        payload = {
            "field_name": "总结",
            "type": 1
        }
        logger.info(f"请求体: {payload}")

        response = client.post(url, json=payload, headers=headers)
        logger.info(f"添加'总结'字段响应: {response.text}")

        # 添加"推荐复听程度"字段（单选）
        payload2 = {
            "field_name": "推荐复听程度",
            "type": 3,
            "property": {
                "options": [
                    {"name": "必听"},
                    {"name": "推荐"},
                    {"name": "可选"}
                ]
            }
        }
        logger.info(f"请求体: {payload2}")
        response2 = client.post(url, json=payload2, headers=headers)
        logger.info(f"添加'推荐复听程度'字段响应: {response2.text}")

        result = {
            "probe": "添加字段",
            "api": "POST /bitable/v1/apps/{database_id}/tables/{table_id}/fields",
            "url": url,
            "database_id": config.FEISHU_DATABASE_ID,
            "table_id": config.FEISHU_TABLE_ID_PODCAST,
            "fields_added": [
                {"name": "总结", "response": response.json()},
                {"name": "推荐复听程度", "response": response2.json()}
            ],
            "http_status": response.status_code,
        }

        logger.info(f"HTTP 状态码: {response.status_code}")
        logger.info("==========================================")

        return result


@router.post("/create_table_main_points")
async def probe_create_table_main_points():
    """
    创建主观点表
    API: POST /bitable/v1/apps/{database_id}/tables
    字段: 所属播客(关联), 主观点序号, 主观点内容, 主观点标签, 重要
    """
    url = f"{config.FEISHU_API_BASE}/bitable/v1/apps/{config.FEISHU_DATABASE_ID}/tables"

    # 获取 token
    token_url = f"{config.FEISHU_API_BASE}/auth/v3/tenant_access_token/internal"
    token_payload = {"app_id": config.FEISHU_APP_ID, "app_secret": config.FEISHU_APP_SECRET}

    logger.info("========== 创建主观点表 ==========")
    logger.info(f"请求 URL: {url}")

    with httpx.Client() as client:
        # 先获取 token
        token_response = client.post(token_url, json=token_payload)
        token_data = token_response.json()
        access_token = token_data.get("tenant_access_token", "")

        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

        # 创建表格，包含初始字段（先创建简单字段，关联字段后续添加）
        payload = {
            "table": {
                "name": "主观点表",
                "fields": [
                    {"field_name": "主观点内容", "type": 1},
                    {"field_name": "主观点序号", "type": 2},
                    {"field_name": "主观点标签", "type": 4},
                    {"field_name": "重要", "type": 7}
                ]
            }
        }
        logger.info(f"请求体: {payload}")

        response = client.post(url, json=payload, headers=headers)
        result = {
            "probe": "创建主观点表",
            "api": "POST /bitable/v1/apps/{database_id}/tables",
            "url": url,
            "database_id": config.FEISHU_DATABASE_ID,
            "request_body": payload,
            "http_status": response.status_code,
            "response_body": response.text,
        }

        logger.info(f"HTTP 状态码: {response.status_code}")
        logger.info(f"响应体: {response.text}")
        logger.info("==========================================")

        return result


@router.post("/create_table_concepts")
async def probe_create_table_concepts():
    """
    创建概念表
    API: POST /bitable/v1/apps/{database_id}/tables
    """
    url = f"{config.FEISHU_API_BASE}/bitable/v1/apps/{config.FEISHU_DATABASE_ID}/tables"

    # 获取 token
    token_url = f"{config.FEISHU_API_BASE}/auth/v3/tenant_access_token/internal"
    token_payload = {"app_id": config.FEISHU_APP_ID, "app_secret": config.FEISHU_APP_SECRET}

    logger.info("========== 创建概念表 ==========")
    logger.info(f"请求 URL: {url}")

    with httpx.Client() as client:
        # 先获取 token
        token_response = client.post(token_url, json=token_payload)
        token_data = token_response.json()
        access_token = token_data.get("tenant_access_token", "")

        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

        # 创建表格，包含初始字段（先创建简单字段，关联字段后续添加）
        payload = {
            "table": {
                "name": "概念表",
                "fields": [
                    {"field_name": "概念名", "type": 1},
                    {"field_name": "在本期中的简要含义", "type": 1},
                    {"field_name": "学科方向", "type": 1},
                    {"field_name": "概念类型", "type": 3, "property": {"options": [{"name": "基础概念"}, {"name": "核心理论"}, {"name": "工具方法"}, {"name": "案例分析"}]}},
                    {"field_name": "来源类型", "type": 3, "property": {"options": [{"name": "书籍"}, {"name": "论文"}, {"name": "课程"}, {"name": "播客"}, {"name": "其他"}]}},
                    {"field_name": "来源名称/描述", "type": 1},
                    {"field_name": "来源是否明确", "type": 3, "property": {"options": [{"name": "是"}, {"name": "否"}]}},
                    {"field_name": "为什么值得补课", "type": 1}
                ]
            }
        }
        logger.info(f"请求体: {payload}")

        response = client.post(url, json=payload, headers=headers)
        result = {
            "probe": "创建概念表",
            "api": "POST /bitable/v1/apps/{database_id}/tables",
            "url": url,
            "database_id": config.FEISHU_DATABASE_ID,
            "request_body": payload,
            "http_status": response.status_code,
            "response_body": response.text,
        }

        logger.info(f"HTTP 状态码: {response.status_code}")
        logger.info(f"响应体: {response.text}")
        logger.info("==========================================")

        return result


@router.post("/create_table_resources")
async def probe_create_table_resources():
    """
    创建资料线索表
    API: POST /bitable/v1/apps/{database_id}/tables
    """
    url = f"{config.FEISHU_API_BASE}/bitable/v1/apps/{config.FEISHU_DATABASE_ID}/tables"

    # 获取 token
    token_url = f"{config.FEISHU_API_BASE}/auth/v3/tenant_access_token/internal"
    token_payload = {"app_id": config.FEISHU_APP_ID, "app_secret": config.FEISHU_APP_SECRET}

    logger.info("========== 创建资料线索表 ==========")
    logger.info(f"请求 URL: {url}")

    with httpx.Client() as client:
        # 先获取 token
        token_response = client.post(token_url, json=token_payload)
        token_data = token_response.json()
        access_token = token_data.get("tenant_access_token", "")

        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

        # 创建表格，包含初始字段（先创建简单字段，关联字段后续添加）
        payload = {
            "table": {
                "name": "资料线索表",
                "fields": [
                    {"field_name": "资料名称", "type": 1},
                    {"field_name": "资料类型", "type": 3, "property": {"options": [{"name": "书籍"}, {"name": "文章"}, {"name": "视频"}, {"name": "课程"}, {"name": "论文"}, {"name": "网站"}, {"name": "其他"}]}},
                    {"field_name": "原文对应摘取", "type": 1},
                    {"field_name": "来源是否明确", "type": 3, "property": {"options": [{"name": "是"}, {"name": "否"}]}},
                    {"field_name": "为什么值得看", "type": 1},
                    {"field_name": "优先级", "type": 3, "property": {"options": [{"name": "高"}, {"name": "中"}, {"name": "低"}]}}
                ]
            }
        }
        logger.info(f"请求体: {payload}")

        response = client.post(url, json=payload, headers=headers)
        result = {
            "probe": "创建资料线索表",
            "api": "POST /bitable/v1/apps/{database_id}/tables",
            "url": url,
            "database_id": config.FEISHU_DATABASE_ID,
            "request_body": payload,
            "http_status": response.status_code,
            "response_body": response.text,
        }

        logger.info(f"HTTP 状态码: {response.status_code}")
        logger.info(f"响应体: {response.text}")
        logger.info("==========================================")

        return result

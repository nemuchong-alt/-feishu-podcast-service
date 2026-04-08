# app/routes/podcast.py
import logging
import re
from typing import Optional
from fastapi import APIRouter, HTTPException
from app.schemas.podcast import (
    PodcastSaveRequest,
    PodcastSaveResponse,
)
from app.config import config
from app.feishu import feishu_client

logger = logging.getLogger(__name__)

router = APIRouter()

MAIN_POINT_ID_FIELD = "主观点ID"
MAIN_POINT_ID_PATTERN = re.compile(r"^\d{10}$")
MAIN_POINT_ID_START = 1000000001
MAIN_POINT_ID_MAX = 9999999999


def resolve_field_name(
    database_id: str,
    table_id: str,
    candidates: list[str],
) -> Optional[str]:
    """Pick the first existing field name from a candidate list."""
    fields = feishu_client.list_fields(database_id, table_id)
    existing_names = {item.get("field_name") for item in fields}
    for candidate in candidates:
        if candidate in existing_names:
            return candidate
    return None


def is_valid_main_point_id(value: object) -> bool:
    """主观点 ID 必须是 10 位纯数字字符串。"""
    if value is None:
        return False
    return bool(MAIN_POINT_ID_PATTERN.fullmatch(str(value).strip()))


def generate_main_point_id(existing_ids: list[object]) -> str:
    """
    生成新的主观点 ID。

    规则：
    1. 固定 10 位纯数字
    2. 全局流水号
    3. 起始值为 1000000001
    4. 跳过非法值（空值、非数字、长度不是 10 位）
    """
    max_valid_id: Optional[str] = None

    for value in existing_ids:
        if not is_valid_main_point_id(value):
            continue

        normalized = str(value).strip()
        if max_valid_id is None or normalized > max_valid_id:
            max_valid_id = normalized

    if max_valid_id is None:
        return str(MAIN_POINT_ID_START)

    if max_valid_id == str(MAIN_POINT_ID_MAX):
        raise ValueError("主观点 ID 已达到 10 位上限，无法继续生成")

    next_id = str(int(max_valid_id) + 1)
    if not is_valid_main_point_id(next_id):
        raise ValueError("生成的主观点 ID 非法")

    return next_id


def generate_main_point_ids(existing_ids: list[object], count: int) -> list[str]:
    """为本次批量写入预先分配一组连续的主观点 ID。"""
    if count <= 0:
        return []

    start_id = int(generate_main_point_id(existing_ids))
    end_id = start_id + count - 1
    if end_id > MAIN_POINT_ID_MAX:
        raise ValueError("主观点 ID 已达到 10 位上限，无法为本批记录分配")

    return [f"{value:010d}" for value in range(start_id, end_id + 1)]


def load_existing_main_point_ids() -> list[object]:
    """读取主观点表中已有的主观点 ID。"""
    records = feishu_client.list_records(
        config.FEISHU_DATABASE_ID,
        config.FEISHU_TABLE_ID_MAIN_POINTS,
    )
    ids: list[object] = []
    for record in records:
        fields = record.get("fields", {})
        ids.append(fields.get(MAIN_POINT_ID_FIELD))
    return ids


def build_single_link(record_id: Optional[str]) -> Optional[list[str]]:
    """飞书单向关联字段写入值：record_id 数组。"""
    if not record_id:
        return None
    return [record_id]


def save_podcast(request: PodcastSaveRequest) -> PodcastSaveResponse:
    """
    保存播客到飞书多维表

    执行流程：
    1. 创建播客主表记录
    2. 遍历主观点，创建主观点表记录，建立 seq -> record_id 映射
    3. 遍历概念，创建概念表记录，建立 name -> record_id 映射
    4. 遍历资料，创建资料线索表记录，关联主观点和概念
    """
    # 验证配置
    missing_config = config.validate()
    if missing_config:
        raise HTTPException(
            status_code=500,
            detail=f"配置缺失: {', '.join(missing_config)}",
        )

    try:
        summary_field_name = resolve_field_name(
            config.FEISHU_DATABASE_ID,
            config.FEISHU_TABLE_ID_PODCAST,
            ["总结", "个人备注"],
        )

        # === Step 1: 创建播客主表记录 ===
        podcast_fields = {
            "播客-期数": request.podcast_title,
            "推荐复听程度": request.structured_json.podcast.relisten_level,
        }
        if summary_field_name:
            podcast_fields[summary_field_name] = request.structured_json.podcast.summary
        else:
            logger.warning("播客主表未找到 summary 对应字段，已跳过写入总结")
        podcast_record_id = feishu_client.add_record(
            config.FEISHU_DATABASE_ID,
            config.FEISHU_TABLE_ID_PODCAST,
            podcast_fields,
        )
        logger.info(f"播客主表记录创建成功: {podcast_record_id}")

        # === Step 2: 创建主观点表记录 ===
        main_point_seq_to_record_id = {}
        existing_main_point_ids = load_existing_main_point_ids()
        allocated_main_point_ids = generate_main_point_ids(
            existing_main_point_ids,
            len(request.structured_json.main_points),
        )

        for index, mp in enumerate(request.structured_json.main_points):
            # 将标签列表转为逗号分隔的字符串
            tags_str = ",".join(mp.tags) if mp.tags else ""
            # 将布尔值转为单选选项文本（假设单选选项为"是"/"否"）
            important_option = "是" if mp.important else "否"

            mp_fields = {
                "主观点ID": allocated_main_point_ids[index],
                "所属播客": build_single_link(podcast_record_id),
                "主观点序号": str(mp.seq),  # 文本字段，需要字符串
                "主观点内容": mp.content,
                "主观点标签": tags_str,  # 文本字段，需要字符串
                "重要": important_option,  # 单选字段，需要选项文本
            }
            mp_record_id = feishu_client.add_record(
                config.FEISHU_DATABASE_ID,
                config.FEISHU_TABLE_ID_MAIN_POINTS,
                mp_fields,
            )
            main_point_seq_to_record_id[mp.seq] = mp_record_id
            logger.info(f"主观点记录创建成功: seq={mp.seq}, record_id={mp_record_id}")

        # === Step 3: 创建概念表记录 ===
        concept_name_to_record_id = {}
        for concept in request.structured_json.concepts:
            # 获取对应主观点的 record_id
            main_point_record = None
            if (
                concept.main_point_seq is not None
                and concept.main_point_seq in main_point_seq_to_record_id
            ):
                main_point_record = build_single_link(
                    main_point_seq_to_record_id[concept.main_point_seq]
                )

            concept_fields = {
                "概念名": concept.name,
                "在本期中的简要含义": concept.meaning_in_episode,
                "学科方向": concept.discipline,
                "概念类型": concept.concept_type,
                "来源类型": concept.source_type,
                "来源名称/描述": concept.source_name,
                "来源是否明确": concept.source_clarity,
                "为什么值得补课": concept.why_worth_learning,
                "所属播客": build_single_link(podcast_record_id),
            }
            if main_point_record:
                concept_fields["对应主观点"] = main_point_record
            concept_record_id = feishu_client.add_record(
                config.FEISHU_DATABASE_ID,
                config.FEISHU_TABLE_ID_CONCEPTS,
                concept_fields,
            )
            concept_name_to_record_id[concept.name] = concept_record_id
            logger.info(f"概念记录创建成功: {concept.name}, record_id={concept_record_id}")

        # === Step 4: 创建资料线索表记录 ===
        for resource in request.structured_json.resources:
            # 获取对应主观点的 record_id
            main_point_record = None
            if (
                resource.main_point_seq is not None
                and resource.main_point_seq in main_point_seq_to_record_id
            ):
                main_point_record = build_single_link(
                    main_point_seq_to_record_id[resource.main_point_seq]
                )

            # 获取对应概念的 record_id
            concept_record = None
            if resource.concept_name and resource.concept_name in concept_name_to_record_id:
                concept_record = build_single_link(
                    concept_name_to_record_id[resource.concept_name]
                )

            resource_fields = {
                "资料名称": resource.name,
                "资料类型": resource.resource_type,
                "原文对应摘取": resource.quote,
                "来源是否明确": resource.source_clarity,
                "为什么值得看": resource.why_worth_checking,
                "优先级": resource.priority,
                "所属播客": build_single_link(podcast_record_id),
            }
            if main_point_record:
                resource_fields["对应主观点"] = main_point_record
            if concept_record:
                resource_fields["对应概念"] = concept_record
            resource_record_id = feishu_client.add_record(
                config.FEISHU_DATABASE_ID,
                config.FEISHU_TABLE_ID_RESOURCES,
                resource_fields,
            )
            logger.info(f"资料线索记录创建成功: {resource.name}, record_id={resource_record_id}")

        logger.info(f"播客保存完成: {request.podcast_title}, record_id={podcast_record_id}")

        return PodcastSaveResponse(
            success=True,
            message="saved",
            podcast_record_id=podcast_record_id,
        )

    except Exception as e:
        logger.error(f"保存播客失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/save-podcast", response_model=PodcastSaveResponse)
async def save_podcast_endpoint(request: PodcastSaveRequest):
    """
    保存播客到飞书多维表

    接收 Dify Workflow 发来的播客整理结果，写入飞书多维表
    """
    return save_podcast(request)

# app/routes/podcast.py
import logging
from fastapi import APIRouter, HTTPException
from app.schemas.podcast import (
    PodcastSaveRequest,
    PodcastSaveResponse,
)
from app.config import config
from app.feishu import feishu_client

logger = logging.getLogger(__name__)

router = APIRouter()


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
        # === Step 1: 创建播客主表记录 ===
        podcast_fields = {
            "播客-期数": request.podcast_title,
            "总结": request.structured_json.podcast.summary,
            "推荐复听程度": request.structured_json.podcast.relisten_level,
        }
        podcast_record_id = feishu_client.add_record(
            config.FEISHU_DATABASE_ID,
            config.FEISHU_TABLE_ID_PODCAST,
            podcast_fields,
        )
        logger.info(f"播客主表记录创建成功: {podcast_record_id}")

        # === Step 2: 创建主观点表记录 ===
        main_point_seq_to_record_id = {}
        for mp in request.structured_json.main_points:
            mp_fields = {
                # "所属播客": [[podcast_record_id]],  # 关联字段暂未实现
                "主观点序号": mp.seq,
                "主观点内容": mp.content,
                "主观点标签": mp.tags,
                "重要": mp.important,
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
            if concept.main_point_seq and concept.main_point_seq in main_point_seq_to_record_id:
                main_point_record = [[main_point_seq_to_record_id[concept.main_point_seq]]]

            concept_fields = {
                "概念名": concept.name,
                "在本期中的简要含义": concept.meaning_in_episode,
                "学科方向": concept.discipline,
                "概念类型": concept.concept_type,
                "来源类型": concept.source_type,
                "来源名称/描述": concept.source_name,
                "来源是否明确": concept.source_clarity,
                "为什么值得补课": concept.why_worth_learning,
                # "所属播客": [[podcast_record_id]],  # 关联字段暂未实现
                # "对应主观点": main_point_record,  # 关联字段暂未实现
            }
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
            if resource.main_point_seq and resource.main_point_seq in main_point_seq_to_record_id:
                main_point_record = [[main_point_seq_to_record_id[resource.main_point_seq]]]

            # 获取对应概念的 record_id
            concept_record = None
            if resource.concept_name and resource.concept_name in concept_name_to_record_id:
                concept_record = [[concept_name_to_record_id[resource.concept_name]]]

            resource_fields = {
                "资料名称": resource.name,
                # "对应主观点": main_point_record,  # 关联字段暂未实现
                # "对应概念": concept_record,  # 关联字段暂未实现
                "资料类型": resource.resource_type,
                "原文对应摘取": resource.quote,
                "来源是否明确": resource.source_clarity,
                "为什么值得看": resource.why_worth_checking,
                "优先级": resource.priority,
                # "所属播客": [[podcast_record_id]],  # 关联字段暂未实现
            }
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

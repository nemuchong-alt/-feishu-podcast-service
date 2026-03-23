# app/schemas/podcast.py
from typing import Optional
from pydantic import BaseModel, Field


class PodcastData(BaseModel):
    """播客基本信息"""
    summary: str = Field(default="", description="播客简短总结")
    relisten_level: str = Field(default="", description="推荐复听程度")


class MainPoint(BaseModel):
    """主观点"""
    seq: int = Field(description="主观点序号")
    content: str = Field(default="", description="主观点内容")
    tags: list[str] = Field(default_factory=list, description="主观点标签")
    important: bool = Field(default=False, description="是否重要")


class Concept(BaseModel):
    """关键概念"""
    name: str = Field(description="概念名")
    meaning_in_episode: str = Field(default="", description="在本期中的简要含义")
    discipline: str = Field(default="", description="学科方向")
    concept_type: str = Field(default="", description="概念类型")
    source_type: str = Field(default="未提及", description="来源类型")
    source_name: str = Field(default="", description="来源名称/描述")
    source_clarity: str = Field(default="未提及", description="来源是否明确")
    why_worth_learning: str = Field(default="", description="为什么值得补课")
    main_point_seq: Optional[int] = Field(default=None, description="对应主观点序号")


class Resource(BaseModel):
    """资料线索"""
    name: str = Field(description="资料名称")
    main_point_seq: Optional[int] = Field(default=None, description="对应主观点序号")
    concept_name: Optional[str] = Field(default=None, description="对应概念名")
    resource_type: str = Field(default="", description="资料类型")
    quote: str = Field(default="", description="原文对应摘取")
    source_clarity: str = Field(default="", description="来源是否明确")
    why_worth_checking: str = Field(default="", description="为什么值得看")
    priority: str = Field(default="", description="优先级")


class StructuredJson(BaseModel):
    """结构化 JSON 数据"""
    podcast: PodcastData
    main_points: list[MainPoint] = Field(default_factory=list)
    concepts: list[Concept] = Field(default_factory=list)
    resources: list[Resource] = Field(default_factory=list)


class PodcastSaveRequest(BaseModel):
    """播客保存请求"""
    podcast_title: str = Field(description="播客标题/期数")
    display_markdown: str = Field(default="", description="给人看的 Markdown 内容")
    structured_json: StructuredJson


class PodcastSaveResponse(BaseModel):
    """播客保存响应"""
    success: bool
    message: str
    podcast_record_id: Optional[str] = None

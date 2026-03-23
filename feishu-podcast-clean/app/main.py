# app/main.py
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.routes.podcast import router as podcast_router
from app.routes.probe import router as probe_router

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="飞书播客中转服务",
    description="接收 Dify Workflow 发来的播客整理结果，写入飞书多维表",
    version="1.0.0",
)


# 注册路由
app.include_router(podcast_router, prefix="/api", tags=["播客"])
app.include_router(probe_router, prefix="/api/probe", tags=["权限探针"])


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理"""
    logger.error(f"全局异常: {exc}")
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": str(exc)},
    )


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

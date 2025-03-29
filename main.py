from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from decouple import config
from src.models.project import DBProject
from src.tasks import add_task, task_success
from rq import Callback
from src.utils import url_parse
from src.api import api_start_video, api_audio_download, api_srt_save, api_image_download
from src.request.MainRequest import (
    StartProject, AudioDownload, SrtSave, ImageDownload, VideoFinally, VideoStatus
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    from src.database import Database
    from src.redis_queue import get_redis_queue

    # 连接 redis
    app.state.queue = get_redis_queue()

    # 连接 mysql
    app.state.database = Database()
    yield


debug = config('DEBUG', default=False, cast=bool)

app = FastAPI(debug=debug, title="AIAgentAPI", lifespan=lifespan)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"],
                   allow_headers=["*"])

app.mount("/static", StaticFiles(directory="static"), name="static")

router = APIRouter(prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": 404, "config": debug}


# 创建视频
@router.post("/start")
async def start_project(item: StartProject):
    data = jsonable_encoder(item)

    result = api_start_video(data, app.state.database.session())

    return {"code": 200, "project_id": result}


# 下载音频
@router.post("/audio")
async def audio_download(item: AudioDownload):
    data = jsonable_encoder(item)

    url_status = url_parse("oceancloudapi.com", data["audio_url"])

    if not url_status:
        raise Exception("不符合的链接，请使用coze官方插件")

    result = api_audio_download(data)

    return {"code": 200, "status": result}


# 保存字幕内容
@router.post("/srt")
async def srt_save(item: SrtSave):
    data = jsonable_encoder(item)

    result = api_srt_save(data)

    return {"code": 200, "status": result}


# 下载图片素材
@router.post("/image")
async def image_download(item: ImageDownload):
    data = jsonable_encoder(item)

    url_status = url_parse("coze.cn", data["image_url"])

    if not url_status:
        raise Exception("不符合的链接，请使用coze官方图像合成插件")

    result = api_image_download(data)

    return {"code": 200, "status": result}


# 将视频块合成一个视频
@router.post("/video/finally")
async def video_finally(item: VideoFinally):
    data = jsonable_encoder(item)

    project_id, chunks_count = data["project_id"], data["chunks_count"]

    session = app.state.database.session()

    db = DBProject(session)

    self_project = db.first(project_id)

    if self_project is None:
        raise HTTPException(status_code=404)

    task_data = {
        "project_id": project_id,
        "setting": self_project.setting,
        "chunks_count": chunks_count
    }

    app.state.queue.enqueue(
        add_task,  # 任务函数
        task_data,  # 任务参数
        job_timeout=60 * 60,  # 任务超时时间（秒）
        on_success=Callback(task_success),  # 成功回调
    )

    return {"code": 200, "status": True}


# 查询视频合成状态
@router.post("/video/status")
async def video_status(item: VideoStatus):
    data = jsonable_encoder(item)

    session = app.state.database.session()

    db = DBProject(session)

    self_project = db.first(data["project_id"])

    download_url = ""

    take_time = 0

    if self_project is None:
        return {"code": 200, "status": 3, "download_url": download_url, "time": take_time}

    if self_project.file_name:
        asset_url = config('ASSET_URL', cast=str)
        download_url = f"{asset_url}/static/{self_project.id}/{self_project.file_name}"
        time_diff = self_project.updated_at - self_project.created_at
        total_seconds = int(time_diff.total_seconds())
        time_hour = total_seconds // 3600
        time_minutes = (total_seconds % 3600) // 60
        time_seconds = total_seconds % 60
        take_time = f"{time_hour:02}:{time_minutes:02}:{time_seconds:02}"

    return {"code": 200, "status": self_project.status, "download_url": download_url, "time": take_time}


app.include_router(router)

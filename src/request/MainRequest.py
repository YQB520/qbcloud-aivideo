from pydantic import BaseModel


class StartProject(BaseModel):
    user_id: str | None
    video_ratio: list
    video_fps: int
    font_size: int
    font_color: str
    stroke_color: str
    stroke_width: int
    font_bottom: int


class AudioDownload(BaseModel):
    project_id: str
    audio_url: str
    chunks_index: int


class SrtSave(BaseModel):
    project_id: str
    chunks_index: int
    content_chunks: list


class ImageDownload(BaseModel):
    project_id: str
    chunks_index: int
    image_index: int
    image_url: str


class VideoFinally(BaseModel):
    project_id: str
    chunks_count: int


class VideoStatus(BaseModel):
    project_id: str

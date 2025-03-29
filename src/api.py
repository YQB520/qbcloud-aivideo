import srt
from decouple import config
from moviepy import TextClip, ImageClip, CompositeVideoClip, concatenate_videoclips, AudioFileClip, VideoFileClip
from sqlalchemy.orm import Session
from src.models.project import DBProject
from src.utils import *


def api_start_video(data, session: Session):
    db = DBProject(session)

    debug = config('DEBUG', default=False, cast=bool)

    project_id = "test" if debug else get_uuid()

    self_project = db.first(project_id)

    if self_project is not None:
        return project_id

    db.create(project_id, data)

    project_path = get_project_path(project_id)

    asset_path = get_asset_path(project_id)

    video_path = get_video_path(project_id)

    audio_path = get_audio_path(project_id)

    images_path = get_image_path(project_id)

    srt_path = get_srt_path(project_id)

    add_folder(project_path)

    add_folder(asset_path)

    add_folder(video_path)

    add_folder(audio_path)

    add_folder(images_path)

    add_folder(srt_path)

    return project_id


def api_audio_download(data):
    audio_path = get_audio_path(data["project_id"])
    audio_path = get_path(f"{audio_path}/{data['chunks_index']}.mp3")
    return download_file(audio_path, data["audio_url"])


def api_srt_save(data):
    srt_path = get_srt_path(data["project_id"])

    srt_path = get_path(f"{srt_path}/{data['chunks_index']}.srt")

    srt_clip = []

    for item in data["content_chunks"]:
        # 字幕文件数据
        start_time = to_timedelta(item["start_time"])
        end_time = to_timedelta(item["end_time"])
        srt_data = srt.Subtitle(index=item["index"], start=start_time, end=end_time, content=item["text"])
        srt_clip.append(srt_data)

    # 生成字幕内容
    srt_data = srt.compose(srt_clip)

    with open(srt_path, "w", encoding="utf-8") as f:
        f.write(srt_data)

    return True


def api_image_download(data):
    images_path = get_image_path(data["project_id"])

    chunks_path = get_path(f"{images_path}/{data['chunks_index']}")

    add_folder(chunks_path)

    save_path = get_path(f"{chunks_path}/{data['image_index']}.png")

    return download_file(save_path, data["image_url"])


def api_video_finally(data):
    project_id = data["project_id"]

    chunks_count = data["chunks_count"]

    video_path = get_video_path(project_id)

    video_name = str_random() + ".mp4"

    asset_path = get_asset_path(project_id)

    finally_path = get_path(f"{asset_path}/{video_name}")

    if chunks_count == 1:
        file_path = get_path(f"{video_path}/0.mp4")

        copy_file(file_path, finally_path)

        return video_name

    setting = data["setting"]

    video_chunks = []

    for file_index in range(chunks_count):
        file_path = get_path(f"{video_path}/{file_index}.mp4")
        if is_file_exist(file_path):
            video_clip = VideoFileClip(file_path)
            video_chunks.append(video_clip)

    finally_video = concatenate_videoclips(video_chunks)

    logger_status = config('DEBUG', default=False, cast=bool)
    logger_status = "bar" if logger_status else None

    run_thread = load_compute()

    finally_video.write_videofile(finally_path, codec='libx264', audio_codec='aac', fps=setting["video_fps"],
                                  threads=run_thread, logger=logger_status)

    return video_name


def api_video_chunks(data):
    project_id = data["project_id"]

    chunks_index = data["chunks_index"]

    setting = data["setting"]

    video_path = get_video_path(project_id)
    video_path = get_path(f"{video_path}/{chunks_index}.mp4")

    audio_path = get_audio_path(project_id)
    audio_path = get_path(f"{audio_path}/{chunks_index}.mp3")

    srt_path = get_srt_path(project_id)
    srt_path = get_path(f"{srt_path}/{chunks_index}.srt")

    images_path = get_image_path(project_id)
    images_path = get_path(f"{images_path}/{chunks_index}")

    font_path = get_source_path("/fonts/MicrosoftYaHeiBold.ttc")

    with open(srt_path, "r", encoding="utf-8") as f:
        srt_clip = f.read()

    srt_clip = list(srt.parse(srt_clip))

    image_list = get_folder_files(images_path)
    image_list = image_list + image_list

    caption_clip = []

    image_clip = []

    cache_end_time = 0

    for caption_index, caption_item in enumerate(srt_clip):
        # 视频字幕
        start_time = round(caption_item.start.total_seconds(), 3)
        end_time = round(caption_item.end.total_seconds(), 3)
        text_clip = TextClip(
            text=caption_item.content,
            font=font_path,
            font_size=setting["font_size"],
            color=setting["font_color"],
            stroke_color=setting["stroke_color"],
            stroke_width=setting["stroke_width"]
        )
        text_clip = text_clip.with_start(start_time).with_end(end_time).with_position(
            ('center', setting["video_ratio"][1] - setting["font_bottom"]))
        caption_clip.append(text_clip)
        # 视频图片
        img_time = round(end_time - cache_end_time, 3)
        cache_end_time = end_time
        if caption_index == len(srt_clip) - 1:
            img_time += 2
        img_clip = ImageClip(image_list[caption_index]).resized(setting["video_ratio"]).with_duration(img_time)
        final_clip = apply_zoom_effect(img_clip, 3, 3, 1.12)
        image_clip.append(final_clip)

    image_video = concatenate_videoclips(image_clip)

    audio = AudioFileClip(audio_path)

    final_video = CompositeVideoClip([image_video] + caption_clip, size=setting["video_ratio"])

    final_video = final_video.with_audio(audio).with_duration(audio.duration)

    logger_status = config('DEBUG', default=False, cast=bool)
    logger_status = "bar" if logger_status else None

    run_thread = load_compute()

    final_video.write_videofile(video_path, codec='libx264', audio_codec='aac', fps=setting["video_fps"],
                                threads=run_thread, logger=logger_status)


def create_zoom_animation(zoom_in_duration, zoom_out_duration, max_scale):
    """
    创建缩放动画函数
    :param zoom_in_duration: 放大持续时间（秒）
    :param zoom_out_duration: 缩小持续时间（秒）
    :param max_scale: 最大缩放比例  例如1.5表示放大到150%
    :return: 返回根据时间计算缩放比例的函数
    """

    def get_scale(t):
        cycle_duration = zoom_in_duration + zoom_out_duration
        if cycle_duration <= 0:
            return 1.0

        t_mod = t % cycle_duration

        if t_mod <= zoom_in_duration:
            # 放大阶段
            if zoom_in_duration == 0:
                return max_scale
            return 1 + (max_scale - 1) * (t_mod / zoom_in_duration)
        else:
            # 缩小阶段
            shrink_time = t_mod - zoom_in_duration
            if zoom_out_duration == 0:
                return 1.0
            return max_scale - (max_scale - 1) * (shrink_time / zoom_out_duration)

    return get_scale


def apply_zoom_effect(img_clip, zoom_in, zoom_out, max_scale):
    # 创建动画函数
    zoom_function = create_zoom_animation(zoom_in, zoom_out, max_scale)

    # 应用缩放并保持居中
    zooming_clip = img_clip.resized(zoom_function).with_position('center')

    # 合成到原始尺寸的画布
    return CompositeVideoClip([zooming_clip], size=img_clip.size).with_duration(img_clip.duration).with_position(
        "center")


def load_compute():
    status = config('RUN_CPU', default="auto", cast=str)

    cpu_count = get_cpu_count()

    if cpu_count < 4:
        return 1

    match status:
        case "auto":
            num_thread = int(cpu_count / 2) + 1
        case "full":
            num_thread = None
        case _:
            try:
                num_thread = int(status)
                num_thread = cpu_count if num_thread > cpu_count else num_thread
            except Exception as e:
                num_thread = int(cpu_count / 2) + 1

    return num_thread

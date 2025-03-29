import multiprocessing
import os
import shutil
import requests
from datetime import timedelta
from pathlib import Path
from uuid import uuid4
from urllib.parse import urlparse


def get_cpu_count():
    return multiprocessing.cpu_count()


def get_uuid():
    return str(uuid4())


def str_random():
    random_hex_string = os.urandom(16).hex()
    return random_hex_string[:8]


def copy_file(source_file, targe_file):
    try:
        shutil.copy(source_file, targe_file)
    except FileNotFoundError:
        print("文件不存在")
    except PermissionError:
        print("权限不足")
    except Exception as e:
        print("文件复制失败", str(e))


def add_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)


def del_folder(path):
    shutil.rmtree(path)


def is_folder_exist(path):
    return os.path.isdir(path)


def is_file_exist(path):
    return os.path.isfile(path)


def get_path(path):
    return Path(path).resolve()


def get_source_path(path):
    return Path(f"./source{path}").resolve()


def get_project_path(project_id):
    return Path(f"./storage/{project_id}").resolve()


def get_asset_path(project_id):
    return Path(f"./static/{project_id}").resolve()


def get_video_path(project_id):
    project_path = get_project_path(project_id)
    return Path(f"{project_path}/video").resolve()


def get_audio_path(project_id):
    project_path = get_project_path(project_id)
    return Path(f"{project_path}/audio").resolve()


def get_image_path(project_id):
    project_path = get_project_path(project_id)
    return Path(f"{project_path}/image").resolve()


def get_srt_path(project_id):
    project_path = get_project_path(project_id)
    return Path(f"{project_path}/srt").resolve()


def get_folder_files(directory):
    path = Path(directory)
    # 获取所有文件的Path对象列表
    files = list(path.glob('*'))
    # 对Path对象列表进行排序
    files.sort(key=lambda p: p.name)  # 根据文件名排序
    return files


def to_timedelta(milliseconds):
    seconds = milliseconds // 1000
    microseconds = (milliseconds % 1000) * 1000
    return timedelta(seconds=seconds, microseconds=microseconds)


def url_parse(domain: str, url: str):
    parsed_url = urlparse(url)
    netloc = parsed_url.netloc
    return netloc in domain


def download_file(path, url):
    response = requests.get(url, verify=False, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
    })

    if response.status_code == 200:
        with open(path, 'wb') as file:
            file.write(response.content)
        return True
    else:
        return False

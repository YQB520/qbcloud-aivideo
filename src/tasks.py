import time
from src.api import api_video_chunks, api_video_finally
from src.database import Database
from src.models.project import DBProject


def add_task(data: dict):
    try:
        data["file_name"] = ""

        for i in range(data["chunks_count"]):
            data["chunks_index"] = i

            api_video_chunks(data)

            if i == data["chunks_count"] - 1:
                time.sleep(2) # 给它点时间缓一缓 ^_^
                data["file_name"] = api_video_finally(data)

        data["status"] = 1

        return data

    except Exception as e:

        data["status"] = 2

        return data


def task_success(job, connection, result):
    database = Database()

    session = database.session()

    DBProject(session).update(result["project_id"], result["status"], result["file_name"])

    session.close()

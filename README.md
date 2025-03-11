## 使用说明
开发时使用的python版本：3.10.11\
需要对FastApi、RQ有一定的认识！\
服务器低于4核4G的请勿轻易尝试！本地环境请随意。\
根目录下没有static和storage目录的，请自行创建。

## 使用
安装依赖：
```commandline
pip install -r requirements.txt
```
启动项目：
```commandline
uvicorn main:app --reload
```
启动RQ工作进程：
```commandline
python worker.py
```
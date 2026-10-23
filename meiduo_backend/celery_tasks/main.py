import os
from celery import Celery
# 1. 为Celery运行设置Django环境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo_backend.settings")
# 2. 创建实例：参数 main 设置脚本路径就可以了
app = Celery('celery_tasks')

# 3. 设置broker
app.config_from_object('celery_tasks.config')

# 4. celery自动检测任务
app.autodiscover_tasks(['celery_tasks.sms','celery_tasks.email'])
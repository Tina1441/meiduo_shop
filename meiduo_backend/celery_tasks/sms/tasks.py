from libs.yuntongxun.sms import CCP
from celery_tasks.main import app

@app.task
def celery_send_sms(mobile, data):
    ccp = CCP()
    ccp.send_template_sms(mobile, [data,'5'],1)
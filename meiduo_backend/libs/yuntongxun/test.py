

'''2. 短信发送代码'''
# libs/rl_sms.py  # 放哪里都行
from ronglian_sms_sdk import SmsSDK

accId = '2c94811c9f3cb45601a161b1da706858'  # 开发者主账号 中的 ACCOUNT SID
accToken = 'a6a71ca140484bedaf4ac01fa631e1c2'  # 开发者主账号 中的 AUTH TOKEN
appId = '2c94811c9f3cb45601a161b1db5b685f'  # 开发者主账号 中的 AppID


def send_message(phone, datas):
    sdk = SmsSDK(accId, accToken, appId)
    tid = '1'  # 测试模板id为: 1. 内容为: 【云通讯】您的验证码是{1}，请于{2}分钟内正确输入。
    # mobile = '133034xxxx'
    # datas = ('666777', '5') # 模板中的参数按照位置传递 （验证码，有效时间）
    resp = sdk.sendMessage(tid, phone, datas)
    return resp

if __name__ == '__main__':
    send_message('13539170514', ['1156', 5])



# import sys
# import ssl
# import requests
#
# print("Python 路径：", sys.executable)
# print("Python 版本：", sys.version)
# print("SSL 模块路径：", ssl.__file__)
# print("OpenSSL 版本：", ssl.OPENSSL_VERSION)
# print("Requests 版本：", requests.__version__)
# print("CA 证书路径：", requests.certs.where())


# import os
# import sys
#
# print("Python:", sys.executable)
# print("工作目录:", os.getcwd())
# print("PATH:")
# for item in os.environ.get("PATH", "").split(os.pathsep):
#     if "conda" in item.lower() or "openssl" in item.lower():
#         print(item)


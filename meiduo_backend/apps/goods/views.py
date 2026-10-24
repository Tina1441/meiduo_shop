from pathlib import Path
from fdfs_client.client import Fdfs_client

# views.py 位于 apps/goods/ 下
BASE_DIR = Path(__file__).resolve().parents[2]

conf_path = BASE_DIR / 'utils' / 'fastdfs' / 'client.conf'

print('配置文件路径：', conf_path)
print('配置文件存在：', conf_path.exists())

client = Fdfs_client(str(conf_path))

# 图片的绝对路径
image_path = r'D:\Docker\images\a.jpg'

print('图片是否存在：', Path(image_path).is_file())

result = client.upload_by_filename(image_path)
print('上传结果：', result)

"""
{'Group name': 'group1', 'Remote file_id': 'group1\\M00/00/00/wKhBA2rcFb-ACgVuAAJXemwU4Js493.jpg', 'Status': 'Upload successed.', 'Local file name': 'D:\\Docker\\images\\a.jpg', 'Uploaded size': '149.00KB', 'Storage IP': '127.0.0.1'}
"""
# 获取field_id upload上传成功后有字典返回
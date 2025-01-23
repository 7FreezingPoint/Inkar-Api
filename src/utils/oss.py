from qiniu import Auth, put_file
import os

from datetime import datetime
from src.config import Config

# 初始化 Auth 对象
q = Auth(Config.qiniu.access_key, Config.qiniu.secret_key)

# 上传文件并返回文件的网络地址
def upload_to_qiniu(local_file_path, key=None):
    """
    将本地文件上传到七牛云存储，并返回文件的网络地址

    :param local_file_path: 本地文件路径
    :param key: 文件在云存储中的名称（可选，默认使用本地文件名）
    :return: 上传文件的访问 URL
    """
    folder_path = datetime.now().strftime("%Y/%m/%d")
    key = key or f"{Config.qiniu.prefix}/{folder_path}/{os.path.basename(local_file_path)}" \
        if Config.qiniu.prefix else f"{folder_path}/{os.path.basename(local_file_path)}"

    # 生成上传凭证，有效期为3600秒
    token = q.upload_token(Config.qiniu.bucket_name, key, 3600)

    # 上传文件
    ret, info = put_file(token, key, local_file_path)

    if info.status_code == 200:  # 上传成功
        # 构造文件的网络地址
        file_url = f"{Config.qiniu.domain}/{key}"
        return file_url
    else:
        raise Exception(f"上传失败: {info}")

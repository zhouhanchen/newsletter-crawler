from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import sys
import logging


logging.basicConfig(level=logging.INFO, stream=sys.stdout)

id = ''
key = ''
token = None
region = 'ap-singapore'
config = CosConfig(Region=region, SecretId=id, SecretKey=key, Token=token)
# 2. 获取客户端对象
client = CosS3Client(config)


# 上传文件
def upload_file(local_path: str, key: str):
    response = client.put_object_from_local_file(
        Bucket='tjprivacy-1306822285',  # 替换为你的存储桶名称
        LocalFilePath=local_path,  # 本地文件路径
        Key=key  # 上传到 COS 上的文件名
    )
    print(response)


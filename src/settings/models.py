from tortoise.models import Model
from tortoise import fields


class TodoUrl(Model):
    id = fields.IntField(pk=True)
    url = fields.CharField(max_length=2000, description='链接')
    ext = fields.CharField(max_length=2000, description='扩展字段')
    status = fields.IntField(default=0, description='状态 0:待处理 1:已处理')
    source = fields.IntField(default=0, description='来源')

    class Meta:
        table = 'todo_url'


class AiInformationData(Model):
    id = fields.BigIntField(pk=True, description='主键ID')
    title = fields.TextField(null=True, description='标题')
    lang = fields.CharField(max_length=20, null=True, description='语言')
    source_url = fields.TextField(null=True, description='源链接')
    markdown = fields.TextField(null=True, description='Markdown格式的内容')
    metadata = fields.TextField(null=True, description='元数据')
    create_time = fields.DatetimeField(auto_now_add=True, null=True, description='创建时间')
    update_time = fields.DatetimeField(null=True, description='更新时间')
    status = fields.TextField(null=True, description='爬取状态')
    continent = fields.CharField(max_length=20, null=True, description='洲')
    country = fields.CharField(max_length=50, null=True, description='国家/地区')
    publish_columns = fields.CharField(max_length=50, null=True, description='发布栏目')
    publish_time = fields.DatetimeField(null=True, description='发布时间')
    deep = fields.IntField(default=0, null=True, description='当前层级')
    pid = fields.BigIntField(null=True, description='父级')
    path = fields.CharField(max_length=255, null=True)
    source = fields.IntField(null=True)

    class Meta:
        table = 'ai_information_data'

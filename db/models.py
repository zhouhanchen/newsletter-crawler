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


class MonitorSite(Model):
    id = fields.IntField(pk=True, generated=True, description='自增主键')
    site = fields.CharField(max_length=255, null=True, description='监控网站')
    latest_url = fields.TextField(null=True, description='最新URL')
    ext = fields.TextField(null=True, description='扩展信息')
    update_time = fields.DatetimeField(null=True, description='更新时间')

    class Meta:
        table = 'monitor_site'
        table_description = '监控网站表'


class TodoCleanData(Model):
    id = fields.BigIntField(pk=True)
    task_id = fields.BigIntField(null=True)
    url = fields.CharField(max_length=1000, null=True, description='链接')
    title = fields.CharField(max_length=2000, null=True, description='title')
    publish_time = fields.DatetimeField(null=True, description='发布时间')
    website_info_id = fields.BigIntField(null=True, description='网站信息id')
    region = fields.CharField(max_length=100, null=True, description='区域')
    country = fields.CharField(max_length=100, null=True, description='国家/地区')
    subject_type = fields.CharField(max_length=100, null=True, description='主体类型')
    organization_type = fields.CharField(max_length=100, null=True, description='机构类型')
    notification_agency = fields.CharField(max_length=100, null=True, description='通报机构')
    article_category = fields.CharField(max_length=100, null=True, description='文章分类')
    regional_scope = fields.CharField(max_length=100, null=True, description='地区范围')
    identification_source = fields.CharField(max_length=100, null=True, description='标识来源')
    lang = fields.CharField(max_length=20, null=True, description='网站语言')
    lang_site = fields.CharField(max_length=20, null=True, description='网站语言')
    attachment = fields.TextField(null=True, description='附件 url')
    create_time = fields.DatetimeField(null=True, description='创建时间')
    update_time = fields.DatetimeField(null=True, description='更新时间')
    status = fields.IntField(default=0, null=True, description='状态 0:未处理 1:已处理')
    retry_num = fields.IntField(default=0, null=True, description='重试次数')

    class Meta:
        table = 'todo_clean_data'
        table_description = '待清洗数据模型'


class TjPushLog(Model):
    id = fields.BigIntField(pk=True)
    status = fields.IntField(default=0, null=True, description='状态 0:失败 1:成功')
    create_time = fields.DatetimeField(null=True, description='创建时间')
    push_time = fields.DatetimeField(null=True, description='推送时间')

    class Meta:
        table = 'tj_push_log'
        table_description = 'tj cos推送日志表'

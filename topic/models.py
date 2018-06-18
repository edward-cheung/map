from django.db import models


# from django.contrib.auth.models import User


# Create your models here.

class User(models.Model):
    """
    用户设置
    """
    name = models.CharField(max_length=20, unique=True, null=False)  # 姓名
    password = models.CharField(max_length=256, null=False)  # 密码
    province = models.CharField(max_length=10, default='四川')  # 所在省份
    city = models.CharField(max_length=10, default='成都')  # 所在城市

    def __str__(self):
        return self.name


class Tag(models.Model):
    """
    话题标签
    """
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-id']


def user_directory_path(instance, filename):
    # 文件上传到MEDIA_ROOT/upload/user_<id>/<filename>目录中
    return 'upload/user_{0}/{1}'.format(instance.author.id, filename)


class Topic(models.Model):
    """
    话题
    """
    author = models.ForeignKey(User, on_delete=models.CASCADE)  # 作者
    '''
        在创建多对一的关系的,需要在Foreign的第二参数中加入on_delete=models.CASCADE 
        主外关系键中，级联删除，也就是当删除主表的数据时候从表中的数据也随着一起删除
        '''
    time = models.DateTimeField(auto_now_add=True)  # 当前日期
    city_x = models.CharField(max_length=16)  # 当前地点
    city_y = models.CharField(max_length=16)  # 当前地点
    text = models.TextField(max_length=128, blank=True, null=True)  # 话题文字内容
    images = models.ImageField(upload_to=user_directory_path, blank=True, null=True)  # 话题图片内容
    tag = models.ManyToManyField(Tag)  # 标签
    comments_num = models.IntegerField(default=0)  # 评论数
    goods_num = models.IntegerField(default=0)  # 点赞量

    class Meta:
        ordering = ['-time']


class Image(models.Model):
    """
        该话题的图片
        """
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)  # 所属话题
    author = models.ForeignKey(User, on_delete=models.CASCADE)  # 所属用户
    images = models.ImageField(upload_to=user_directory_path, blank=True, null=True)  # 话题图片

    class Meta:
        ordering = ['-id']


class Comment(models.Model):
    """
    该话题的评论
    """
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)  # 被评论的话题
    author = models.ForeignKey(User, on_delete=models.CASCADE)  # 评论人
    time = models.DateTimeField(auto_now_add=True)  # 评论时间
    content = models.CharField(max_length=32)  # 评论内容

    class Meta:
        ordering = ['-time']


class Good(models.Model):
    """
    该话题的点赞
    """
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)  # 被点赞的话题
    author = models.ForeignKey(User, on_delete=models.CASCADE)  # 点赞人
    time = models.DateTimeField(auto_now_add=True)  # 点赞时间

    class Meta:
        ordering = ['-time']

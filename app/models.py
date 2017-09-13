from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser


class UserInfo(AbstractUser):
    """
    用户信息
    """
    nid = models.BigAutoField(primary_key=True)
    nickname = models.CharField(verbose_name='昵称', max_length=32)
    telephone = models.CharField(max_length=11, blank=True, null=True, unique=True, verbose_name='手机号码')
    avatar = models.FileField(verbose_name='头像', upload_to='./upload/avatar/',default="")  # 如果是相对路径，前面不要加/
    create_time = models.DateTimeField(verbose_name='创建时间',auto_now_add=True)

    fans = models.ManyToManyField(verbose_name='粉丝们',
                                  to='UserInfo',
                                  through='UserFans',

                                  through_fields=('user', 'follower'))

    # followeds = models.ManyToManyField(verbose_name='关注',
    #                                    to='UserInfo',
    #                                    through='UserFans',
    #                                    through_fields=('follower','user'))

    # @property
    # def followrs(self): # 获取粉丝数
    #     return self.fans.count()

    def __str__(self):
        return self.username


class UserFans(models.Model):
    """
    互粉关系表
    """
    nid = models.AutoField(primary_key=True)
    user = models.ForeignKey(verbose_name='博主', to='UserInfo', to_field='nid', related_name='users')
    follower = models.ForeignKey(verbose_name='粉丝', to='UserInfo', to_field='nid', related_name='followers')

    class Meta:
        unique_together = [
            ('user', 'follower'),
        ]


class Blog(models.Model):
    """
    博客信息
    """
    nid = models.BigAutoField(primary_key=True)
    title = models.CharField(verbose_name='个人博客标题', max_length=64)
    site = models.CharField(verbose_name='个人博客后缀', max_length=32, unique=True)
    theme = models.CharField(verbose_name='博客主题', max_length=32)
    user = models.OneToOneField(to='UserInfo', to_field='nid')
    def __str__(self):
        return self.title


class Category(models.Model):
    """
    博主个人文章分类表
    """
    nid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name='分类标题', max_length=32)

    blog = models.ForeignKey(verbose_name='所属博客', to='Blog', to_field='nid')

    def __str__(self):
        return self.title


class Article(models.Model):
    nid = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=50, verbose_name='文章标题')
    desc = models.CharField(max_length=255, verbose_name='文章描述')
    read_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    up_count = models.IntegerField(default=0)
    down_count = models.IntegerField(default=0)
    category = models.ForeignKey(verbose_name='文章类型', to='Category', to_field='nid', null=True)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    blog = models.ForeignKey(verbose_name='所属博客', to='Blog', to_field='nid')
    tags = models.ManyToManyField(
        to="Tag",
        through='Article2Tag',
        through_fields=('article', 'tag'),
    )

    type_choices = [
        (1, "Python"),
        (2, "Linux"),
        (3, "OpenStack"),
        (4, "GoLang"),
    ]

    article_type_id = models.IntegerField(choices=type_choices, default=None)

    @property
    def content(self):  # 获取文章内容
        return ArticleDetail.objects.filter(nid = self.nid).first().content

    @property
    def username(self): # 获取文章用户名
        # 博客id -- > 用户名
        blog_id = self.blog_id
        return UserInfo.objects.filter(nid=blog_id).first().username

    @property
    def bloger(self): # 获取文章的博主
        blog_id = self.blog_id
        return UserInfo.objects.filter(nid=blog_id).first()

    @property
    def comments(self): #获取文章的所有评论
        return Comment.objects.filter(article_id=self.nid)

    def __str__(self):
        return self.title


class ArticleDetail(models.Model):
    """
    文章详细表
    """
    nid = models.AutoField(primary_key=True,default=1)
    content = models.TextField(verbose_name='文章内容', )

    article = models.OneToOneField(verbose_name='所属文章', to='Article', to_field='nid')


class Comment(models.Model):
    """
    评论表
    """
    nid = models.BigAutoField(primary_key=True)
    article = models.ForeignKey(verbose_name='评论文章', to='Article', to_field='nid')
    content = models.CharField(verbose_name='评论内容', max_length=255)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    parent_id = models.ForeignKey('self', blank=True, null=True, verbose_name='父级评论')
    user = models.ForeignKey(verbose_name='评论者', to='UserInfo', to_field='nid')

    up_count = models.IntegerField(default=0)

    @property
    def parent_comment(self): #获取父评论
        if self.parent_id_id:
            return Comment.objects.filter(nid=self.parent_id_id).first()




class ArticleUpDown(models.Model):
    """
    点赞表
    """
    nid = models.AutoField(primary_key=True)
    user = models.ForeignKey('UserInfo', null=True)
    article = models.ForeignKey("Article", null=True)
    UporDown=models.BooleanField(verbose_name='是否赞', default=True)




class CommentUp(models.Model):
    """
    点赞表
    """
    nid = models.AutoField(primary_key=True)
    user = models.ForeignKey('UserInfo', null=True)
    comment = models.ForeignKey("Comment", null=True)


class Tag(models.Model):
    nid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name='标签名称', max_length=32)
    blog = models.ForeignKey(verbose_name='所属博客', to='Blog', to_field='nid')


class Article2Tag(models.Model):
    nid = models.AutoField(primary_key=True)
    article = models.ForeignKey(verbose_name='文章', to="Article", to_field='nid')
    tag = models.ForeignKey(verbose_name='标签', to="Tag", to_field='nid')

    class Meta:
        unique_together = [
            ('article', 'tag'),
        ]

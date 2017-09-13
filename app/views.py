from django.shortcuts import render, redirect, HttpResponse
from .models import *
# from .models import UserInfo, Article, *
from django.core.paginator import Paginator
from django.urls import reverse
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from  SuperBlog import settings
from .forms import RegisterForm, CommentForm
from django.db.models import F,Q
from django.db.models import Avg, Sum, Min, Max, Count
import json


def get_funcs(request):
    return ({"funcs": settings.FUNCTIONS})
# get_funcs() takes 0 positional arguments but 1 was given  ; 需要有形参request


def index(request, **kwargs):
    print('访问了Index.........')
    # 渲染所有的文章, 获取用户点击的page,
    articles = Article.objects.all().order_by('create_time').reverse()
    type_choices = Article.type_choices
    print('kwargs------',kwargs)
    current_type_choice = kwargs.get('article_type', 0)
    # 如果没有这个键，说明用户访问的是首页；返回0，在模板中判断高亮效果
    # 如果拿到的是current_type_choice, 那么可以拿到type_id
    if current_type_choice:
        for type_tuple in type_choices:
            if current_type_choice in type_tuple:
                current_type_choice_id = type_tuple[0]
                articles = Article.objects.filter(article_type_id=current_type_choice_id).\
                    order_by('create_time').reverse()

    # 分页
    pagination = Paginator(articles, 10)
    page = request.GET.get('page',1)
    currentPage = int(page)
    articles = pagination.page(page)

    return render(request, 'index.html',{'articles': articles,
                                            'user': request.user,
                                            'type_choices': type_choices,
                                            'current_type_choice': current_type_choice,
                                            'pagination': pagination,
                                            'currentPage': currentPage,
    })


def my_login(request):
    print('客户端访问了---my_login')
    # next_url = request.GET.get('next')  # 这种方式取不到
    next_url = request.META.get('HTTP_REFERER', '/')
    # 这样才能取到客户端跳转前访问的地址 http://127.0.0.1:8000/blog/yuan/p/2
    # 如果是post请求过来，上述地址就会变成 http://127.0.0.1:8000/login/?next=/follow/adsd，这样post认证成功后，跳转地址就变了
    # request.session['next_url'] = next_url
    print('客户端访问地址是',next_url)
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        valid_code = request.POST.get('valid_code')
        next_url = request.POST.get('next_url')
        print(username, password, valid_code)
        ajax_response = {'user': None, "errors": ""}

        if not valid_code.upper() == request.session.get("valid_code", "a").upper():
            ajax_response["errors"] = '您输入的验证码不正确'
        else:
            print('准备验证')
            user = auth.authenticate(username=username, password=password)
            if user:
                print('验证成功')
                auth.login(request, user)
                ajax_response["user"]=user.username
                # 因为客户端是Ajax登录，因此无法接收重定向响应。
                # 改为在客户端JS跳转：location.href = next_url;
            else:
                ajax_response["errors"] = '用户名或密码错误'
                # 提示：如果总是验证失败，检查下是不是大小写问题
        return HttpResponse(json.dumps(ajax_response))

    if request.is_ajax():
        return HttpResponse(json.dumps({"login": reverse("login")}))
    else:
        # 跳转需要改，在需要登录权限的视图上加装饰器@login_required，登录成功后跳转至上次浏览的页面
        return render(request, 'login.html',{'next_url': next_url})


def valid_code(request):
    print('客户端访问了-- valid_code')
    from PIL import Image, ImageDraw, ImageFont
    from io import BytesIO  # 内存管理
    import random

    f = BytesIO()
    img = Image.new(mode='RGB', size=(120, 30),
                    color=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    # 创建图片

    draw = ImageDraw.Draw(img, mode='RGB')  # 创建画笔
    font = ImageFont.truetype("app/static/bootstrap-3.3.7/dist/fonts/kumo.ttf", 28) # 请注意路径的准确

    code_list = []
    for i in range(5):
        char = random.choice([chr(random.randint(65, 90)), str(random.randint(1, 9))])
        code_list.append(char)
        draw.text([i * 24, 0], char, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
                  font=font)
        # 位置，文本，颜色，字体
        # [i * 24, 0] 字体坐标，i*24设置水平偏移，让每个字符分开显示
    img.save(f, "png")
    valid_code = ''.join(code_list)
    request.session["valid_code"] = valid_code

    return HttpResponse(f.getvalue())


def my_logout(request):
    auth.logout(request)
    return redirect(reverse("index"))


def register(request):
    print('访问了--register')
    form_obj = RegisterForm(request) # 因为重写了init方法，这里要额外接收request
    if request.method == "POST":
        print('收到了post请求')
        print(request.POST)
        form = RegisterForm(request, request.POST) # 因为重写了init方法，这里要额外接收request
        ajax_response = {'user':None, 'errors': None}

        if form.is_valid():
            print('验证的表单数据是', form.cleaned_data)
            username = form.cleaned_data.get('username')
            if UserInfo.objects.filter(username=username):
                ajax_response['errors'] = {"username": ['用户名已存在！']}
            else:
                file_obj = request.FILES.get("img") # 获取用户上传的图像
                print(file_obj)
                UserInfo.objects.create_user(username=username,
                                             email=form.cleaned_data['email'],
                                             password=form.cleaned_data['password'],
                                             avatar=file_obj)
                ajax_response['user'] = form.cleaned_data['username']

        else:
            print('错误信息是',form.errors) # {key:[xxx], key:[],...}
            ajax_response['errors'] = form.errors

        return HttpResponse(json.dumps(ajax_response))
    return render(request,'register.html',{'form_obj': form_obj})


def change_password(request):
    pass


def home(request, sitename, **kwargs):
    # print('访问了home')
    # 过滤用户，如果存在，渲染主页，否则404
    bloger = UserInfo.objects.filter(username=sitename).first()
    condition = kwargs.get("condition")
    if bloger:
        current_blog = bloger.blog
        articles = current_blog.article_set.all()   # 当前站点下的所有文章

        # 拿到分类
        category_list = current_blog.category_set.all()
        # 当前站点的分类及文章数（如果用values_list, 前端渲染更方便一点
        category_details = Article.objects.filter(blog=current_blog).values_list("category__title").annotate(
            Count('title'))
        # print('分类及文章个数',category_details) #分类及文章个数 <QuerySet [('python', 2), ('前端', 1), ('版本控制', 1)]>

        # 拿到标签和对应文章个数  tag和article多对多
        tag_details = articles.values_list("tags__title").annotate(Count("title"))
        # 通过tags字段__ 双下划线反向到Tag表
        # print('标签及文章个数',tag_details)

        # 拿到日期和对应文章数
        # 拿到所有的日期，处理掉冗余，对比去重
        date_archives = {}
        for article in articles:
            format_date = str(article.create_time.date())  # 将日期时间 转化为Y-M-D日期：2017-09-08
            print(format_date)
            if format_date not in date_archives:
                date_archives[format_date] = 0
        # 拿到日期字典，循环文章，如果日期一样，值加一
        # print('日期字典',date_archives)
        for article in articles:
            d = str(article.create_time.date())
            if d in date_archives:
                date_archives[d] += 1
                # print('日期和数量',date_archives)
                # print('日期和数量', date_archives)

        # r'^(?P<sitename>\w+)/articles/(?P<condition>category|tag|date)/(?P<title>\w+/)$'
        title = kwargs.get('title')
        print('title--------',title)
        # title-------- python/  修改前端的url  title-------- 版本控制/  在url匹配中分组后加/就正常了，django默认会加/
        if condition =="category":
            category_id = Category.objects.filter(title=title).first()
            articles = current_blog.article_set.filter(category_id=category_id)
        elif condition == "tag": # tag和blog多对一，tag和文章多对多；因为这里blog定了，所以tag的范围也是定点
            tag_id = Tag.objects.filter(title=title)
            records = Article2Tag.objects.filter(tag_id=tag_id)
            articles = []
            for record in records:
                articles.append(current_blog.article_set.filter(nid=record.article_id).first())
            print('tag文章清单是',articles)

        elif condition == "date":
            # 根据日期date拿到datetime
            articles = []
            for article in current_blog.article_set.all():
                if str(article.create_time.date()) == title:
                    articles.append(article)
            print('日期分类文章清单是')

        # 分页
        pagination = Paginator(articles, 10)
        page = request.GET.get('page', 1)
        currentPage = int(page)
        articles = pagination.page(page)

        return render(request, 'home.html', {"bloger": bloger,
                                                 "category_details": category_details,
                                                 "tag_details": tag_details,
                                                 "date_archives": date_archives,
                                                "pagination": pagination,
                                                "currentPage": currentPage,
                                                "articles": articles,})
    else:
        return render(request, '404.html')


def article(request,sitename, article_id):
    article = Article.objects.filter(nid=article_id).first()
    # bloger = UserInfo.objects.filter(username=sitename).first()
    if article:
        comment_form = CommentForm()
        bloger = article.bloger
        comments = article.comments
        # 分页
        # pagination = Paginator(comments, 10)
        # page = request.GET.get('page', 1)
        # currentPage = int(page)
        # comments = pagination.page(page)

        return render(request, 'post.html', {"article":article,
                                                "bloger": bloger,
                                                "comment_form": comment_form,
                                                "comments": comments,})
                                                # "pagination": pagination,
                                                # "currentPage":currentPage})
    else:
        return render(request,'404.html')


@login_required
def follow(request,bloger):
    return render(request, 'test.html')


@login_required
def article_poll(request):  # 文章点赞功能
    print('访问了poll.........')
    article_id = request.GET.get('article_id')
    current_article = Article.objects.filter(nid=article_id)    # update方法只能用于QSET对象

    if current_article:
        flag = int(request.GET.get('flag'))  # flag点赞标志位：1 赞 0 踩
        print('flag--------%r'%flag)    # flag--------'1', 因为ajax发送的是字符串，所以上面要转为int
        # 先过滤ArticleUpDown，如果存在article和user记录：
        # 如果用户已经赞，再次点赞就删除赞；-- 更改bool值，article的 up_count -1
        # 如果用户已经赞，点踩，就删除该用户的赞 -- 更改bool值，articled的up_count -1 down_count +1
        # 如果用户已经踩，再点踩，就删除该用户的踩 -- 更改bool值，article的down_count -1
        # 如果不存在记录：新建记录
        record = ArticleUpDown.objects.filter(article=current_article, user=request.user)
        if record: # 有记录
            print('存在赞踩记录。。。')
            if record.first().UporDown: # 原记录是点赞
                if flag ==1:    # 再次取消点赞，删除该条记录，文章赞 -1
                    record.delete()
                    current_article.update(up_count = F("up_count")-1)
                else: # 踩, 更改为踩，文章赞 -1 踩 +1
                    record.update(UporDown = False)
                    current_article.update(up_count = F("up_count")-1)
                    current_article.update(down_count = F("down_count")+1)
            else: # 原记录是踩
                if flag == 1: # 点赞，
                    record.update(UporDown = True)
                    current_article.update(up_count = F("up_count")+1)
                    current_article.update(down_count = F("down_count")-1)
                else: # 踩, 取消踩，删除这条记录，文章踩 -1
                    record.delete()
                    current_article.update(down_count = F("down_count")-1)
        else: # 没有记录
            article_obj = current_article.first()   # query set 集合取到实例，下面新建记录要用
            print('不存在赞踩记录。。。，新建。。。')
            record = ArticleUpDown(user=request.user, article=article_obj)

            if flag == 1:
                record.UporDown = True
                record.save()
                current_article.update(up_count = F("up_count")+1)
            else:
                record.UporDown = False
                record.save()
                current_article.update(down_count = F("down_count")+1)

        current_article = current_article.first()
        print('赞数', current_article.up_count, '踩数',current_article.down_count)
        ajax_response = {'up': current_article.up_count, 'down': current_article.down_count}
        # 'error':'', 'login':''
        return HttpResponse(json.dumps(ajax_response))

    else:
        return HttpResponse(json.dumps({'error': '无法找到文章！'}))
    # 'login':''


@login_required
def comment_poll(request):
    print('访问了comment_poll.......')
    comment_id = int(request.GET.get('comment_id'))
    print('comment_id',comment_id)
    comment = Comment.objects.filter(nid=comment_id)
    if comment:
        record = CommentUp.objects.filter(comment_id=comment_id, user_id=request.user.nid)
        if record:
            print('已经点赞')
            # 说明已经点赞，再次点击，取消赞
            record.delete()
            comment.update(up_count = F("up_count")-1)
        else:
            print('未点赞')
            c = CommentUp(comment_id=comment_id,user_id=request.user.nid)
            c.save()
            comment.update(up_count = F("up_count")+1)

        comment_obj = comment.first()
        ajax_response = {"up":comment_obj.up_count}
        print('comment点赞数',comment_obj.up_count)
        return HttpResponse(json.dumps(ajax_response))

    else:
        return HttpResponse(json.dumps({'error': '无法找到评论！'}))


@login_required
def write_comment(request): # 写评论：文章, 评论内容，用户
    article_id = request.POST.get("article_id")
    article_obj = Article.objects.filter(nid=article_id)
    ajax_response = { "errors":"", "ele":""}
    parent_comment_id = request.POST.get("parent_comment_id") # 父级评论,通过这个值是否为空，来判断对文章评论还是对评论评论
    print('父级的id是',parent_comment_id)

    if article_obj:
        if parent_comment_id: # 说明对评论评论
            print('对评论评论------')
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                parent_comment_obj = Comment.objects.filter(nid=parent_comment_id).first()  # 父评论
                parent_comment_username = parent_comment_obj.user.nickname
                print('父项评论的用户是',parent_comment_username)
                comment_body = comment_form.cleaned_data["comment_body"]
                print('评论内容是',comment_body)
                # Comment表新建一条记录，Article 评论数+1
                c = Comment(content=comment_body,
                            article_id=article_id,
                            user_id=request.user.nid,
                            parent_id_id=parent_comment_id)
                c.save()
                article_obj.update(comment_count=F("comment_count") + 1)
                res = render(request, 'render_comment.html', {"comment": c,
                                                                "parent_comment_obj":parent_comment_obj})
                return res  # 前端在json解析res时，通过异常捕捉判断这个响应

            else:
                errors = comment_form.errors
                print('错误信息是...',errors)
                ajax_response['errors']=errors

        else: # 单纯对文章评论
            print('对文章评论-----------')
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment_body = comment_form.cleaned_data.get("comment_body")
                print(comment_body)
                # Comment表新建一条记录，Article 评论数+1
                c = Comment(content=comment_body,
                            article_id=article_id,
                            user_id=request.user.nid)
                c.save()
                article_obj.update(comment_count=F("comment_count") + 1)

                res = render(request, 'render_comment.html', {"comment": c})
                return res  # 前端在json解析res时，通过异常捕捉判断这个响应

            else:
                errors = comment_form.errors
                print('错误信息是...', errors)
                ajax_response['errors'] = errors

    else:
        errors = {"errors": ["内容不存在或已删除！"]}
        ajax_response['errors']=errors

    return HttpResponse(json.dumps(ajax_response))
    # httpresponse不能json, 不支持的格式；
    # 因此需要一个办法在前端判断，是直接接收render字符串响应，还是json响应；前者直接当html元素添加到页面，后者解析；
    # 异常捕捉搞定





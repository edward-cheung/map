from django.shortcuts import HttpResponse, render
from django.shortcuts import redirect

# from django.forms.models import model_to_dict

import hashlib
import json

# from urllib import parse

from topic.models import User, Tag, Topic, Comment, Good, Image
from topic import forms


# Create your views here.


def hash_encode(s, salt='map'):  # 加点盐,对用户密码进行hash编码
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())  # update方法只接收bytes类型
    return h.hexdigest()


class TopicEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Topic):
            if obj.images:
                return {
                    'p_id': obj.id,
                    'p_author': obj.author.name,
                    'city_x': obj.city_x,
                    'city_y': obj.city_y,
                    'p_text': obj.text,
                    'p_images': obj.images.url,
                    'comments_num': obj.comments_num,
                    'goods_num': obj.goods_num
                }
            else:
                return {
                    'p_id': obj.id,
                    'p_author': obj.author.name,
                    'city_x': obj.city_x,
                    'city_y': obj.city_y,
                    'p_text': obj.text,
                    'comments_num': obj.comments_num,
                    'goods_num': obj.goods_num
                }
        return json.JSONEncoder.default(self, obj)


def index(request):
    user_info = {'id': request.session.get('user_id', ''),
                 'name': request.session.get('user_name', ''),
                 'province': request.session.get('user_province', ''),
                 'city': request.session.get('user_city', '')
                 }
    data = list()  # <-   data = []
    topic, comments, is_good = None, None, False
    topics = Topic.objects.all()
    if request.method == "GET":
        option = request.GET.get('opt', '').strip()
        user_name = request.GET.get('u', '').strip()
        content = request.GET.get('cont', '').strip()
        tag_name = request.GET.get('t', '').strip()
        if option and user_name:
            user = User.objects.get(name=user_name)
            if option == 'homepage':
                user_topics = topics.filter(author=user)
                for t in user_topics:
                    data.append(json.dumps(t, cls=TopicEncoder))  # data.append(model_to_dict(t))

            elif option == 'comments':
                user_comments = Comment.objects.filter(author=user)
                for c in user_comments:
                    data.append(json.dumps(c.topic, cls=TopicEncoder))

            elif option == 'goods':
                user_goods = Good.objects.filter(author=user)
                for g in user_goods:
                    data.append(json.dumps(g.topic, cls=TopicEncoder))

            else:
                for t in topics:
                    data.append(json.dumps(t, cls=TopicEncoder))

        if tag_name:
            tag = Tag.objects.get(name=tag_name)
            topics = tag.topic_set.all()
            for t in topics:
                data.append(json.dumps(t, cls=TopicEncoder))

        if not data:
            for t in topics:
                data.append(json.dumps(t, cls=TopicEncoder))

        if content:
            # topic = topics.filter(text=parse.unquote(content)).first()
            topic = topics.get(pk=content)
            # tags = topic.tag.all()
            comments = topic.comment_set.all()  # 外键反向查询
            goods = topic.good_set.all()
            try:
                goods = goods.filter(author=User.objects.get(name=request.session.get('user_name', '')))
                is_good = True if goods else False
            except Exception:
                is_good = False
        return render(request, 'index.html',
                      {'user_info': json.dumps(user_info),
                       'data': json.dumps(data),
                       'topic': topic,
                       'comments': comments,
                       'is_good': is_good
                       })


def login(request):
    if request.method == "POST":
        login_form = forms.UserForm(request.POST)
        message = "请检查填写的内容！"
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            try:
                user = User.objects.get(name=username)
                if user.password == hash_encode(password):
                    request.session['is_login'] = True
                    request.session['user_id'] = user.id
                    request.session['user_name'] = user.name
                    request.session['user_province'] = user.province
                    request.session['user_city'] = user.city
                    return redirect('/')
                else:
                    message = "密码不正确！"
            except Exception:
                message = "用户名不存在！"
        return render(request, 'login.html', locals())

    login_form = forms.UserForm()
    return render(request, 'login.html', locals())


def login1(request):
    if request.session.get('is_login', None):
        return redirect("/")
    if request.method == "POST":
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        message = "所有字段都必须填写！"
        if username and password:  # 确保用户名和密码都不为空
            username = username.strip()
            # 用户名字符合法性验证
            # 密码长度验证
            # 更多的其它验证.....
            try:
                user = User.objects.get(name=username)
                if user.password == hash_encode(password):
                    request.session['is_login'] = True
                    request.session['user_id'] = user.id
                    request.session['user_name'] = user.name
                    return redirect('/')
                else:
                    message = "密码不正确！"
            except Exception:
                message = "用户名不存在！"
        return render(request, 'login.html', {"message": message})
    return render(request, 'login.html')


def register(request):
    if request.session.get('is_login', None):
        # 登录状态不允许注册。你可以修改这条原则！
        return redirect("/")
    if request.method == "POST":
        username = request.POST.get('username', None)
        password1 = request.POST.get('password1', None)
        password2 = request.POST.get('password2', None)
        message = "请检查填写的内容！"
        if username and password1 and password2:  # 确保用户名和密码都不为空
            username = username.strip()
            if password1 != password2:  # 判断两次密码是否相同
                message = "两次输入的密码不同！"
                return render(request, 'register.html', locals())
            else:
                same_name_user = User.objects.filter(name=username)
                if same_name_user:  # 用户名唯一
                    message = '用户已经存在，请重新选择用户名！'
                    return render(request, 'register.html', locals())

                # 当一切都OK的情况下，创建新用户
                new_user = User.objects.create()
                new_user.name = username
                new_user.password = hash_encode(password1)
                new_user.save()
                return redirect('/login/')  # 自动跳转到登录页面
    return render(request, 'register.html', locals())


def logout(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/")
    request.session.flush()  # <- del request.session["username"]
    return redirect('/')


def issue(request):
    if request.session.get('is_login', None):
        response = {'flag': False}
        if request.method == "POST":
            topic_tag = request.POST.get('topic_tag', None)
            topic_text = request.POST.get('topic_text', None)
            topic_images = request.FILES.getlist('topic_images', None)
            topic_author = User.objects.get(pk=request.session.get('user_id'))

            # file_content = ContentFile(request.FILES['img'].read())
            # files = request.FILES.getlist('my_files')
            # for f in files:
            #     destination = open('d:/temp/' + f.name, 'wb+')
            #     for chunk in f.chunks():
            #         destination.write(chunk)
            #     destination.close()

            if topic_tag and topic_text:
                new_topic = Topic.objects.create(author=topic_author,
                                                 city_x=request.COOKIES.get('point_x'),
                                                 city_y=request.COOKIES.get('point_y'),
                                                 text=topic_text.strip(),
                                                 images=topic_images[0]
                                                 )
                topic_tag = topic_tag.split()
                for t in topic_tag:
                    tags = Tag.objects.all()
                    tags = list(map(str, tags))
                    if t not in tags:
                        Tag.objects.create(name=t)
                    tag = Tag.objects.get(name=t)
                    new_topic.tag.add(tag)
                    new_topic.save()
                response['flag'] = True
                response['message'] = "发表成功！"
                return HttpResponse(json.dumps(response))
            else:
                response['message'] = "填写内容不能为空！"
                return HttpResponse(json.dumps(response))
        else:
            return redirect("/")
    else:
        return redirect("/login/")


def messages(request):
    pass
    return render(request, 'messages.html')


def settings(request):
    if request.session.get('is_login', None):
        if request.method == "POST":
            province = request.POST.get('province', None)
            city = request.POST.get('city', None)
            message = "请检查填写的内容！"
            if province == '请选择省份' and city == '请选择城市':
                return render(request, 'settings.html', locals())
            else:
                new_user = User.objects.get(pk=request.session.get('user_id'))
                new_user.province = province
                new_user.city = city
                new_user.save()
                request.session['user_province'] = province
                request.session['user_city'] = city
                return render(request, 'settings.html')
        else:
            return render(request, 'settings.html')
    else:
        return redirect("/login/")


def comment(request):
    if request.session.get('is_login', None):
        response = {'flag': False}
        if request.method == "POST":
            user = User.objects.get(pk=request.session.get('user_id'))
            topic = Topic.objects.get(pk=request.POST.get('topic_id'))
            content = request.POST.get('content', None)
            if topic and content:
                Comment.objects.create(topic=topic, author=user, content=content)
                topic.comments_num += 1
                topic.save()
                response['flag'] = True
                return HttpResponse(json.dumps(response))
            else:
                return HttpResponse(json.dumps(response))
        else:
            return redirect("/")
    else:
        return redirect("/login/")


def good(request):
    if request.session.get('is_login', None):
        response = {'flag': False}
        if request.method == "POST":
            user = User.objects.get(pk=request.session.get('user_id'))
            topic = Topic.objects.get(pk=request.POST.get('topic_id'))
            goods = topic.good_set.all()
            goods = goods.filter(author=User.objects.get(name=request.session.get('user_name', '')))
            if goods:
                return HttpResponse(json.dumps(response))
            else:
                if topic:
                    Good.objects.create(topic=topic, author=user)
                    topic.goods_num += 1
                    topic.save()
                    response['flag'] = True
                    return HttpResponse(json.dumps(response))
                else:
                    return HttpResponse(json.dumps(response))
        else:
            return redirect("/")
    else:
        return redirect("/login/")

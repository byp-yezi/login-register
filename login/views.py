from django.shortcuts import render, redirect
from . import models
from . import forms
from django.conf import settings
from django.utils import timezone
import hashlib, datetime


# Create your views here.


def send_mail(email, code):
    from django.core.mail import EmailMultiAlternatives

    subject = '来自叶子的注册确认邮件'

    text_content = '''感谢注册，如果你看到这条消息，说明你的邮箱服务器不提供HTML链接功能，请联系管理员！'''

    html_content = '''
                        <p>感谢注册<a href="http://{}/confirm/?code={}" target=blank>www.yezi.com</a>，\
                        专注于Python、Django和机器学习技术的分享！</p>
                        <p>请点击站点链接完成注册确认！</p>
                        <p>此链接有效期为{}天！</p>
                        '''.format('127.0.0.1:8080', code, settings.CONFIRM_DAYS)

    msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def make_confirm_string(user):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    code = hash_code(user.name, now)
    models.ConfirmString.objects.create(code=code, user=user)
    return code


def hash_code(s, salt='login-register'):
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())
    return h.hexdigest()


def user_confirm(request):
    code = request.GET.get('code', None)
    message = ''
    try:
        confirm = models.ConfirmString.objects.get(code=code)
    except:
        message = '无效的确认请求'
        return render(request, 'login/confirm.html', locals())

    c_time = confirm.c_time
    now = datetime.datetime.utcnow().replace(tzinfo=timezone.utc)
    if now > c_time + datetime.timedelta(settings.CONFIRM_DAYS):
        confirm.user.delete()
        message = '你的邮件已经过期，请重新注册'
        return render(request, 'login/confirm.html', locals())
    else:
        confirm.user.has_confirmed = True
        confirm.user.save()
        confirm.delete()
        message = '已经确认，请使用账户登录'
        return render(request, 'login/confirm.html', locals())



def index(request):
    if not request.session.get('is_login', None):
        return redirect('/login/')
    return render(request, 'login/index.html')


def login(request):
    if request.session.get('is_login', None):
        return redirect('/index/')
    if request.method == 'POST':
        login_form = forms.UserForm(request.POST)
        message = '请检查填写的内容!'
        if login_form.is_valid():
            username = login_form.cleaned_data.get('username')
            password = login_form.cleaned_data.get('password')

            try:
                user = models.User.objects.get(name=username)
            except:
                message = '用户不存在!'
                return render(request, 'login/login.html', locals())

            if not user.has_confirmed:
                message = '该用户未经过邮件确认'
                return render(request, 'login/login.html', locals())

            if user.password == hash_code(password):
                request.session['is_login'] = True
                request.session['user_id'] = user.id
                request.session['user_name'] = user.name
                return redirect('/index/')
            else:
                message = '密码不正确!'
                return render(request, 'login/login.html', locals())
        else:
            return render(request, 'login/login.html', locals())

    login_form = forms.UserForm()
    return render(request, 'login/login.html', locals())


def register(request):
    if request.session.get('is_login', None):
        return redirect('/index/')
    if request.method == 'POST':
        register_form = forms.RegisterForm(request.POST)
        message = '请检查填写的内容!'
        if register_form.is_valid():
            username = register_form.cleaned_data.get('username')
            password1 = register_form.cleaned_data.get('password1')
            password2 = register_form.cleaned_data.get('password2')
            email = register_form.cleaned_data.get('email')
            sex = register_form.cleaned_data.get('sex')

            if password1 != password2:
                message = '两次输入的密码不一致'
                return render(request, 'login/register.html', locals())
            else:
                try:
                    same_name_user = models.User.objects.filter(name=username)
                    if same_name_user:
                        message = '用户已存在'
                        return render(request, 'login/register.html', locals())
                    same_email_user = models.User.objects.filter(email=email)
                    if same_email_user:
                        message = '邮箱已存在'
                        return render(request, 'login/register.html', locals())
                    new_user = models.User()
                    new_user.name = username
                    new_user.password = hash_code(password1)
                    new_user.email = email
                    new_user.sex = sex
                    new_user.save()

                    code = make_confirm_string(new_user)
                    send_mail(email, code)
                    return redirect('/login/')
                except:

                    return render(request, 'login/register.html', locals())
        else:
            return render(request, 'login/register.html', locals())
    register_form = forms.RegisterForm()
    return render(request, 'login/register.html', locals())


def logout(request):
    if not request.session.get('is_login', None):
        return redirect('/login/')
    request.session.flush()
    return redirect("/login/")

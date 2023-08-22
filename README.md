# 这是一个用户登录和注册教学项目
# 简单的使用方法：

1、使用pip安装第三方依赖
pip install -r requirements.txt

2、修改settings.example.py文件为settings.py，并修改文件内容
SECRET_KEY = 'xxxxxxxxxxxxxxxxxxx'
EMAIL_HOST_USER = 'xxxxxxxx@qq.com'
EMAIL_HOST_PASSWORD = 'xxxxxxxxxxxx'

3、进入到项目根目录，运行python manage.py makemigrations和python manage.py migrate命令，创建数据库和数据表

4、运行python manage.py runserver启动服务器


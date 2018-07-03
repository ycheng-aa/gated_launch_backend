.. _development:


配置开发环境
=============================



项目代码Gerrit网址
---------------------

http://git.intra.ffan.com/#/admin/projects/qa/gated-launch-backend


环境配置
----------------

Python版本
`````````````````````````````````
确保本地使用版本为python3.5


可选: 安装虚拟环境
``````````````````````

安装virtualenvwrapper ::

    $ pip install virtualenvwrapper
    $ mkvirtualenv gated-launch


安装依赖库
`````````````

进入项目根目录，继续 ::

    $ workon gated-launch
    $ pip install -r requirements/production.txt
    $ pip install -r requirements/devel.txt


定制settings
```````````````

在项目目录，即 `根目录/gated_launch_backend` 下,加入自己的配置，例如数据库配置，celery配置


初始化数据库
``````````````````````

::

    $ python manage.py migrate --noinput


可选：启动celery
``````````````````````

一些接口和功能依赖于celery，如果需要运行或调试相应功能，需要启动celery。


在灰度项目中，settings默认使用redis做为broker和result backend。因此首先根据不同系统在本系统安装redis server，安装完成后启动redis server。

使用 redis-cli 进行确认: ::

    $ redis-cli ping
    PONG

在项目根目录运行: ::

    $ celery -A gated_launch_backend.celery worker -l info
    $ celery -A gated_launch_backend.celery beat


启动服务
----------------

默认情况下在 127.0.0.1:8000 启动服务::

    $ python manage.py runserver


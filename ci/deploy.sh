#!/bin/bash

set -e

export LANG=zh_CN.gbk
export LANGUAGE=zh_CN.gbk
unset LC_ALL
ftpServer="10.213.137.52"
ftpUser="ffanscm"
ftpPass="ffanscm"

BUILD_NUMBER=$2
product_name=$3
module_name=$4
deploy_dir=/home/sre

##每个环节校验执行结果，如果失败则exit 1

# 1 参数校验
if [ "$1" == "sit" ];then
	echo "Begin to deploy to sit."
elif [ $1 == "product" ];then
	echo "Begin to deploy to product."
else
	echo "your parm is wrong."
	exit 1
fi

# 2 环境准备--安装本次部署所需要的环境
#   环境校验--获取每项环境的version号，和标准的进行比对，不一致退出

echo "the environment has been installed successfully"

# 3 分环境获取安装包
if [ "$1" == "sit" ];then
	deploy_dir=/home/ee
fi
mkdir -p ${deploy_dir}/deploy/gated_launch_backend/$BUILD_NUMBER
cd ${deploy_dir}/deploy/gated_launch_backend/$BUILD_NUMBER

if [ "$1" == "sit" ];then
	echo "get the sit package..."
    ftp -n <<EOF
	open $ftpServer	10021
	user $ftpUser $ftpPass
	prompt
	bin
	cd sit/${product_name}/${module_name}
	mget ${product_name}_sit_${module_name}_${BUILD_NUMBER}.tar.tgz
	by
EOF

elif [ $1 == "product" ];then
	echo "get the sit package..."
	ftp -n <<EOF
	open $ftpServer 10021
    user $ftpUser $ftpPass
    prompt
    bin
    cd product/${product_name}/${module_name}
    mget ${product_name}_product_${module_name}_${BUILD_NUMBER}.tar.tgz
    by
EOF

fi
echo "get the package successfully"

# 4 解压包，启动服务--一般各套环境的启动服务的命令一致
cd ${deploy_dir}/deploy/gated_launch_backend/$BUILD_NUMBER
tar zxvf ${product_name}_$1_${module_name}_${BUILD_NUMBER}.tar.tgz

PROJECT_DIR=${deploy_dir}/gated-launch-backend

sudo mkdir -p $PROJECT_DIR

sudo cp -rf output/* $PROJECT_DIR

echo "cp to project dir successfully"

cd $PROJECT_DIR

# 安装requirments
sudo /usr/local/python35/bin/pip3 install -r requirements/production.txt

if [ "$1" == "sit" ];then
	echo "install..."
	sudo /usr/local/python35/bin/pip3 install -r requirements/devel.txt
fi

echo "pip install successfully"

sudo /usr/local/python35/bin/python3 manage.py migrate --noinput
#sudo /usr/local/python35/bin/python3 manage.py collectstatic

echo "DB migrate successfully"

# 获得新配置并，重启所有相关服务， 假设supervisord已经启动
sudo supervisorctl -c ./supervisor.conf stop all

sudo supervisorctl -c ./supervisor.conf reload

echo "restart Django, celery and Nginx successfully"

if [ "$1" == "sit" ];then
    # 生成项目文档

    # 先生成model关系图
    echo "making docs"
    sudo /usr/local/python35/bin/python3 manage.py graph_models -aE -o docs/build/docs/models_svg/all.svg
    sudo /usr/local/python35/bin/python3 manage.py graph_models -gE app -o docs/build/docs/models_svg/app.svg
    sudo /usr/local/python35/bin/python3 manage.py graph_models -gE auth -o docs/build/docs/models_svg/auth.svg
    sudo /usr/local/python35/bin/python3 manage.py graph_models -gE award -o docs/build/docs/models_svg/award.svg
    sudo /usr/local/python35/bin/python3 manage.py graph_models -gE bp -o docs/build/docs/models_svg/bp.svg
    sudo /usr/local/python35/bin/python3 manage.py graph_models -gE common -o docs/build/docs/models_svg/common.svg
    sudo /usr/local/python35/bin/python3 manage.py graph_models -gE info -o docs/build/docs/models_svg/info.svg
    sudo /usr/local/python35/bin/python3 manage.py graph_models -gE issue -o docs/build/docs/models_svg/issue.svg
    sudo /usr/local/python35/bin/python3 manage.py graph_models -gE strategy -o docs/build/docs/models_svg/strategy.svg
    sudo /usr/local/python35/bin/python3 manage.py graph_models -gE task_manager -o docs/build/docs/models_svg/task_manager.svg
    sudo /usr/local/python35/bin/python3 manage.py graph_models -gE user_group -o docs/build/docs/models_svg/user_group.svg

    # 生成文档
    make docs
    echo "docs done"
fi



# 5 验证服务是否ok

echo "verify service successfully"

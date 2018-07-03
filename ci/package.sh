#!/bin/bash

export LANG=zh_CN.gbk
export LANGUAGE=zh_CN.gbk
unset LC_ALL
ftpServer="10.213.137.52"
ftpUser="ffanscm"
ftpPass="ffanscm"

BUILD_NUMBER=$1
product_name=$2
module_name=$3

#1 为不同环境打不同的包
#1.1 sit环境打包--生成zhongce_sit_${module_name}_${BUILD_NUMBER}.tar.tgz
mkdir output
cp -rf apps extra_apps benchmark_django_rest_framework gated_launch_backend requirements statics docs Makefile manage.py supervisor.conf config_files newrelic.ini output
tar -zcvf ${product_name}_sit_${module_name}_${BUILD_NUMBER}.tar.tgz output

echo "package for sit env successful"

#1.2 product环境打包----生成zhongce_product_backend_${BUILD_NUMBER}.tar.tgz
tar -zcvf ${product_name}_product_${module_name}_${BUILD_NUMBER}.tar.tgz output

echo "package for product env successful"


#2 将不同环境的包上传至不同的ftp目录
#2.1 上传sit包至ftp
#------------------tranfer  .tgz to the ftp-----------------------
	ftp -n <<EOF
	open $ftpServer	10021
	user $ftpUser $ftpPass
	prompt	
	bin
	cd sit/${product_name}/${module_name}
	put ${product_name}_sit_${module_name}_${BUILD_NUMBER}.tar.tgz
    cd ../../../product/${product_name}/${module_name}
    put ${product_name}_product_${module_name}_${BUILD_NUMBER}.tar.tgz
	by
EOF
#-----------------------------------------------------------------

#3 删除workspace下的tar包和output目录
rm -rf ${product_name}_sit_${module_name}_${BUILD_NUMBER}.tar.tgz
rm -rf ${product_name}_product_${module_name}_${BUILD_NUMBER}.tar.tgz
rm -rf output



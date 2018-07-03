# -*- coding: utf-8 -*-
import argparse
import os
import django
import xlrd
from django.contrib.auth import get_user_model

#  you have to set the correct path to you settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gated_launch_backend.settings")
django.setup()


def update_mail(phone, mail_1, mail_2):
    mail = mail_1 if mail_1 else mail_2
    get_user_model().objects.filter(phone=phone).update(email=mail)


def import_mail_info(file_path):
    book = xlrd.open_workbook(file_path)
    sh = book.sheet_by_index(0)
    # format:
    # 移动电话  电子邮件（工作） 电子邮件（个人）
    for rx in range(sh.nrows):
        if rx == 0:
            continue
        row = sh.row(rx)

        update_mail(str(int(row[0].value)), row[1].value.strip(), row[2].value.strip())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='导入快钱信息')
    parser.add_argument('-s', '--source',
                        help='source data file', required=True)
    options = parser.parse_args()
    import_mail_info(options.source)

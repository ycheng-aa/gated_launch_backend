# -*- coding: utf-8 -*-
import argparse
import os
import django
import xlrd
from django.contrib.auth import get_user_model

#  you have to set the correct path to you settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gated_launch_backend.settings")
django.setup()


def update_mail(ctx, mail_prefix):
    get_user_model().objects.filter(username=ctx).update(email=mail_prefix + '@hd123.com')


def import_mail_info(file_path):
    book = xlrd.open_workbook(file_path)
    sh = book.sheet_by_index(0)
    # format:
    # 移动电话  电子邮件（工作） 电子邮件（个人）
    for rx in range(sh.nrows):
        if rx == 0:
            continue
        row = sh.row(rx)
        ctx_account = row[0].value.strip()
        mail_prefix = ctx_account.rstrip('1234567890')

        update_mail(ctx_account, mail_prefix)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='导入快钱信息')
    parser.add_argument('-s', '--source',
                        help='source data file', required=True)
    options = parser.parse_args()
    import_mail_info(options.source)

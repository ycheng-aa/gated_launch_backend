from apps.common.tests import BaseTestCase
from apps.auth.models import Department
from django.contrib.auth import get_user_model


class AuthTestCase(BaseTestCase):
    def setUp(self):
        # 一级部门
        self.depl1_1 = Department.objects.create(name='一级部门1')
        self.depl1_2 = Department.objects.create(name='一级部门2')

        # 二级部门
        self.depl2_1_1 = Department.objects.create(name='二级部门1_1', parent=self.depl1_1)
        self.depl2_1_2 = Department.objects.create(name='二级部门1_2', parent=self.depl1_1)

        # 二级部门
        self.depl2_2_1 = Department.objects.create(name='二级部门2_1', parent=self.depl1_2)
        self.depl2_2_2 = Department.objects.create(name='二级部门2_2', parent=self.depl1_2)

        self.user_1 = get_user_model().objects.create(username='user1', email='user1@test.com',
                                                      password='test', department=self.depl2_1_1)
        self.user_2 = get_user_model().objects.create(username='user2', email='user2@test.com',
                                                      password='test', department=self.depl2_2_1)

    def test_department_structure(self):
        dep = Department.objects.get(name='二级部门2_2')
        self.assertEqual(dep.parent.name, '一级部门2')

        dep = Department.objects.get(name='二级部门1_2')
        self.assertEqual(dep.parent.name, '一级部门1')

        dep = Department.objects.get(name='一级部门1')
        result = []
        for d in dep.get_children():
            result.append(d)

        # 一级部门1的所有后代
        self.assertEqual(result, [self.depl2_1_1, self.depl2_1_2])

        # test level
        # 一级部门
        self.assertEqual(self.depl1_1.get_level(), 0)
        self.assertEqual(self.depl1_2.get_level(), 0)

        # 二级部门
        self.assertEqual(self.depl2_1_1.get_level(), 1)
        self.assertEqual(self.depl2_2_2.get_level(), 1)

    def test_user_dep_ino(self):
        # test user's direct department
        self.assertEqual(self.user_1.direct_dep.name, '二级部门1_1')
        self.assertEqual(self.user_2.direct_dep.name, '二级部门2_1')

        # test user's level 1 department
        self.assertEqual(self.user_1.level_one_dep.name, '一级部门1')
        self.assertEqual(self.user_2.level_one_dep.name, '一级部门2')

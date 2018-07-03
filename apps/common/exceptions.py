# coding:utf-8
class JiraError(Exception):
    """ Inappropriate argument value (of correct type). """
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        """ Create and return a new object.  See help(type) for accurate signature. """
        return self.msg

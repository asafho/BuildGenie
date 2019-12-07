from .common import *

__author__ = 'asafh'

class test(object):

    def __init__(self, obj):
        self.obj = obj

    def run_pipe(self):
        execute_pipeline(self.obj, 'test')
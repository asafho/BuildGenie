from .common import *

__author__ = 'asafh'

class build(object):

    def __init__(self, obj):
        self.obj = obj

    def run_pipe(self):
        logs("start running build pipeline")
        for cmd in self.obj:
            keys_list = list(cmd.keys())

            run_dir = None
            if 'run_dir' in keys_list:
                run_dir = get_json_value(cmd, 'run_dir')
                keys_list.remove('run_dir')

            for key in keys_list:
                command = get_json_value(cmd, key) or None
                if key == 'sh':
                    key = ''
                run_cli(key +' '+ command, run_dir=run_dir)

        logs("end running build pipeline")

import argsParser
from pipesParser import pipesParser
from services.common import *

__author__ = 'asafh'

class BuildGenie(object):

    def __init__(self, args):
        logs("init vars")
        self.sudoPass = args['sudoPass']
        self.prepare = args['prepare']
        self.post = args['post']
        self.build = args['build']
        self.test = args['test']
        self.package = args['package']
        self.version = args['version']
        self.git_creds = args['git_creds']
        self.pipe = load_json_to_string(args['pipeline_file'], self.version)
        self.pipe_branches = args['pipe_branches']

        pipe_runner = pipesParser(self)
        run_all_steps=True
        if self.prepare is True:
            pipe_runner.pipelines(step='prepare')
            pipe_runner.prepare()
            run_all_steps = False

        if self.build is True:
            pipe_runner.pipelines(step='build')
            pipe_runner.build()
            run_all_steps = False

        if self.test is True:
            pipe_runner.pipelines(step='test')
            pipe_runner.test()
            run_all_steps = False

        if self.package is True:
            pipe_runner.pipelines(step='package')
            pipe_runner.package()
            run_all_steps = False

        if self.post is True:
            pipe_runner.pipelines(step='post')
            pipe_runner.post()
            run_all_steps = False

        if run_all_steps == True:
            pipe_runner.pipelines() # run multi pipelines file
            pipe_runner.prepare()
            pipe_runner.build()
            pipe_runner.test()
            pipe_runner.package()
            pipe_runner.post()


if __name__ == '__main__':
    args = argsParser.ArgParser().parse_args()
    args = vars(args)
    buildGenie = BuildGenie(args)

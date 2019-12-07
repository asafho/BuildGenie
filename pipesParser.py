from services.common import *
from services.git import git
from services.filesystem import filesystem
from services.build import build
from services.test import test
from services.package import package

__author__ = 'asafh'


class pipesParser(object):

    def __init__(self,obj, initWorkspace=True):
        self.obj = obj
        self.pipe = obj.pipe
        self.version = obj.version
        self.pipe_branches = obj.pipe_branches
        self.git_creds = obj.git_creds
        self.create_snapshot_log()
        if initWorkspace == True:
            self.workspace_path = self.init_workspace()

    def create_snapshot_log(self):

        self.snapshot_file_dir = '/tmp/genie/log/'
        self.snapshot_file = '/'.join([self.snapshot_file_dir, self.version,'.json'])
        try:
            if not os.path.exists(self.snapshot_file_dir):
                run_cli('mkdir -p ' + self.snapshot_file_dir)
            run_cli('chmod -R 777 ' + self.snapshot_file_dir, exit_on_failure=False)
        except:
            logs('failed to create snapshot path')




    def init_workspace(self):
        if 'workspace' in self.pipe:
            path = self.pipe['workspace']
        else:
            path = 'workspace'
        if not path.startswith('/'):
            path = '/'.join([os.getcwd(),path])
        if not os.path.exists(path):
            logs("creating workspace path")
            os.makedirs(path)
        else:
            run_cli('rm -rf build_packages', run_dir=path)
        logs('==========================WORKSPACE===========================')
        logs(path)
        logs('==============================================================')
        os.chdir(path)
        return path

    def prepare(self):
        # run prepare pipe
        if 'prepare' in self.pipe:
            prepare = self.pipe['prepare']
            logs(prepare)
            if 'git' in prepare:
                logs("start running git pipe")
                objects = prepare['git']
                for obj in objects:
                    pipe = git(self, obj, pipeline_branches=self.pipe_branches, git_credentials=self.git_creds)
                    pipe.run_pipe()
                logs("end running git pipe")
            if 'filesystem' in prepare:
                # run pipe on filesystem stage
                objects = prepare['filesystem']
                pipe = filesystem(objects, self.workspace_path)
                pipe.run_pipe()
            if 'build' in prepare:
                # run pipe on filesystem stage
                objects = prepare['build']
                pipe = build(objects)
                pipe.run_pipe()

    def post(self):
        # run post pipe
        if 'post' in self.pipe:
            post = self.pipe['post']
            logs(post)
            if 'git_tag' in post:
                logs("start running git tag")
                objects = post['git_tag']
                for obj in objects:
                    pipe = git(self, obj, pipe_branches=self.pipe_branches, git_credentials=self.git_creds)
                    pipe.tag()
                logs("end running git tag")

    def build(self):
        if 'build' not in self.pipe:
            return
        objects = self.pipe['build']
        pipe = build(objects)
        pipe.run_pipe()

    def test(self):
        if 'test' not in self.pipe:
            return
        objects = self.pipe['test']
        pipe = test(objects)
        pipe.run_pipe()

    def package(self,version=None):
        if 'package' not in self.pipe:
            return
        objects = self.pipe['package']
        pipe = package(objects, version=self.version,
                                workspace_path = self.workspace_path,
                                package_skip_docker = self.package_skip_docker)
        pipe.pack()


    #function to run multi pipeline files
    def pipelines(self, step='all'):
        if 'pipelines' not in self.pipe:
            return
        objects = self.pipe['pipelines']
        dir_path = os.path.dirname(os.path.realpath(__file__))
        for p in objects:
            p_path = '/'.join([dir_path,'pipelines',p])
            content = load_json_to_string(p_path, self.version)
            self.obj.pipe = content
            subpipe = pipesParser(self.obj, initWorkspace=False)
            subpipe.workspace_path = self.workspace_path
            if step == 'prepare' or step == 'all':
                subpipe.prepare()
            if step == 'build' or step == 'all':
                subpipe.build()
            if step == 'test' or step == 'all':
                subpipe.test()
            if step == 'package' or step == 'all':
                subpipe.package(self.version)
            if step == 'post':
                subpipe.post()


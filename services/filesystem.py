from .common import *

__author__ = 'asafh'


class filesystem(object):

    def __init__(self, obj, workspace_path):
        self.dirs = get_json_value(obj, 'dirs') or []
        self.files = get_json_value(obj, 'files') or []
        self.links = get_json_value(obj, 'links') or []
        self.workspace_path = workspace_path

    def run_pipe(self):
        logs("start running filesystem pipeline")
        self.create_dirs()
        self.create_files()
        self.create_links()
        logs("end running filesystem pipeline")

    def create_dirs(self):
        logs("create directories")
        for d in self.dirs:
            run_cli("mkdir -p {0}".format(d))

    def create_files(self):
        logs("create empty files")
        logs (self.files)
        for f in self.files:
            run_cli("touch {0}".format(f))

    def create_links(self):
        logs ("create links")
        for link in self.links:
            run_cli("ln -sf {0} {1}".format('/'.join([self.workspace_path,link['dst']]),link['src']), run_dir=self.workspace_path)
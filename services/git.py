import os
import subprocess
from .common import *
import json
__author__ = 'asafh'


class git(object):

    def __init__(self, obj=None,json_obj=None, pipeline_branches=None, git_credentials=None):
        self.obj = obj
        self.repo = get_json_value(json_obj, 'repo')
        self.user = get_json_value(json_obj, 'user')
        self.cmd = get_json_value(json_obj, 'cmd')
        self.version = None
        try:
            self.version = obj.version
        except:
            print ("version not defined")
        self.repo_dir = get_json_value(json_obj, 'repo_dir')
        self.branch = get_json_value(json_obj, 'branch') or "master"
        self.git_url = get_json_value(json_obj, 'git_url') or "github.com"
        self.repoDirPath = get_json_value(json_obj, 'dest') or self.repo
        self.mergeBranch =  get_json_value(json_obj, 'mergeBranch')
        self.newBranch = get_json_value(json_obj, 'newBranch')
        self.pushNewBranch = get_json_value(json_obj, 'pushNewBranch')
        if git_credentials:
            logs("using git credentials with https")
            self.git_repo_url='https://{0}@{1}/'.format(git_credentials, self.git_url)
        else:
            logs("using git ssh keys")
            self.git_repo_url = 'git@{0}:'.format(self.git_url)

        if pipeline_branches:
            # pipeline_branches format reponame:branch
            repo_details = pipeline_branches.strip().split(',')
            if len(repo_details) == 1 and ':' not in repo_details[0]:
                self.branch = repo_details[0]
            else:
                for repo in repo_details:
                    full_repo = repo.split(':')
                    if full_repo[0] == self.repo:
                        self.branch = full_repo[1]
                        break
        if os.environ.get('sourceBranch') is not None:
            repositoryBranch = os.environ.get('sourceBranch')
            repositoryName = os.environ.get('repositoryName')
            if self.repo == repositoryName:
                self.branch = repositoryBranch
                if os.environ.get('targetBranch') is not None:
                    self.mergeBranch = os.environ.get('targetBranch')

    def run_pipe(self):
        logs("start-running git pipeline")
        self.pull(self.repo,
                  self.repoDirPath,
                  self.branch,
                  self.user)
        if self.mergeBranch:
            self.merge()
        logs("end-running git pipeline")

    def pull(self, repoName, repoDirPath, branch, user):
        if not repoDirPath:
            self.repoDirPath = repoName
        run_cli("rm -rf {}".format(self.repoDirPath))
        cloneArgs=''
        if not self.mergeBranch:
            cloneArgs = '--depth 1'
        cmd = "git clone -b {0} {1}{2}/{3}.git {4} {5}".format(branch,
                                                               self.git_repo_url,
                                                               user,
                                                               repoName,
                                                               self.repoDirPath,
                                                               cloneArgs)
        run_cli(cmd)

        run_cli('git branch', run_dir=self.repoDirPath)
        if self.version:
            sha = run_cli('git rev-parse HEAD',  run_dir=self.repoDirPath)
            self.snapshot_append(repoName, branch, sha.replace('\n', ''))

        if self.newBranch:
            run_cli('git checkout -b {0}'.format(self.newBranch), run_dir=self.repoDirPath)
            run_cli('git branch', run_dir=self.repoDirPath)
            if self.pushNewBranch:
                run_cli('git push --set-upstream origin {0}'.format(self.newBranch), run_dir=self.repoDirPath)

    def merge(self):
        cmd = "git merge origin/{0}".format(self.mergeBranch)
        run_cli(cmd, run_dir=self.repoDirPath)

    def snapshot_append(self, repo, branch, sha):
        snap = {}
        if os.path.isfile(self.obj.snapshot_file):
            with open(self.obj.snapshot_file, 'r') as f:
                snap = json.load(f)
        snap[repo] = {}
        snap[repo]['branch'] = branch
        snap[repo]['sha'] = sha

        with open(self.obj.snapshot_file, 'w+') as f:
            json.dump(snap, f, indent=4)

    def tag(self, repo_dir, sha, version):
        run_cli('git tag -a {0}-BuildGenie -m "tag {0}"'.format(version), run_dir=repo_dir)
        run_cli('git push --tags', run_dir=repo_dir)

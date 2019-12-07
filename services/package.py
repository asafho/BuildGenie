from .common import *
import shutil
from datetime import datetime

__author__ = 'asafh'


class package(object):

    def __init__(self, obj, version='1.0', workspace_path = '/tmp'):
        self.obj = obj
        self.version = version
        self.workspace_path = workspace_path
        self.deb_package_dir = None
        self.artifacts = []
        self.set_init_service = "false"
        self.set_deb_scripts = "true"
        self.templates_path = os.path.dirname(os.path.realpath(__file__)) + '/../templates/debian/'
        self.PACKAGES_DIR='/'.join([self.workspace_path, 'build_packages'])

        if not os.path.exists(self.PACKAGES_DIR):
            os.makedirs(self.PACKAGES_DIR)

    def pack(self):
        logs("build packages")
        for cmd in self.obj:
            json = get_json_value(cmd, 'deb') or None
            if json:
                logs("build deb by json: " + str(json))
                self.prepare_debian_package(json)

            json = get_json_value(cmd, 'docker') or None
            if json:
                logs("build docker by json: " + str(json))
                self.prepare_docker_package(json)
        logs("end running build pipeline")

    def prepare_docker_package(self, json):
        execute_pipeline(json, 'package docker')

    def prepare_debian_package(self, json):
        self.parse_json(json)
        self.prepare_DEBIAN_DIR(json)
        self.prepare_ubuntu_package()
        if self.set_init_service == 'true' or self.set_init_service == 'yes':
            self.set_deb_initD()
        self.build_debian()

    def set_deb_initD(self):
        initdPath = '/'.join([self.deb_package_dir,'/etc/init.d/'])
        with open(self.templates_path+'initd-service', 'r') as myfile:
            data = myfile.read().replace('<service_name>', self.service_name)
            try:
                os.makedirs(os.path.dirname(initdPath))
            except:
                logs("")
            with open(initdPath + self.package_name, 'w') as file:
                file.write(data)

    def parse_json(self, json_file):

        if isinstance(json_file, dict):
            data = json_file
            self.repo_path = data['repo']
        else:
            self.repo_path = json_file.split('/')[0]
            with open(json_file) as data_file:
                data = json.load(data_file)
        logs(data)
        self.package_name = data['package']
        self.artifacts = data['artifacts']
        self.git_sha = run_cli('git rev-parse HEAD', run_dir=self.repo_path).replace('\n', '')
        self.git_branch = run_cli('git rev-parse --abbrev-ref HEAD', run_dir=self.repo_path).replace('\n', '')

        if '/' in self.package_name:
            self.package_name = 'ik-' + self.package_name.split('/')[-1]
        self.service_name = self.package_name
        if 'update_env' in data:
            self.update_env = data['update_env']
        if 'set_init_service' in data:
            self.set_init_service = data['set_init_service'].lower()
        if 'set_deb_scripts' in data:
            self.set_deb_scripts = data['set_deb_scripts'].lower()


        self.deb_package_dir = os.path.join(self.PACKAGES_DIR, self.package_name, self.package_name, self.package_name + '_' + self.version)
        logs(self.deb_package_dir)

    def prepare_DEBIAN_DIR(self,file):

        logs("update DEBIAN directory")
        try:
            srcDEBIAN = os.path.dirname(file) + '/DEBIAN/'
        except:
            srcDEBIAN = None
        dstDEBIAN = self.deb_package_dir + '/DEBIAN/'

        if os.path.exists(dstDEBIAN):
            shutil.rmtree(dstDEBIAN)
        os.makedirs(dstDEBIAN)
        if self.set_deb_scripts == "true":
            debian_files=['control', 'postinst', 'preinst', 'prerm']
        else:
            debian_files = ['control']
        for f in debian_files:
            if srcDEBIAN and os.path.exists(srcDEBIAN+f):
                f_path = srcDEBIAN + f
            else:
                f_path = self.templates_path + f
            with open(f_path, "r") as conrolFile:
                data = conrolFile.read()
                data = data.replace('<service_name>', self.package_name)
                data = data.replace('<version>', self.version)
                data = data.replace('<git_sha>', self.git_sha)
                data = data.replace('<git_branch>', self.git_branch)
                with open(dstDEBIAN+f, "w") as newfile:
                    newfile.write(data)
        run_cli('chmod -R a+x {0}'.format(dstDEBIAN))

    def prepare_ubuntu_package(self):
        logs('preparing package for debian build')
        logs(self.deb_package_dir)
        versionFile = '/'.join([self.workspace_path, self.repo_path,'version.json'])
        with open(versionFile, 'w') as file:
            file.write('{"version":"'+self.version+'"}')
        for a in self.artifacts:
            self.copyfiles(a,type='deb')

    def build_debian(self):
        dst_file = '{0}/{1}.deb'.format(self.PACKAGES_DIR, self.package_name)
        logs(self.deb_package_dir)
        run_cli('dpkg-deb --build ' + self.deb_package_dir + ' ' + dst_file)

    def copyfiles(self, artifact,type=None):
        dst = artifact['dst']
        exclude = []
        exclude_from_file = []
        logs('update package dest to version')
        files = []
        if 'files' in artifact:
            files = artifact['files']
        if 'exclude' in artifact:
            exclude = artifact['exclude']
        if 'exclude_from_file' in artifact:
            exclude_from_file = artifact['exclude_from_file']
        logs("files: " + str(files))
        logs("exclude: " + str(exclude))
        if type == 'deb':
            dst_dir = '/'.join([self.deb_package_dir, dst])
        else:
            dst_dir = '/'.join([self.PACKAGES_DIR,self.package_name, dst])
        logs(dst_dir)
        repo_full_path = '/'.join([self.workspace_path, self.repo_path])
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        for f in exclude_from_file:
            exclude_file='/'.join([repo_full_path, f])
            if os.path.isfile(exclude_file):
                self.exclude_from_file(repo_full_path, exclude_file)
        for f in exclude:
            run_cli('rm -rf {0}/{1}'.format(dst_dir,f))
        for f in files:
            f = '/'.join([self.workspace_path, self.repo_path,f])
            run_cli('cp -r {0} {1}'.format(f, dst_dir))

    def exclude_from_file(self, dst_dir, exclude_file):
        logs("removing files that are listed in: " + exclude_file)
        removed_scripts=0
        with open(exclude_file, "r") as exclude_data:
            data = exclude_data.readlines()
            for line in data:
                line = line.strip()
                if not len(line.strip()) == 0 and not line.startswith('#'):
                    file_to_remove = '/'.join([dst_dir,line])
                    if os.path.exists(file_to_remove):
                        run_cli('rm -r {0}'.format(file_to_remove))
                        removed_scripts += 1
        logs("*********************************")
        logs("number of removed files: " + str(removed_scripts))
        logs("*********************************")

    def update_file(self, file_path):
        file_path = '/'.join([self.workspace_path, self.repo_path, file_path])
        content = open(file_path, 'r').read()
        os.environ["buildVersion"] = self.version
        os.environ["date"] = datetime.now().strftime('%d-%m-%Y')
        os.environ["gitSha"] = self.git_sha

        vars = []
        for line in content.split('\n'):
            if '${' and '}' in line:
                vars.append(line.split("${", 1)[1].split("}")[0])

        for var in vars:
            logs("updating file with: " + var)
            content = content.replace("${" + var + "}", os.environ.get(var))
        with open(file_path, "w") as f:
            f.write(content)


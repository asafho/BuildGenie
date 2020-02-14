from argparse import (ArgumentParser,
                      RawTextHelpFormatter)

__author__ = 'asafh'


class ArgParser(ArgumentParser):
    def __init__(self):
        description = 'Genie Parameters.'
        super(ArgParser, self).__init__(description=description,
                                        formatter_class=RawTextHelpFormatter)

    def parse_args(self):

        self.add_argument('--sudo-pass', '-s',
                          action='store',
                          dest='sudoPass',
                          default=None,
                          help='sudo user password')

        self.add_argument('--pipeline-file', '-pf',
                          action='store',
                          type=str,
                          dest='pipeline_file',
                          default='',
                          help='build pipe json')

        self.add_argument('--pipeline-branches','-pb',
                          action='store',
                          type=str,
                          dest='pipe_branches',
                          default='',
                          help='Git Branches Seperated by comma ("<repo:branch>')

        self.add_argument('--version','-v',
                          action='store',
                          type=str,
                          dest='version',
                          default='1.0',
                          help='version')

        self.add_argument('--build','-b',
                          action='store_true',
                          dest='build',
                          default=False,
                          help='build without reconfigure workspace')

        self.add_argument('--test','-t',
                          action='store_true',
                          dest='test',
                          default=False,
                          help='run tests')


        self.add_argument('--prepare','-pr',
                          action='store_true',
                          dest='prepare',
                          default=False,
                          help='prepare workspace')

        self.add_argument('--post','-pb',
                          action='store_true',
                          dest='post',
                          default=False,
                          help='run post build actions')

        self.add_argument('--git-credentials','-gc',
                          action='store',
                          dest='git_creds',
                          default=None,
                          help='git credential for https commands')

        self.add_argument('--package','-p',
                          action='store_true',
                          dest='package',
                          default=False,
                          help='run package instructions')

        return super(ArgParser, self).parse_args()

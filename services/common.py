import os
import subprocess
import sys
import json

__author__ = 'asafh'


def logs(str):
    try:
        str = json.dumps(str, indent=4)
    except:
        pass
    print(str)

def execute_pipeline(json_object, step = 'unknown'):
    logs("start to execute {0} pipeline".format(step))
    for cmd in json_object:
        keys_list = list(cmd.keys())
        if 'run_dir' in keys_list:
            run_dir = get_json_value(cmd, 'run_dir')
            keys_list.remove('run_dir')
        else:
            run_dir = None
        for key in keys_list:
            command = get_json_value(cmd, key) or None
            if key == 'sh':
                key = ''
            run_cli(key + ' ' + command, run_dir=run_dir)
    logs("end {0} pipeline".format(step))

def run_cli(cmd, run_dir=None,sudoPass=None, exit_on_failure=True, verbose=True):

    current_dir = os.getcwd()
    if run_dir:
        os.chdir(run_dir)
    if sudoPass:
        cmd = 'echo {0} | sudo -S {1}'.format(sudoPass, cmd)
    logs("working dir: " + os.getcwd())
    logs(cmd)
    p = subprocess.Popen(cmd, shell=True,  universal_newlines=True, stdout=subprocess.PIPE)
    console_output=''
    while True:
        line = p.stdout.readline()
        if line == '' and p.poll() != None:
            break
        if verbose == True:
            sys.stdout.write(line)
            sys.stdout.flush()
            console_output +=line

    exitCode = p.returncode
    if (exitCode == 0):
        logs("INFO:command")
        if not os.path.exists(current_dir):
            os.makedirs(current_dir)
        os.chdir(current_dir)
        return console_output
    else:
        os.chdir(current_dir)
        if exit_on_failure == True:
            logs("ERROR: " + cmd)
            raise Exception
        else:
            logs("IGNORE: ignoring failure")


def load_json_to_string(content, version):
    logs(content)
    if os.path.exists(os.path.dirname(content)):
        logs("load json from path: " + content)
        content = open(content, 'r').read()

    logs("replace arguments in file")
    content = content.replace('<version>', version)
    try:
        content = json.loads(content)
    except ValueError as e:
        logs("Invalid json content")
        raise e
    logs(content)
    return content


def get_json_value(obj, arg):
    if arg in obj:
        return obj[arg]
    else:
        return None

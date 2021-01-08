import os
import subprocess
import sys
import time


def human_parser_run_script():
    print('parse script')
    cwd = os.getcwd()
    parser_path = os.path.join(os.getenv('HOME'), 'human_parser', 'human-parser')
    os.chdir(parser_path)

    os.system('bash run_script.sh')
    print('asdasdasdas')
    os.chdir(cwd)

    return True

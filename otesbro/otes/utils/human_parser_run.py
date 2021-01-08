import os
import subprocess
import sys
import time


def human_parser_run_script():
    cwd = os.getcwd()
    print('-asdasdasd')
    path = '/home/park/human_parser/human-parser/'
    # interpreter = '/home/park/anaconda3/envs/otesbro/bin/python'
    # interpreter = sys.executable
    # cmd = 'python simple_extractor.py --model-restore "checkpoints/exp-schp-201908261155-lip.pth" --input-dir "inputs" --output-dir "outputs"'
    # cmd = '{} simple_extractor.py --model-restore "checkpoints/exp-schp-201908261155-lip.pth" --input-dir "inputs" --output-dir "outputs"'.format(interpreter)

    # print(interpreter)
    os.chdir(path)

    # os.system('bash run_hp.sh')
    subprocess.call('bash run_hp.sh', shell=True)
    # subprocess.run(cmd, shell=True)
    # subprocess.call([interpreter, cmd], shell=True)
    time.sleep(0.5)
    print('END')
    os.chdir(cwd)

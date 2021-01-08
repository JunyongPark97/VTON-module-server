import os
import sys
# sys.path.append(os.path.realpath('..'))
cwd = os.getcwd()
openpose_wd = os.getenv('HOME') + '/Desktop/otesbro/otesbro/otes/utils/openpose'
os.chdir(openpose_wd)
print('---')
# path = os.getenv('HOME') + '/Desktop/otesbro/otes/utils/openpose/test.py'
path = 'test.py'

cmd = 'python {}'.format(path)
os.system(cmd)

os.chdir(cwd)
#!/bin/bash

sudo cp /home/park/Desktop/otesbro/otesbro/otes/utils/tmp/avatar_in.png /home/human/human_parser/human-parser/inputs/avatar_in.png && sudo chown human:human /home/human/human_parser/human-parser/inputs/avatar_in.png

echo 'avatar in transfered'

sudo bash /home/human/human_parser/human-parser/run_script.sh

echo 'human run script'

sudo cp /home/human/human_parser/human-parser/outputs/avatar_in.png /home/park/Desktop/otesbro/otesbro/otes/utils/tmp/avatar_out.png && sudo chown park:park /home/park/Desktop/otesbro/otesbro/otes/utils/tmp/avatar_out.png

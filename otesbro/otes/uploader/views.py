import os
import subprocess
import json
import sys
from io import BytesIO

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.views.generic import TemplateView, DetailView
import time
from PIL import Image

from uploader.forms import InputImageUploadForm
from uploader.models import AcgpnInputs, Outputs
from utils.background_remover import remover
from utils.human_parser_run import human_parser_run_script
from utils.pixel_segmentation import mask_3d_255, edge_255
import subprocess


class CheckACGPNInputsView(DetailView):
    queryset = AcgpnInputs.objects.all()
    template_name = 'check_acgpn_inputs.html'


class CheckACGPNOutputsView(DetailView):
    queryset = Outputs.objects.all()
    template_name = 'acgpn_outputs.html'


class InputImageUploadView(TemplateView):
    template_name = 'input_images_uploader.html'

    def get_context_data(self, **kwargs):
        context = super(InputImageUploadView, self).get_context_data()
        form = InputImageUploadForm
        context['form'] = form
        return context

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        form = InputImageUploadForm(request.POST, request.FILES)
        file = form.files
        self.m_target = file.get('target')
        self.m_human_model = file.get('human_model')
        if form.is_valid():
            inputs = form.save(commit=False)
            inputs.ip = request.META['REMOTE_ADDR']
            inputs.save()

            acgpn_inputs, _ = AcgpnInputs.objects.get_or_create(reference_input=inputs)

            self.avatar_warping_mask(inputs, acgpn_inputs)
            self.human_model_segmentation(inputs, acgpn_inputs)
            self.target_nukkiNmask(inputs, acgpn_inputs)
            self.run_openpose()

            # 얘는 가장 마지막에
            # self._save_openpos_json(acgpn_inputs)
            pk = acgpn_inputs.id
            print(pk)
            return redirect('check', pk)
        return redirect('home')

    def avatar_warping_mask(self, inputs, acgpn_inputs):
        avatar_img = Image.open(inputs.avatar)

        # human parser script %% /home/park/human_parser/human-parser/
        tmp_path = os.getenv('HOME') + '/Desktop/otesbro/otesbro/otes/utils/tmp'
        # path = os.getenv('HOME') + '/human_parser/human-parser/' # human-parser 에 직접 저장 중.
        # input_path = path + 'inputs'
        # output_path = path + 'outputs'
        # model_root = path + 'checkpoints/exp-schp-201908261155-lip.pth' #test
        avatar_img = avatar_img.resize((192, 256))
        # avatar img save for human parse  %% /home/park/human_parser/human-parser/inputs/avatar.png
        avatar_img.save(os.path.join(tmp_path, 'avatar_in.png')) # tmp/avatar_in.png
        time.sleep(0.5)

        # 3d model segmentation
        print('Avatar Segmentation Start')
        # human_parser_run(model_root, input_path, output_path)  ##TODO
        # 파일 실행 경로를 human 으로 바꿔야?
        human_parser_run_script()
        time.sleep(0.5)

        # 3d model up-clothes mask
        # human-parser/outputs/avatar.png ==> ACGPN/Data_preprocessing/test_warped_mask/model_cut.png
        print('Avatar Mask Start')
        mask_path = mask_3d_255(os.path.join(tmp_path, 'avatar_out.png'))

        # model save (3d avatar mask)
        img = Image.open(mask_path)
        byteIO = BytesIO()
        img.save(byteIO, "png")
        byteIO.seek(0)
        warping_mask = InMemoryUploadedFile(byteIO, None, 'warp_mask.png', 'image/png', len(byteIO.getvalue()), None)
        acgpn_inputs.warping_mask = warping_mask
        acgpn_inputs.save()

    def human_model_segmentation(self, inputs, acgpn_inputs):
        human_img = Image.open(inputs.human_model)

        # human parser script %% /home/park/human_parser/human-parser/
        path = os.getenv('HOME') + '/human_parser/human-parser/'

        # path = os.getenv('HOME') + '/Desktop/otesbro/otes/human_parser/' # TODO : fix to another server
        # model_root = path + 'checkpoints/exp-schp-201908261155-lip.pth'
        input_path = path + 'inputs'
        output_path = path + 'outputs'
        human_img = human_img.resize((192, 256))

        # human image save for human-parse
        human_img.save(os.path.join(input_path, 'real_cut.png'))  # 해보고 안되면, 여기를 jpg로..

        # save for acgpn
        ####### png 로 저장 ? test 중
        acgpn_path = os.getenv('HOME') + '/Desktop/otesbro/otesbro/otes/ACGPN/DeepFashion_Try_On/Data_preprocessing/test_img/'
        human_jpg_img = Image.open(inputs.human_model) # 새로 이미지 열었음.
        print('=======')
        name = acgpn_path + "real_cut.jpg"
        human_jpg_img = human_jpg_img.resize((192, 256))
        human_jpg_img = human_jpg_img.convert('RGB') # png 저장 안된다 해 jpg로 저장해보려함.
        human_jpg_img.save(name)
        ####### png 저장 후 jpg 로 이름만 바꿈
        # os.rename(acgpn_path+'real_cut.png', acgpn_path+'real_cut.jpg')
        ########
        time.sleep(0.5)

        # instance save (human model)
        byteIO = BytesIO()
        human_img.save(byteIO, "png")  # img : resized 계속 열려있으므로 저장 가능
        byteIO.seek(0)
        human_model = InMemoryUploadedFile(byteIO, None, 'human_model.jpg', 'image/png', len(byteIO.getvalue()), None)
        acgpn_inputs.human_model = human_model
        acgpn_inputs.save()

        # 3d model segmentation => save image in human_parser/outputs/real_cut.png
        print('Human model Segmentation Start')
        human_parser_run_script()
        # human_parser_run(model_root, input_path, output_path)  # TODO
        time.sleep(0.5)

        # load image in human parser output & save ACGPN/Data../test_label/real_cut.png
        acgpn_path = os.getenv('HOME') + '/Desktop/otesbro/otesbro/otes/ACGPN/DeepFashion_Try_On/Data_preprocessing/test_label/'
        name = acgpn_path + "real_cut.png"
        path = os.path.join(output_path, 'real_cut.png') # human parse output  에서 가져옴
        img = Image.open(path)
        img.save(name)  # ACGPN -> test_label/real_cut.png

        # instance save (human segmentation)
        byteIO = BytesIO()
        img.save(byteIO, "png")  # img : resized 계속 열려있으므로 저장 가능
        byteIO.seek(0)
        segmentation = InMemoryUploadedFile(byteIO, None, 'human_segmentation.png', 'image/png', len(byteIO.getvalue()), None)
        acgpn_inputs.human_segment = segmentation
        acgpn_inputs.save()

    def target_nukkiNmask(self, inputs, acgpn_inputs):
        # NUKKI START
        print('Nukki Start')
        target = inputs.target
        tmp_path = os.getenv('HOME') + '/Desktop/otesbro/otesbro/otes/utils/tmp'
        input_path = os.path.join(tmp_path, 'input.{}'.format(target.name.split('.')[1]))
        output_path = os.path.join(tmp_path, 'output.png')

        # target image save for nukki
        img = Image.open(target)
        # if target.name.split('.')[1] == 'jpg':
        #     pass
        img.save(input_path)

        # background remove and save => tmp/output.png
        remover(input_path, output_path)
        time.sleep(0.5)

        # convert png to jpg and resize (196,256)
        im = Image.open(output_path)  # 누끼딴 것 tmp 에서 결과물 엶.
        im = im.resize((192, 256))

        # save ACGPN dataset & model
        acgpn_path = os.getenv('HOME') + '/Desktop/otesbro/otesbro/otes/ACGPN/DeepFashion_Try_On/Data_preprocessing/test_color/'
        byteIO = BytesIO()
        im.save(byteIO, "png")
        byteIO.seek(0)
        name = acgpn_path + 'train.png'  # 그걸 다시 ACGPN 에 저장
        im.save(name)

        # instance save (nukki)
        byteIO = BytesIO()
        im.save(byteIO, "png")
        byteIO.seek(0)
        nukki = InMemoryUploadedFile(byteIO, None, 'nukki.jpg', 'image/png', len(byteIO.getvalue()), None)
        acgpn_inputs.nukki = nukki
        acgpn_inputs.save()
        # NUKKI END

        # NUKKI MASK START
        print('Nukki Mask Start')
        nukki_acgpn_path = os.getenv('HOME') + '/Desktop/otesbro/otesbro/otes/ACGPN/DeepFashion_Try_On/Data_preprocessing/'
        nukki_img_path = nukki_acgpn_path + 'test_color/train.png'
        nukki_mask_path = nukki_acgpn_path + 'test_edge/train.png'

        # make mask and save ACGPN/Data../test_dege/train.jpg
        edge_255(nukki_img_path, nukki_mask_path)  # test_color 에 저장된 이미지의 edge를 따서 test_edge에 저장
        time.sleep(0.5)

        # mask model save (nukki mask)
        mask_img = Image.open(nukki_mask_path) # test_edge의 사진을 가져옴
        byteIO = BytesIO()
        mask_img.save(byteIO, "png")
        byteIO.seek(0)
        nukki_mask = InMemoryUploadedFile(byteIO, None, 'nukki_mask.jpg', 'image/png', len(byteIO.getvalue()), None)
        acgpn_inputs.nukki_mask = nukki_mask
        acgpn_inputs.save()

    def run_openpose(self):
        # save current working dir
        cwd = os.getcwd()

        # path
        openpose_wd = os.getenv('HOME') + '/Desktop/openpose'
        image_path = os.getenv('HOME') + '/Desktop/otesbro/otesbro/otes/ACGPN/DeepFashion_Try_On/Data_preprocessing/test_img/'
        output_path = os.getenv('HOME') + '/Desktop/otesbro/otesbro/otes/ACGPN/DeepFashion_Try_On/Data_preprocessing/test_pose/'

        # change working dir to openpose
        os.chdir(openpose_wd)
        # run openpose
        command = './build/examples/openpose/openpose.bin --image_dir {} --model_pose COCO --write_json {} --display 0 --render_pose 0'.format(
            image_path, output_path
        )
        os.system(command)

        # change working dir origin
        os.chdir(cwd)


def _save_openpos_json(acgpn_inputs):
    output_path = os.getenv('HOME') + '/Desktop/otesbro/otesbro/otes/ACGPN/DeepFashion_Try_On/Data_preprocessing/test_pose/'
    key_points_path = output_path + 'real_cut_keypoints.json'
    with open(key_points_path, "r") as key_points_json:
        tmp = json.load(key_points_json)
        acgpn_inputs.pose = tmp
        acgpn_inputs.save()


def run_acgpn(request, pk):
    acgpn_inputs = AcgpnInputs.objects.get(id=pk)

    # save json pose
    _save_openpos_json(acgpn_inputs)

    # run acgpn
    cwd = os.getcwd()
    acgpn_test_path = os.getenv('HOME') + '/Desktop/otesbro/otesbro/otes/ACGPN/DeepFashion_Try_On/ACGPN_inference'
    os.chdir(acgpn_test_path)
    print(os.getcwd())
    interpreter = sys.executable
    if os.path.isfile('.DS_Store'):
        print('DELETE_DS')
        os.remove('.DS_Store')

    command = '{} test.py'.format(interpreter)
    # command = '{} test.py'.format(os.system('/home/ubuntu/anaconda3/envs/otesbro/bin/python3.6'))
    subprocess.call(command, shell=True)
    print('-==================-')
    os.chdir(cwd)

    # result image save
    inputs = acgpn_inputs.reference_input
    output_instance = Outputs.objects.create(reference_input=inputs)
    print(output_instance)
    result_img = Image.open(acgpn_test_path + '/sample/real_cut.jpg')
    byteIO = BytesIO()
    result_img.save(byteIO, "JPEG")
    byteIO.seek(0)
    result = InMemoryUploadedFile(byteIO, None, 'result.jpg', 'image/jpeg', len(byteIO.getvalue()), None)
    output_instance.output = result
    output_instance.save()
    return redirect('output_check', output_instance.pk)

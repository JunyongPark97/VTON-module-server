import os
import json
import sys
from io import BytesIO

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import transaction
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

            pk = acgpn_inputs.id
            return redirect('check', pk)
        return redirect('home')

    def avatar_warping_mask(self, inputs, acgpn_inputs):

        parser_path = os.path.join(os.getenv('HOME'), 'human_parser', 'human-parser')
        parser_inputs_path = os.path.join(parser_path, 'inputs', 'avatar_in1.png')
        parser_output_path = os.path.join(parser_path, 'outputs', 'avatar_in1.png')

        # avatar 사진 Input 열기
        avatar_img = Image.open(inputs.avatar)
        avatar_img = avatar_img.resize((192, 256))
        avatar_img.save(parser_inputs_path)  # inputs/avatar_in.png
        time.sleep(0.5)

        # 3d mask parse
        human_parser_run_script()
        time.sleep(1.5)

        # 3d model up-clothes mask
        tmp_avatar_path = os.path.join(os.getenv('HOME'), 'OTesbro', 'otesbro', 'otes', 'utils', 'tmp', 'avatar')
        mask_path = mask_3d_255(img_root=parser_output_path, save_path=(tmp_avatar_path + '/mask_re.png'))

        # model save (3d avatar mask)
        img = Image.open(mask_path)
        byteIO = BytesIO()
        img.save(byteIO, "png")
        byteIO.seek(0)
        warping_mask = InMemoryUploadedFile(byteIO, None, 'warp_mask.png', 'image/png', len(byteIO.getvalue()), None)
        acgpn_inputs.warping_mask = warping_mask
        acgpn_inputs.save()

    def human_model_segmentation(self, inputs, acgpn_inputs):

        # tmp save for acgpn (원본 이미지 jpg 로 저장)
        tmp_human_path = os.path.join(os.getenv('HOME'), 'OTesbro', 'otesbro', 'otes', 'utils', 'tmp', 'human_model')
        human_jpg_img = Image.open(inputs.human_model) # 새로 이미지 열었음.
        test_img_name = tmp_human_path + "/model_re.jpg"
        # ADDED
        test_png_img_name = tmp_human_path + "/model_re.png"
        human_jpg_img = human_jpg_img.resize((192, 256))
        human_jpg_img = human_jpg_img.convert('RGB') # png 저장 안된다 해 jpg로 저장해보려함.
        human_jpg_img.save(test_img_name)
        time.sleep(0.5)


        # NUKKI START
        # background remove and save => tmp/human_model/model_re.png
        remover(test_img_name, test_png_img_name)
        time.sleep(0.5)

        # instance save (human model PNG)
        human_png_img = Image.open(test_png_img_name)
        byteIO = BytesIO()
        human_png_img.save(byteIO, "png")  # img : resized 계속 열려있으므로 저장 가능
        byteIO.seek(0)
        human_model = InMemoryUploadedFile(byteIO, None, 'human_model.png', 'image/png', len(byteIO.getvalue()), None)
        acgpn_inputs.human_model = human_model
        acgpn_inputs.save()

        # # instance save (human model) JPG
        # byteIO = BytesIO()
        # human_jpg_img.save(byteIO, "JPEG")  # img : resized 계속 열려있으므로 저장 가능
        # byteIO.seek(0)
        # human_model = InMemoryUploadedFile(byteIO, None, 'human_model.jpg', 'image/jpeg', len(byteIO.getvalue()), None)
        # acgpn_inputs.human_model = human_model
        # acgpn_inputs.save()

        #
        # human-parser path
        parser_path = os.path.join(os.getenv('HOME'), 'human_parser', 'human-parser')
        parser_inputs_path = os.path.join(parser_path, 'inputs', 'real_cut.png')
        parser_output_path = os.path.join(parser_path, 'outputs', 'real_cut.png')

        # human model parser
        human_img = Image.open(inputs.human_model)
        human_img = human_img.resize((192, 256))
        human_img.save(os.path.join(parser_inputs_path))

        # human mask parse
        human_parser_run_script()
        time.sleep(1.5)

        path = os.path.join(parser_output_path)  # human parse output 에서 가져옴
        img = Image.open(path)
        test_label_name = tmp_human_path + "/real_cut.png"
        img.save(test_label_name)

        # instance save (human segmentation)
        byteIO = BytesIO()
        img.save(byteIO, "png")  # img : resized 계속 열려있으므로 저장 가능
        byteIO.seek(0)
        segmentation = InMemoryUploadedFile(byteIO, None, 'human_segmentation.png', 'image/png', len(byteIO.getvalue()), None)
        acgpn_inputs.human_segment = segmentation
        acgpn_inputs.save()

    def target_nukkiNmask(self, inputs, acgpn_inputs):

        # NUKKI START
        target = inputs.target
        tmp_target_path = os.path.join(os.getenv('HOME'), 'OTesbro', 'otesbro', 'otes', 'utils', 'tmp', 'target')
        nukki_input_path = os.path.join(tmp_target_path, 'input.{}'.format(target.name.split('.')[1]))
        nukki_output_path = os.path.join(tmp_target_path, 'output.png')

        # target image save for nukki
        img = Image.open(target)
        img.save(nukki_input_path)

        # background remove and save => tmp/target/output.png
        remover(nukki_input_path, nukki_output_path)
        time.sleep(0.5)

        # convert png to jpg and resize (196,256)
        im = Image.open(nukki_output_path)
        im = im.resize((192, 256))
        byteIO = BytesIO()
        im.save(byteIO, "png")
        byteIO.seek(0)
        nukki = InMemoryUploadedFile(byteIO, None, 'nukki.jpg', 'image/png', len(byteIO.getvalue()), None)
        acgpn_inputs.nukki = nukki
        acgpn_inputs.save()

        # tmp/target/train.png 로 저장
        test_color_name = tmp_target_path + '/train.png'
        im.save(test_color_name)
        # NUKKI END

        # NUKKI MASK START
        test_edge_path = tmp_target_path + '/train_edge.png'

        edge_255(img_root=test_color_name, output_path=test_edge_path)
        time.sleep(0.5)

        # mask model save (nukki mask)
        mask_img = Image.open(test_edge_path)  # test_edge의 사진을 가져옴
        byteIO = BytesIO()
        mask_img.save(byteIO, "png")
        byteIO.seek(0)
        nukki_mask = InMemoryUploadedFile(byteIO, None, 'nukki_mask.jpg', 'image/png', len(byteIO.getvalue()), None)
        acgpn_inputs.nukki_mask = nukki_mask
        acgpn_inputs.save()

    def run_openpose(self):
        openpose_command_path = os.path.join(os.getenv('HOME'), 'OTesbro', 'otesbro', 'otes', 'utils', 'openpose_cmd')
        input_file_transfer_cmd = openpose_command_path + '/input_file_transfer.sh'
        output_file_transfer_cmd = openpose_command_path + '/output_file_transfer.sh'

        # file transfer human -> park (openpose inputs)
        os.system('bash {}'.format(input_file_transfer_cmd))
        time.sleep(0.5)

        # save current working dir
        cwd = os.getcwd()
        park_path = '/home/park/Desktop/openpose'
        os.chdir(park_path)

        # run openpose
        run_openpose_cmd = park_path + '/run_openpose.sh'
        os.system('bash {}'.format(run_openpose_cmd))
        time.sleep(0.5)
        # change working dir origin
        os.chdir(cwd)

        # output file transfer park -> human
        # 만약 안되면 chdir 하기 전에 해보자.
        os.system('bash {}'.format(output_file_transfer_cmd))
        time.sleep(0.5)

        return True

def _save_openpose_json(acgpn_inputs):
    tmp_keypoints_path = os.path.join(os.getenv('HOME'), 'OTesbro', 'otesbro', 'otes', 'utils', 'tmp', 'human_model')
    key_points_path = tmp_keypoints_path + '/model_re_keypoints.json'
    with open(key_points_path, "r") as key_points_json:
        tmp = json.load(key_points_json)
        acgpn_inputs.pose = tmp
        acgpn_inputs.save()
    return True

def run_acgpn(request, pk):
    acgpn_inputs = AcgpnInputs.objects.get(id=pk)
    
    # save json pose
    _save_openpose_json(acgpn_inputs)

    # file transfer tmp -> ACGPN/Data_preprocessing
    acgpn_command_path = os.path.join(os.getenv('HOME'), 'OTesbro', 'otesbro', 'otes', 'utils', 'acgpn_cmd')
    acgpn_file_transfer_cmd = acgpn_command_path + '/acgpn_file_transfer.sh'
    os.system('bash {}'.format(acgpn_file_transfer_cmd))

    # run acgpn
    cwd = os.getcwd()
    acgpn_test_path = os.getenv('HOME') + '/ACGPN/DeepFashion_Try_On/ACGPN_inference'
    os.chdir(acgpn_test_path)

    if os.path.isfile('.DS_Store'):
        os.remove('.DS_Store')

    interpreter = '/home/human/anaconda3/envs/acgpn/bin/python'
    command = '{} test.py'.format(interpreter)
    subprocess.call(command, shell=True)
    os.chdir(cwd)

    # result image save
    inputs = acgpn_inputs.reference_input
    output_instance = Outputs.objects.create(reference_input=inputs)
    result_img = Image.open(acgpn_test_path + '/sample/model_re.jpg')
    byteIO = BytesIO()
    result_img.save(byteIO, "JPEG")
    byteIO.seek(0)
    result = InMemoryUploadedFile(byteIO, None, 'result.jpg', 'image/jpeg', len(byteIO.getvalue()), None)
    output_instance.output = result
    output_instance.save()
    return redirect('output_check', output_instance.pk)

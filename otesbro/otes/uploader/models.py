from django.db import models
from PIL import Image


from uploader.others import img_directory_path_input_target, img_directory_path_input_human, \
    img_directory_path_input_avatar, img_directory_path_acgpn_input_nukki, img_directory_path_acgpn_input_nukki_mask, \
    img_directory_path_acgpn_input_warping_mask, img_directory_path_acgpn_input_human_model, \
    img_directory_path_acgpn_input_human_segment, img_directory_path_acgpn_output_image


class InputImages(models.Model):
    """
    인풋 이미지들은 192, 256으로 맞출 필요 x
    비율만 맞춰주세요.

    단, 아바타와 human 은 상의 위치를 맞춰야 합니다.
    """
    target = models.ImageField(upload_to=img_directory_path_input_target)
    human_model = models.ImageField(upload_to=img_directory_path_input_human)
    avatar = models.ImageField(upload_to=img_directory_path_input_avatar, help_text='3d modeling avatar 전체 이미지')
    description = models.TextField(default='', help_text='Test의 목적을 적어주세요.')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.validate_image()
        super(InputImages, self).save(*args, **kwargs)

    def validate_image(self):
        if self.avatar:
            img = Image.open(self.avatar)
            w, h = img.size
            ratio = float(w)/float(h)
            if abs(ratio - 0.75) > 0.1:
                raise Exception('비율맞춰주세요 ratio not acceptable')
        if self.target:
            img = Image.open(self.target)
            w, h = img.size
            ratio = float(w)/float(h)
            if abs(ratio - 0.75) > 0.1:
                raise Exception('비율맞춰주세요 ratio not acceptable')
        if self.human_model:
            img = Image.open(self.human_model)
            w, h = img.size
            ratio = float(w)/float(h)
            if abs(ratio - 0.75) > 0.1:
                raise Exception('비율맞춰주세요 ratio not acceptable')


class AcgpnInputs(models.Model):
    reference_input = models.ForeignKey(InputImages, on_delete=models.CASCADE, related_name='acgpn_inputs')
    nukki = models.ImageField(upload_to=img_directory_path_acgpn_input_nukki, null=True, blank=True)
    nukki_mask = models.ImageField(upload_to=img_directory_path_acgpn_input_nukki_mask, null=True, blank=True)
    warping_mask = models.ImageField(upload_to=img_directory_path_acgpn_input_warping_mask, help_text='warped 3d mask', null=True, blank=True)
    human_model = models.ImageField(upload_to=img_directory_path_acgpn_input_human_model, null=True, blank=True)
    pose = models.JSONField(null=True, blank=True)
    human_segment = models.ImageField(upload_to=img_directory_path_acgpn_input_human_segment, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Outputs(models.Model):
    reference_input = models.ForeignKey(InputImages, on_delete=models.CASCADE, related_name='acgpn_outputs')
    output = models.ImageField(upload_to=img_directory_path_acgpn_output_image)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


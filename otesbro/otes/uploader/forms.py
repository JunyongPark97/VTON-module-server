from django import forms
from PIL import Image
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from uploader.models import InputImages


class InputImageUploadForm(forms.ModelForm):

    class Meta:
        model = InputImages
        fields = ['target', 'human_model', 'avatar', 'description']

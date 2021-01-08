from django.contrib import admin
from django.utils.safestring import mark_safe

from uploader.models import InputImages, AcgpnInputs, Outputs


class InputImagesAdmin(admin.ModelAdmin):
    list_display = ['id', 'target_img', 'human_model_img', 'avatar_img', 'created_at']
    list_per_page = 50

    def target_img(self, obj):
        if not obj.target:
            return '-'
        return mark_safe('<img src="%s" width=120px "/>' % obj.target.url)
    target_img.short_description = 'target image'

    def human_model_img(self, obj):
        if not obj.human_model:
            return '-'
        return mark_safe('<img src="%s" width=120px "/>' % obj.human_model.url)
    human_model_img.short_description = 'human image'

    def avatar_img(self, obj):
        if not obj.avatar:
            return '-'
        return mark_safe('<img src="%s" width=120px "/>' % obj.avatar.url)
    avatar_img.short_description = 'avatar image'


class ACGPNInputsAdmin(admin.ModelAdmin):
    list_display = ['id', 'reference_input', 'nukki_img', 'nukki_mask_img', 'warping_mask_img',
                    'human_model_img', 'human_segment_img', 'created_at']
    list_per_page = 50

    def nukki_img(self, obj):
        if not obj.nukki:
            return '-'
        return mark_safe('<img src="%s" width=120px "/>' % obj.nukki.url)
    nukki_img.short_description = '누끼'

    def nukki_mask_img(self, obj):
        if not obj.nukki_mask:
            return '-'
        return mark_safe('<img src="%s" width=120px "/>' % obj.nukki_mask.url)
    nukki_mask_img.short_description = '누끼 mask'

    def warping_mask_img(self, obj):
        if not obj.warping_mask:
            return '-'
        return mark_safe('<img src="%s" width=120px "/>' % obj.warping_mask.url)
    warping_mask_img.short_description = '워핑마스크'

    def human_model_img(self, obj):
        if not obj.human_model:
            return '-'
        return mark_safe('<img src="%s" width=120px "/>' % obj.human_model.url)
    human_model_img.short_description = '입힐 사람 이미지'

    def human_segment_img(self, obj):
        if not obj.human_segment:
            return '-'
        return mark_safe('<img src="%s" width=120px "/>' % obj.human_segment.url)
    human_segment_img.short_description = '입힐 사람 segmentation'


class OutputsAdmin(admin.ModelAdmin):
    list_display = ['id', 'reference_input', 'output_img']
    list_per_page = 50

    def output_img(self, obj):
        if not obj.output:
            return '-'
        return mark_safe('<img src="%s" width=120px "/>' % obj.output.url)
    output_img.short_description = '결과'


admin.site.register(InputImages, InputImagesAdmin)
admin.site.register(AcgpnInputs, ACGPNInputsAdmin)
admin.site.register(Outputs, OutputsAdmin)

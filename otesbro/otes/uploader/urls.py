from django.urls import path, include
from rest_framework.routers import SimpleRouter

from uploader import views
from uploader.views import InputImageUploadView, CheckACGPNInputsView, CheckACGPNOutputsView

urlpatterns = [
    path('', InputImageUploadView.as_view(), name='home'),
    path('<int:pk>', CheckACGPNInputsView.as_view(), name='check'),
    path('output/<int:pk>', CheckACGPNOutputsView.as_view(), name='output_check'),
    path('acgpn/<int:pk>', views.run_acgpn, name='run_acgpn'),
]
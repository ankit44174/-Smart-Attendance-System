from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('upload/',UploadVideoView.as_view(), name='upload_video'),
    path('recognized-faces/', RecognizedFacesView.as_view(),name='recognized_faces'),
]

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from apps.user.views import *

urlpatterns = [
    path('auth/register/', RegisterUserAPIView.as_view()),
    path('auth/login/', LoginAPIView.as_view()),
    path('auth/logout/', LogoutAPIView.as_view()),
    path('auth/refresh-token/', TokenRefreshView.as_view()),
    path('auth/google-login/', GoogleLoginApi.as_view()),
    path('verification-email/<str:email>/<str:email_type>/', VerificationEmailAPIView.as_view()),
    path('restore-password/', RestorePasswordAPIView.as_view()),  # forgot password flow
    path('change-password/', ChangePasswordAPIView.as_view()),  # will be used from profile page
    path('profile/update/', UpdateUserAPIView.as_view()),
    path('profile/destroy/', RetrieveDestroyUserAPIView.as_view()),
    path('profile/retrive/', RetrieveDestroyUserAPIView.as_view()),
    path('profile/activate/', ActivateUserAPIView.as_view()),
    path('setup-job-settings/', UserJobSettingsSetupAPIView.as_view()),
    path('setup-job-search-filters/', SetupJobSearchFiltersAPIView.as_view()),
    path('change-default-resume/<int:resume_id>/', ChangeDefaultResumeAPIView.as_view()),

]

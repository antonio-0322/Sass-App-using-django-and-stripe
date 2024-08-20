
from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveDestroyAPIView, UpdateAPIView, \
    get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenViewBase

from apps.job_applying.decorators import active_plan_requires
from apps.core.decorators import validate_request_params
from apps.core.exceptions import BaseNotFoundError, BaseAPIException
from apps.payment.utils import user_subscribes_to_free_plan
from apps.user.enums import EmailType
from apps.user.mixins import RetrieveUserByEmailMixin
from apps.user.serializers import *
from apps.user.services import GoogleLoginService
from apps.user.utils import send_verification_email, create_verification_code


class RegisterUserAPIView(CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)


class UpdateUserAPIView(UpdateAPIView):
    serializer_class = UpdateUserDetailsSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return User.objects.filter(pk=self.request.user.pk).get()


class RetrieveDestroyUserAPIView(RetrieveDestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return User.objects.filter(pk=self.request.user.pk).get()

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data

        if not instance.is_welcome_said:
            instance.is_welcome_said = True
            instance.save()

        return Response(data)


class LoginAPIView(TokenViewBase):
    """
    Takes a set of user credentials and returns an access and refresh JSON web
    token pair to prove the authentication of those credentials.
    """
    serializer_class = TokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.filter(email=request.data['email']).first()
        if not user.has_used_free_subscription:

            user_subscribes_to_free_plan(user=user)

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class VerificationEmailAPIView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, email, email_type: EmailType):
        """
           API endpoint for sending a verification email to a user.
           Parameters:
               email: The email address of the user to whom the verification email will be sent.
               email_type (EmailType) : The email type which should be sent
           Returns:
               Returns a 204 No Content response if the verification email is sent successfully.
           Permission:
               This API endpoint allows access to all users (no authentication required).
           Raises:
               Raises a BaseNotFoundError if no user with the provided email address is found.
       """
        user = User.objects.filter(email=email).first()
        if not user:
            raise BaseNotFoundError(detail="User with such email doesn't exist")
        if not (email_type in [e.value for e in EmailType]):
            raise BaseValidationError(detail="Unknown email type")

        if email_type == EmailType.ACTIVATE_ACCOUNT.value and user.is_active:
            raise BaseAPIException("This account has already been activated.")

        if user.signup_type == 'google' and email_type == EmailType.RESET_PASSWORD.value:
            raise BaseAPIException("This account created by google account and password can't be changed.")

        send_verification_email(
            user=user,
            code=create_verification_code(email=user.email),
            email_type=email_type,
        )

        return Response(status=status.HTTP_204_NO_CONTENT)


class RestorePasswordAPIView(RetrieveUserByEmailMixin, UpdateAPIView):
    serializer_class = RestorePasswordSerializer
    permission_classes = (AllowAny,)


class ChangePasswordAPIView(UpdateAPIView):
    serializer_class = ChangePasswordSerializer

    def get_object(self):
        return self.request.user


class ActivateUserAPIView(APIView):
    """
        View to activate a user account.
        Patch endpoint for activating a user by providing a verification code and email.
        Request Body:
        {
            "code": "string",
            "email": "string"
        }

        Response:
        Status Code 204 - No Content

        Error Responses:
        Status Code 404 - If such user doesn't exist, or code is wrong
        Status Code 405 - If user already has been activated
        Status Code 400 - If code already has been expired
        """

    serializer_class = ActivateUserSerializer
    permission_classes = (AllowAny,)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        serializer.update(instance=instance, validated_data=serializer.validated_data)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_object(self):
        user = User.objects.filter(email=self.request.data['email']).first()
        if not user:
            raise BaseValidationError("User with this email doesn't exist.", code=404)
        if user.is_active:
            raise BaseValidationError("This user is already active.", code=405)
        return user


class LogoutAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    @validate_request_params(serializer_class=LogoutSerializer)
    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class GoogleLoginApi(APIView):
    permission_classes = (AllowAny, )

    def post(self, request, *args, **kwargs):
        serializer = GoogleLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.data
        code = validated_data.get('code')
        google_login_service = GoogleLoginService()
        access_token = google_login_service.retrieve_access_token_by_code(
            code=code,
            redirect_uri=validated_data['redirect_url']
        )

        user, created = google_login_service.get_or_create_user_from_id_token(access_token['id_token'])

        if created:
            user_subscribes_to_free_plan(user=user)

        if not user.is_active:
            user.is_active = True
            user.save()

        token = RefreshToken.for_user(user)  # generate token without username & password

        return Response({
            "access": str(token.access_token),
            "refresh": str(token)
        })


class UserJobSettingsSetupAPIView(CreateAPIView):
    serializer_class = UserSetupJobSettingsSerializer

    @active_plan_requires
    def post(self, request, *args, **kwargs):
        user = request.user

        serializer = self.serializer_class(data={
            "user": user,
            **request.data
        }, instance=user)

        serializer.is_valid(raise_exception=True)

        serializer.save(serializer.validated_data)

        return Response(status=status.HTTP_201_CREATED)


class ChangeDefaultResumeAPIView(APIView):
    """
        API view for changing the user's default resume selection.
        This view allows a user to change their default resume selection by specifying the
        resume ID. The selected resume becomes the default one associated with the user's profile.
        """
    def patch(self, request, resume_id):
        """
        Handle PATCH request to change the user's default resume selection.
        Args:
            request (HttpRequest): The HTTP request object containing user input data.
            resume_id (int): The ID of the resume to set as the default.
        Returns:
            Response: HTTP response indicating the status of the operation.
        """
        resume = get_object_or_404(UserResume, pk=resume_id, user=request.user)
        request.user.selected_resume = resume
        request.user.save()

        return Response(status=status.HTTP_206_PARTIAL_CONTENT)


class SetupJobSearchFiltersAPIView(CreateAPIView):
    """
        API view for setting up job search filters for a user's profile.
        This view allows a user to customize their job search filters by providing a list of
        filters and their corresponding values. It validates the provided data, considering the user's
        active subscription plan, and saves the filters to the user's profile.
    """
    serializer_class = UserSetupJobSearchFiltersSerializer

    @active_plan_requires
    def post(self, request):
        """
            Handle POST request to set up job search filters for the user's profile.
            Args:
                request (HttpRequest): The HTTP request object containing user input data.
            Returns:
                Response: HTTP response indicating the status of the operation.
        """
        user = request.user
        serializer = self.serializer_class(data={
            "user": user,
            **request.data
        }, instance=user)
        serializer.is_valid(raise_exception=True)

        serializer.save(serializer.validated_data)

        return Response(status=status.HTTP_201_CREATED)
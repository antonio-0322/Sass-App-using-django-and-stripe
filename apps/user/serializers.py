from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import update_last_login
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, AuthenticationFailed

from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainSerializer

from apps.core.exceptions import BaseValidationError, InActiveUser
from apps.core.serializers import Base64StringField
from apps.payment.serializers import SubscriptionSerializer
from apps.setup.enums import FieldType, FieldSlugs
from apps.setup.models import AdditionalQuestion, Field
from apps.setup.serializers import AdditionalQuestionSerializer
from apps.user.mixins import ValidatePasswordsMatchMixin, ValidatePasswordRulesMixin, ValidateCodeMixin
from apps.user.models import User, UserJobTitle, UserSkill, UserAdditionalQuestion, UserResume, UserJobSearchFilter
from apps.user.services import VectoriseUserInfo
from apps.user.utils import delete_all_verification_codes_for_user, verify_code


class UserAdditionalQuestionSerializer(serializers.ModelSerializer):
    additional_question_id = serializers.PrimaryKeyRelatedField(
        queryset=AdditionalQuestion.objects.all(),
        write_only=True
    )
    additional_question = AdditionalQuestionSerializer(read_only=True)

    def validate(self, attrs):
        q = attrs.get('additional_question_id')
        field = get_field_serializer(q)
        field.run_validation(attrs.get('values') if attrs.get('is_multiple') else attrs.get('value'))

        return attrs

    class Meta:
        model = UserAdditionalQuestion
        exclude = ('user',)


class UpdateUserDetailsSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=25)
    last_name = serializers.CharField(max_length=25)

    class Meta:
        model = User
        fields = ('first_name', 'last_name')


class RestorePasswordSerializer(ValidateCodeMixin, ValidatePasswordRulesMixin, ValidatePasswordsMatchMixin,
                                serializers.ModelSerializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=45, write_only=True, required=True)
    password = serializers.CharField(max_length=35, min_length=8, write_only=True)
    password_confirm = serializers.CharField(max_length=35, write_only=True)

    def update(self, instance, validated_data):
        instance.password = make_password(validated_data['password'])
        instance.save()
        delete_all_verification_codes_for_user(instance.email)

        return instance

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'password', 'code', 'password_confirm')


class ChangePasswordSerializer(ValidatePasswordRulesMixin, ValidatePasswordsMatchMixin, serializers.ModelSerializer):
    password = serializers.CharField(max_length=35, min_length=8, write_only=True)
    password_confirm = serializers.CharField(max_length=35, write_only=True)
    current_password = serializers.CharField(max_length=35, write_only=True)

    def update(self, instance, validated_data):
        instance.password = make_password(validated_data['password'])
        instance.save()

        return instance

    def validate_current_password(self, value):
        user = authenticate(username=self.instance.email, password=value)
        if not user:
            raise ValidationError("Current password is incorrect.")

        return value

    class Meta:
        model = User
        fields = ('password', 'password_confirm', 'current_password')


class ActivateUserSerializer(ValidateCodeMixin, serializers.Serializer):
    code = serializers.CharField(max_length=45, required=True)
    email = serializers.EmailField(required=True)

    def update(self, instance, validated_data):
        instance.is_active = True
        instance.save()

        delete_all_verification_codes_for_user(instance.email)

        return instance

    def validate(self, data):
        verify_code(data.get('email'), data.get('code'))

        data = super().validate(data)
        return data


class TokenObtainPairSerializer(TokenObtainSerializer):
    default_error_messages = {
        "no_active_account": "Invalid email address or password. Please try again."
    }

    def validate(self, attrs):
        user = User.objects.filter(email=attrs['email']).first()
        if user and not user.is_active:
            raise InActiveUser()

        data = super().validate(attrs)
        refresh = self.get_token(self.user)

        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)

        return data

    @classmethod
    def get_token(cls, user):
        return RefreshToken.for_user(user)

    class Meta:
        ref_name = "User 1"


class GetVerificationEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()


class GoogleLoginSerializer(serializers.Serializer):
    code = serializers.CharField(required=True)
    redirect_url = serializers.URLField(required=True)


class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()


class JobTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserJobTitle
        exclude = ('user',)


class UserSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSkill
        exclude = ('user',)


class UserResumesSerializer(serializers.ModelSerializer):
    file = Base64StringField(
        required=True,
        allow_null=False,
        max_size=2000,
        allowed_extensions=['pdf', 'docx']
    )

    class Meta:
        model = UserResume
        exclude = ('user',)


class UserSetupJobSettingsSerializer(serializers.ModelSerializer):
    skills = serializers.ListSerializer(child=UserSkillSerializer(), allow_empty=True)
    additional_questions = serializers.ListSerializer(child=UserAdditionalQuestionSerializer(), allow_empty=False)
    resumes = serializers.ListSerializer(child=UserResumesSerializer(), required=True)
    deleted_resumes = serializers.ListSerializer(child=serializers.IntegerField(), required=False, write_only=True)
    is_update = serializers.BooleanField(default=False)

    def validate_resumes(self, value):
        if not self.initial_data.get('is_update') and len(value) == 0:
            raise ValidationError("Upload at least 1 resume")

        return value

    def validate(self, attrs):
        data = super().validate(attrs)

        if self.instance.selected_resume and self.instance.selected_resume_id in attrs.get('deleted_resumes', []):
            raise BaseValidationError({"deleted_resumes": "Default resume can't be deleted"})

        return data

    class Meta:
        model = User
        fields = ('additional_questions', 'skills', 'resumes', 'deleted_resumes', 'is_update')

    @transaction.atomic
    def save(self, validated_data):
        self.instance.additional_questions.all().delete()
        self.instance.skills.all().delete()
        deleted_resumes = validated_data.pop('deleted_resumes', None)
        if deleted_resumes:
            self.instance.resumes.filter(pk__in=deleted_resumes).delete()

        self.instance.skills.bulk_create(UserSkill(**i, user=self.instance) for i in validated_data['skills'])

        self.instance.additional_questions.bulk_create(
            UserAdditionalQuestion(
                user=self.instance,
                additional_question_id=i['additional_question_id'].id,
                value=i.get('value'),
                values=i.get('values')
            ) for i in validated_data['additional_questions']
        )
        if len(validated_data.get('resumes', [])) > 0:
            for f in validated_data['resumes']:
                UserResume(user=self.instance, file=f['file'], display_name=f['display_name']).save()

        try:
            if not self.instance.selected_resume and len(self.instance.resumes.all()):
                self.instance.selected_resume = self.instance.resumes.all()[0]
                self.instance.save()
        except UserResume.DoesNotExist:
            self.instance.selected_resume = self.instance.resumes.first()
            self.instance.save()

        VectoriseUserInfo(user=self.instance).save_local()



class UserJobSearchSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        q = attrs.get('job_search_filter')
        field = get_field_serializer(q)
        field.run_validation(attrs.get('values') if attrs.get('is_multiple') else attrs.get('value'))

        return attrs

    class Meta:
        model = UserJobSearchFilter
        exclude = ('user',)


class UserSerializer(ValidatePasswordsMatchMixin, ValidatePasswordRulesMixin, serializers.ModelSerializer):
    password = serializers.CharField(max_length=35, write_only=True)
    password_confirm = serializers.CharField(max_length=35, write_only=True)
    first_name = serializers.CharField(max_length=25)
    last_name = serializers.CharField(max_length=25)
    active_subscription = SubscriptionSerializer(required=False, read_only=True)
    last_used_subscription = SubscriptionSerializer(required=False, read_only=True)
    additional_questions = serializers.ListSerializer(child=UserAdditionalQuestionSerializer(), read_only=True)
    job_titles = serializers.ListSerializer(child=JobTitleSerializer(), read_only=True)
    skills = serializers.ListSerializer(child=UserSkillSerializer(), read_only=True)
    resumes = serializers.ListSerializer(child=UserResumesSerializer(), read_only=True)
    job_search_filters = serializers.ListSerializer(child=UserJobSearchSerializer(), read_only=True)
    selected_resume = UserResumesSerializer(read_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'password',
            'first_name',
            'last_name',
            'password_confirm',
            'active_subscription',
            'last_used_subscription',
            'job_titles',
            'skills',
            'resumes',
            'additional_questions',
            'job_search_filters',
            'has_used_free_subscription',
            'selected_resume',
            "signup_type",
            "is_welcome_said"
        )

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        user.is_active = False
        user.save()
        return user


class UserSetupJobSearchFiltersSerializer(serializers.ModelSerializer):
    job_search_filters = serializers.ListSerializer(child=UserJobSearchSerializer())

    def validate(self, attrs):
        job_title_filter = next(
            item for item in attrs['job_search_filters'] if item["job_search_filter"].slug == FieldSlugs.JOB_TITLE
        )
        if not self.instance.active_subscription or len(
                job_title_filter['values']) > self.instance.active_subscription.total_job_titles:
            raise BaseValidationError({"job_titles": "Your plan doesn't allow add more job titles"})

        return attrs

    @transaction.atomic
    def save(self, validated_data):
        self.instance.job_search_filters.all().delete()
        self.instance.job_search_filters.bulk_create(
            UserJobSearchFilter(
                user=self.instance,
                job_search_filter=i['job_search_filter'],
                value=i.get('value'),
                values=i.get('values')
            ) for i in validated_data['job_search_filters']
        )

    class Meta:
        model = User
        fields = ('job_search_filters', )


def get_field_serializer(field: Field):
    if field.type == FieldType.INPUT:
        return serializers.CharField(max_length=300, required=field.is_required)
    choices = []
    if field.items:
        choices = [(item.get('value'), item.get('value')) for item in field.items]

        if not field.is_required:
            choices += [('', '')]

    if field.type in [FieldType.RADIO, FieldType.SELECT, FieldType.SWITCH_BUTTON]:
        return serializers.ChoiceField(
            choices=choices,
            required=field.is_required
        )
    if field.type in [FieldType.MULTI_SELECT, FieldType.CHECKBOX_GROUP]:
        return serializers.ListSerializer(child=serializers.ChoiceField(
            choices=choices,
            required=field.is_required
        ))

    if field.type == FieldType.NUMBER_INPUT:
        return serializers.IntegerField(required=field.is_required)

    if field.type == FieldType.MULTI_INPUT:
        return serializers.ListSerializer(
            child=serializers.CharField(),
            required=field.is_required, allow_empty=not field.is_required
        )

import base64
import json
import os

import requests
from django.conf import settings
from pydparser import ResumeParser
from langchain.text_splitter import CharacterTextSplitter
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from apps.job_applying.services.info_collector import UserInfoCollector
from apps.user.enums import SignupTypes
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from apps.user.models import User, UserResume, UserResumeParsed


class GoogleLoginService:
    ACCESS_TOKEN_OBTAIN_URL = 'https://oauth2.googleapis.com/token'

    def __init__(
            self,
            client_id: str = settings.GOOGLE_OAUTH2_CLIENT_ID,
            client_secret: str = settings.GOOGLE_OAUTH2_CLIENT_SECRET
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.http_client = requests.Session()
        self.user_model = User

    def retrieve_access_token_by_code(self, code: str, redirect_uri: str) -> dict:
        response = self.http_client.post(self.ACCESS_TOKEN_OBTAIN_URL, data={
            'code': code,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'
        })

        if not response.ok:
            raise AuthenticationFailed('Failed to obtain access token from Google.')

        return response.json()

    def get_user_info_from_id_token(self, id_token: str):
        parts = id_token.split(".")
        if len(parts) != 3:
            raise Exception("Incorrect id token format")

        payload = parts[1]
        padded = payload + '=' * (4 - len(payload) % 4)
        decoded = base64.b64decode(padded)
        return json.loads(decoded)

    def get_or_create_user_from_id_token(self, id_token: str):
        user_info = self.get_user_info_from_id_token(id_token)

        return self.user_model.objects.get_or_create(email=user_info['email'], defaults={
            "first_name": user_info.get('given_name', ''),
            "last_name": user_info.get('family_name', ''),
            "signup_type": SignupTypes.GOOGLE
        })


class ResumeParserService:
    def __init__(self, resume: UserResume):
        self.resume = resume
        self.temp_file_path = os.path.join(settings.BASE_DIR, 'uploads', self.resume.file.name)

    def get_parsed_data(self, file_path: str):
        return ResumeParser(file_path).get_extracted_data()

    def save_parsed_data(self):
        self.save_file_to_local()
        if not os.path.exists(self.temp_file_path):
            raise FileNotFoundError(f"File not found at {self.temp_file_path}")

        data = self.get_parsed_data(self.temp_file_path)
        try:
            user_data = self.resume.user.user_resume_parsed
        except UserResumeParsed.DoesNotExist:
            user_data =  UserResumeParsed(user=self.resume.user, data={})

        user_data.data.update({self.resume.file.name: data})
        user_data.save()

    def save_file_to_local(self):
        try:
            file = self.resume.file.file
        except FileNotFoundError:
            return

        with open(self.temp_file_path, 'wb') as f:
            f.write(file.read())

    def __del__(self):
        self.temp_file_path and os.remove(self.temp_file_path)

class VectoriseUserInfo:
    folder_path = os.path.join(settings.BASE_DIR, 'uploads', 'vectorStore', 'faiss')
    def __init__(self, user: User):
        self.user = user
        self.embedder = OpenAIEmbeddings()
        os.makedirs(os.path.dirname(self.folder_path), exist_ok=True)

    def save_local(self):
        user_info = UserInfoCollector(self.user).execute()
        texts = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        ).split_text(user_info)
        db = FAISS.from_texts(texts, self.embedder)
        db.save_local(self.folder_path, f'user_{self.user.id}')

    def load_local(self):
        try:
            db = FAISS.load_local(
                self.folder_path, self.embedder, f'user_{self.user.id}', allow_dangerous_deserialization=True
            )
        except:
            self.save_local()
            db = FAISS.load_local(
                self.folder_path, self.embedder, f'user_{self.user.id}', allow_dangerous_deserialization=True
            )

        return db
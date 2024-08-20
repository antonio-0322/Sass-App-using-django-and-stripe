import docx
from apps.core.exceptions import LogicException
from apps.user.models import User, UserResume
from PyPDF2 import PdfReader


class UserInfoCollector:
    def __init__(self, user: User):
        self.user = user

    def execute(self):
        if not self.user.selected_resume:
            raise LogicException("User doesn't have selected resume")

        info = self.get_identity_info()
        info += "Here is my resume. \n"
        info += self.resume_as_text()

        info += "\n\n" + self.additional_questions_as_text()
        info += "\n\n Here are my skills and experience in each skill"
        info += "\n \n" + self.skills_as_text()

        print(info)
        return info

    def resume_as_text(self) -> str:
        return ResumeReader(resume=self.user.selected_resume).read()

    def additional_questions_as_text(self) -> str:
        return  ("\n Here is additional information about me. \n"
                 + '\n'.join([f'{j.additional_question.title} - {j.value} ' for j in self.user.additional_questions.all()]))

    def skills_as_text(self) -> str:
        return '\n'.join([f'{s.name} - {s.experience_in_years} years' for s in self.user.skills.all()])

    def get_identity_info(self) -> str:
        return f"""
            First name: {self.user.first_name}, 
            Last name: {self.user.last_name},
            email: {self.user.email}, \n  
        """

class ResumeReader:
    def __init__(self, resume: UserResume):
        self.resume = resume

    def read(self):
        if self.resume.is_pdf:
            return self.read_pdf()

        if self.resume.is_docx:
            return self.read_docx()

        raise Exception("Unknown resume extension")

    def read_pdf(self):
        reader = PdfReader(self.resume.file.file)
        raw_text = ''
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                raw_text += text

        return raw_text

    def read_docx(self):
        doc = docx.Document(self.resume.file.file)
        raw_text = []
        for para in doc.paragraphs:
            raw_text.append(para.text)

        return '\n'.join(raw_text)


import logging
import re

# from langchain.chat_models import ChatOpenAI
# from langchain_community import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain_community.chat_models import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from apps.user.models import User
from apps.user.services import VectoriseUserInfo

class QAService:
    def __init__(self, user: User):
        self.user = user
        self.logger = logging.getLogger('job_applying')


    def get_answer(self, question, answer_options: list, output_type=None):
        doc_search = VectoriseUserInfo(self.user).load_local()
        template = PromptBuilder(answer_options=answer_options, output_type=output_type).get_prompt_template()
        prompt = PromptTemplate(
            template=template,
            input_variables=["question", "context"]
        )
        chain_type_kwargs = {"prompt": prompt}
        qa = RetrievalQA.from_chain_type(
             llm=ChatOpenAI(model="gpt-4", max_tokens=500, temperature=0),
             chain_type="stuff",
             retriever=doc_search.as_retriever(serch_type="similarity", search_kwargs={"k": 2}),
             chain_type_kwargs=chain_type_kwargs
        )
        answer = qa({"query": question})

        res =  self.normalize_answer(answer['result'])
        self.logger.info(f"AI answer: {res}")

        return res
        # with get_openai_callback() as cb:
        #     answer = load_qa_chain(self.open_ai, chain_type="stuff").run(
        #         input_documents=input_documents,
        #         question=query
        #     )
        #
        # return f'{answer}, total-tokens: {cb.total_tokens}, prompt-tokens: {cb.prompt_tokens}, completion-tokens: {cb.completion_tokens}, total-cost: {cb.total_cost}'
    @classmethod
    def normalize_answer(cls, answer: str):
        """
            This class method is used to normalize the answer received from the OpenAI API.
            Args:
                answer (str): The raw answer string received from the OpenAI API.
            Returns:
                str: The normalized answer string.
            """
        return re.sub(r"\[answer_start]|\[answer_end]|\[answer]|Answer:|-|NOOUTPUT|NO-INPUT|\\|\"", '', answer).strip()


class PromptBuilder:
    base_instructions = [
        "- Be laconic and precise",
        "- Don't provide any additional information",
        "- Return only value which is asked",
        "- You should give answer which will be pasted in the form field",
        "- If you don't know answer, just return the NO-INPUT."
        # "If you don't know answer, please think rationally answer from your own knowledge base, but not more than 2 sentences"
    ]
    def __init__(self, answer_options: list = None, output_type: str = None):
        self.answer_options = answer_options
        self.output_type = output_type
    def get_prompt_template(self):
        query = f""""
            [persona_begin]
              You are user which filling form for applying job.
              You look at the instructions section and apply all of them one by one for the final answer.
            [persona_end]
            [goal_begin]
              Provide an answer to the question based on the provided context.
            [goal_end]
            [instructions_begin]{self.make_instructions()}[instructions_end]
         """

        query += """
            [question_start]{question}[question_end]
            [context_start]{context}[context_end]"
            Answer:
        """


        return query

    def make_instructions(self):
        instructions = self.base_instructions

        if self.output_type == "number":
            instructions += ["- Provide an answer only in integer format.",
                             "- If you are not sure about the answer then see if I have any experience with closely related technologies.",
                             "- Example of closely related technologies: MySql & Postgresql, React & React native, Database & RDBMS",
                             "- If you don't know say 1"]

        if self.answer_options:
            opt = "[options_start]" + ", ".join(self.answer_options) + "[options_end]"
            instructions += [f'-Answer should be only one of this options: {opt}']
        return "\n\t\t\t" + "\n\t\t\t".join(instructions) + "\n\t\t\t"

# pull official base image
FROM python:3.11

# set work directory
WORKDIR /usr/src/app

# set environment variables
#ENV PYTHONDONTWRITEBYTECODE 1
#ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt/ ./requirements.txt
RUN pip install -r requirements.txt
RUN pip install uvicorn

# install spacy and nltk
RUN python -m spacy download en_core_web_sm
RUN python -m nltk.downloader words
RUN python -m nltk.downloader stopwords

# copy project
COPY . .
#ENTRYPOINT ["./docker-entrypoint.sh"]

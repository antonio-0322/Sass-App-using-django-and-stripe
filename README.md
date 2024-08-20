<div id="top"></div>
<h1 align="center">AutoSubmit</h1>

![Build Status](https://img.shields.io/badge/Status-Development-green)
![Python](https://img.shields.io/badge/python-v3.11-blue)
![Mysql](https://img.shields.io/badge/mysql-8.0.31-blue)
![Django](https://img.shields.io/badge/Django-4.2.2-blue)
![Django Rest Framework](https://img.shields.io/badge/Django%20Rest%20Framework-3.14.0-blue)

## About The Project

This application purpose is apply to job instead of users. In first stage will be implemented only Linkedin profile.
User will download Google Chrome extension which will automatically apply to jobs in Linkedin based on user built job 
search query and user setup resume. 
To answer questions during applying will be used OpenAI which will answer questions based on user provided information
(resume and additional questions answers). 

## Getting Started

Here's how you can set up a project and what you need to do for it. 
Create .env based on .env.example.

### Prerequisites

For running project, without docker you should have installed on your machine`

* Python 3.11
* Mysql 8.0.31



Here's instruction for installing and setting up the app step by step._

1. Clone the repo`
   ```shell
   git clone 
   ```

2. Move to the working directory, install and activate your virtualenv`
   ```shell
    cd /project_path 
   ```
   ```shell
    python -m venv yourVenvName
   ```
   ```shell
    source yourVenvName/bin/activate
   ```
### Installation without docker

3. For Mysql adapter you should install on your machine (Linux/Ubuntu)`
   ```shell
    sudo apt-get update
    sudo apt-get install libpq-dev
   ```
   ```shell
    sudo apt-get install python-dev
    OR
    sudo apt-get install python3-dev
   ```

4. Install requirements`
   ```shell
    pip install -r requirements.txt
   ```

5. Set your .env file and migrate`
   ```shell
    python manage.py migration
   ```

6. Collect static files`
   ```shell
    python manage.py collectstatic -y
   ```
7. Seed data needed for application properly work
   
   ```shell
    python manage.py seed_plans
    python manage.py sync_plans
    python manage.py seed_additional_questions
    python manage.py seed_linkedin_search_filters
   
   ```
   
7. Run`
   ```shell
    python manage.py runserver
   ```
### Installation with docker
1. Run`
   ```shell
    docker-compose up -d --build
   ```
<p align="center"><a href="#top">Back to top</a></p>

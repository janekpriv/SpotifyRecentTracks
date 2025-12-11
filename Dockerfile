FROM python:3.7.4

WORKDIR /flask-app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . /flask-app/

CMD python main.py
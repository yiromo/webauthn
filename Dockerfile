FROM python:3.9

WORKDIR /src

COPY requirements.txt .
COPY ./src ./src
COPY ./frontend/index.html ./src/static/index.html

RUN pip install -r requirements.txt

CMD ["python", "./src/main.py"]
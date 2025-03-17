FROM python:3.12

RUN mkdir /app

COPY requirements.txt /app

RUN python -m pip install --upgrade pip && pip3 install -r app/requirements.txt --no-cache-dir

COPY . /app

WORKDIR /app

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ]
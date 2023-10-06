FROM python:3.9

WORKDIR /code

RUN apt-get update && apt-get install -y \
    libasound-dev libportaudio2 libportaudiocpp0 portaudio19-dev

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]

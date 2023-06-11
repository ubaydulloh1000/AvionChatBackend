FROM python:3.8-slim-buster

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV HOME_DIR=/app
#RUN mkdir -p $HOME_DIR

WORKDIR $HOME_DIR

COPY requirements requirements

RUN pip install --upgrade pip
RUN pip install -r requirements/production.txt


RUN useradd app && usermod -aG app app

COPY . .

RUN chown -R app:app $HOME_DIR

USER app
RUN chmod a+x entrypoint.sh

#ENTRYPOINT ./entrypoint.sh

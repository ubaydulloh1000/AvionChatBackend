FROM python:3.10-bullseye

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV HOME_DIR=/home/app
RUN mkdir -p $HOME_DIR

WORKDIR $HOME_DIR

COPY requirements requirements

RUN pip install --upgrade pip
RUN pip install -r requirements/production.txt

RUN useradd app && usermod -aG app app


RUN chown -R app:app $HOME_DIR

COPY . .

RUN chown -R app:app $HOME_DIR
USER app

WORKDIR $HOME_DIR

RUN chmod +x entrypoint.sh
#ENTRYPOINT ["./entrypoint.sh"]

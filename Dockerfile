FROM python:3.12-rc-slim-buster

WORKDIR /app

COPY mailer_container.py /app

CMD ["python", "mailer_container.py"]
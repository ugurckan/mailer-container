FROM python:3.7
COPY mailer_container.py .
CMD ["python", "mailer_container.py"]
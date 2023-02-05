FROM python:3.10-alpine

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY circleci_env_cli.py .

ENTRYPOINT ["python", "circleci_env_cli.py"]

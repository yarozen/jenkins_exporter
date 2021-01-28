FROM python:3.8-alpine

LABEL maintainer="Yaniv Rozenboim yarozen@gmail.com"

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

WORKDIR /app
COPY jenkins_exporter.py /app

EXPOSE 9789

ENTRYPOINT ["python", "-u", "jenkins_exporter.py"]

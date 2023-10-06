# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.10.7-slim
EXPOSE 5000
# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

RUN apt-get update
RUN apt-get install -y nodejs npm

# Install pip requirements
COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt
# RUN pip install -U hrequests[all]


# install the musescore scraper
RUN npm install -g dl-librescore


WORKDIR /app
COPY . /app

RUN playwright install-deps

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app && chown -R appuser /usr/local/lib
USER appuser

RUN playwright install chromium
# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "--timeout", "0", "main:app"]


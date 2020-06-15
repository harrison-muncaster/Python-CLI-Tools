FROM python:3.8-alpine
COPY requirements.txt /
RUN pip install -r /requirements.txt
COPY cli /app/cli
COPY templates /app/templates
RUN mkdir /app/files
WORKDIR /app/cli
ENTRYPOINT [ "python3", "main.py" ]

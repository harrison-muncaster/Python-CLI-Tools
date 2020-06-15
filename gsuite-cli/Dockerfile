FROM python:3.8-alpine
COPY requirements.txt /
RUN pip install -r /requirements.txt
COPY disqo_cli /app/disqo_cli
COPY templates /app/templates
RUN mkdir /app/files
WORKDIR /app/disqo_cli
ENTRYPOINT [ "python3", "main.py" ]
FROM python:3.10

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

ENV PYTHONPATH="${PYTHONPATH}:/app"

COPY . /app

RUN python -m grpc_tools.protoc -Iproto --python_out=. --grpc_python_out=. proto/glossary.proto

CMD ["python", "server/server.py"]
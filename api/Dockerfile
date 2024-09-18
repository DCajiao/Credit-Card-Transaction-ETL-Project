FROM python:3.9

WORKDIR /api

COPY README.md /api
COPY requirements.txt /api
COPY src/ /api/

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python", "main.py"]
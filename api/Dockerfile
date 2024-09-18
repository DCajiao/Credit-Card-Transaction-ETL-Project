FROM python:3.9

WORKDIR /api

COPY README.md /api
COPY src/ /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python", "api.py"]
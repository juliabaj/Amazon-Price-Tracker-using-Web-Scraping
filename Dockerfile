FROM python:3.12-slim

WORKDIR /app
COPY predict.py spam_detector.py /app/

RUN pip install --no-cache-dir pandas scikit-learn

CMD ["python", "spam_detector.py"]



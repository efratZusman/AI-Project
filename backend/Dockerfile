FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# מתקינים תלויות
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# מעתיקים את כל ה-backend
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

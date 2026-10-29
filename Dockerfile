FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Generate and clean data + initialize SQLite DB during build
RUN python src/data_generator.py && \
    python src/data_cleaning.py && \
    python src/db_manager.py

EXPOSE 8080

CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
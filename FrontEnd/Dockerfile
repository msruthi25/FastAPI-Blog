# Base Python image
FROM python:3.11-slim

# Create a non-root user
RUN adduser --disabled-password --gecos "" myuser

# Install ffmpeg
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Set working directory inside container
WORKDIR /app

# Copy requirements file first
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --timeout 300 --retries 5 -r requirements.txt
RUN python -c "import whisper; whisper.load_model('base')"
# Copy all your frontend code into the container
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]

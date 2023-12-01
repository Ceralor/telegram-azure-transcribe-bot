FROM python:3.10-bullseye
WORKDIR /app
COPY *.py .
RUN apt update && apt upgrade -y && apt install -y ffmpeg build-essential libssl-dev ca-certificates libasound2 wget && \
    pip install "python-telegram-bot[job-queue]" python-dotenv azure-cognitiveservices-speech pydub
CMD ["python", "bot.py"]

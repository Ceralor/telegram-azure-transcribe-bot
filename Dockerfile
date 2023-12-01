FROM python:3.10-bullseye
RUN apt update && apt upgrade -y && apt install -y ffmpeg build-essential libssl-dev ca-certificates libasound2 wget && \
    pip install "python-telegram-bot[job-queue]" python-dotenv azure-cognitiveservices-speech pydub
WORKDIR /app
COPY *.py .
LABEL org.opencontainers.image.source=https://github.com/Ceralor/telegram-azure-transcribe-bot
LABEL org.opencontainers.image.description="Azure Transcription bot for Telegram"
LABEL org.opencontainers.image.licenses=MIT
CMD ["python", "bot.py"]

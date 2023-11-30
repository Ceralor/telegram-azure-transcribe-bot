# telegram-azure-transcribe-bot

Simple Telegram bot to transcribe voice messages sent to it via Azure speech-to-text.

Requires libraries:
 - python-telegram-bot[job-queue]
 - python-dotenv
 - azure-cognitiveservices-speech
 - pydub

Requires installed:
 - dotnet
 - ffmpeg

Configure .env file with the following:
 - TELEGRAM_BOT_TOKEN: Token provided by botfather
 - TELEGRAM_BOT_ALLOWED_CHAT_IDS: optional comma-separated list of chat IDs that may use this bot
 - SPEECH_KEY: speech key from Azure speech service
 - SPEECH_REGION: region from Azure speech servce
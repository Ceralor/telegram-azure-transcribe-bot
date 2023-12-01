# telegram-azure-transcribe-bot

Simple Telegram bot to transcribe voice messages sent to it via Azure speech-to-text.

## Configure

You'll need a free (or paid) Azure account with a Speech Services resource. You can visit the [Azure Speech Services page](https://azure.microsoft.com/en-us/products/ai-services/ai-speech) to get started. Make sure to select Free Plan when creating the resource and NOT the pay-as-you-go option.

Configure .env file with the following:
 - TELEGRAM_BOT_TOKEN: Token provided by [@BotFather](https://t.me/botfather)
 - TELEGRAM_BOT_ALLOWED_CHAT_IDS: optional comma-separated list of chat IDs that may use this bot
 - SPEECH_KEY: speech key from Azure speech service
 - SPEECH_REGION: region from Azure speech servce
 - LOG_LEVEL: optional, use strings from Python '[logging](https://docs.python.org/3.10/howto/logging.html)' such as INFO, WARN, DEBUG, ERROR

## Run in Docker

You have two options for running in Docker.

### Use pre-built package

`docker pull ghcr.io/ceralor/telegram-azure-transcribe-bot:latest`

### Build locally

Clone the repository, then use `docker build . -t <insert-local-image-name>

### Running

Either create a `.env` file with the required variables (below) or supply via `-e LOG_LEVEL=WARN` in the command line.

`docker run --restart unless-stopped --env-file .env --detach ghcr.io/ceralor/telegram-azure-transcribe-bot:latest`

## Running bare or building

Requires libraries:
 - python-telegram-bot[job-queue]
 - python-dotenv
 - azure-cognitiveservices-speech
 - pydub

Requires installed:
 - dotnet
 - ffmpeg

Then `python bot.py`
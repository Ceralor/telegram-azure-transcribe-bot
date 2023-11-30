from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, PicklePersistence
from telegram.ext.filters import VOICE
import logging
from os import getenv
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk
from asyncio import sleep, get_event_loop
from pydub import AudioSegment

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger = logging.getLogger('Recognizer')
    logger.info("Received voice message!")
    chat_id = update.effective_chat.id
    voice_id = update.message.id
    msg = await context.bot.send_message(chat_id=chat_id, text="Working on it!", 
                                         reply_to_message_id=voice_id)
    
    new_file = await context.bot.get_file(update.message.voice.file_id)
    path = await new_file.download_to_drive()
    ogg_path = str(path)
    wav_path = str(path) + ".wav"
    ogg_seg = AudioSegment.from_ogg(ogg_path)
    ogg_seg.export(wav_path, format="wav")
    await msg.edit_text("Converted!")
    
    global speech_config
    audio_config = speechsdk.audio.AudioConfig(filename=wav_path)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    done = False
    current_message = ""
    def stop_cb(evt):
        """callback that signals to stop continuous recognition upon receiving an event `evt`"""
        logger.debug('CLOSING on {}'.format(evt))
        nonlocal done
        done = True
    # async def update_message_async(evt, current_message=current_message):
    #     logger.info(f"Async Message: {evt.result.text}")
    #     if not current_message:
    #         current_message = await context.bot.send_message(chat_id=chat_id, 
    #                                                    text=evt.result.text,
    #                                                    reply_to_message_id=voice_id)
    #     else:
    #         await current_message.edit_text(evt.result.text)
    # def update_message(evt):
    #     logger.info(f"Message: {evt.result.text}")
    #     loop = get_event_loop()
    #     loop.create_task(update_message_async(evt, current_message))
    #     loop.run_until_complete()
    def finish_message(evt):
        # previous_message_id = current_message.id
        # loop = get_event_loop()
        # loop.create_task(current_message.edit_text(evt.result.text))
        # current_message = None
        # loop.run_until_complete()
        nonlocal current_message
        current_message += evt.result.text + " "
    # def start_session(evt):
    #     loop = get_event_loop()
    #     loop.create_task()
    #     loop.run_until_complete()
    # def finish_session(evt):
    #     loop = get_event_loop()
    #     loop.create_task(msg.delete())
    #     loop.run_until_complete()
    # Connect callbacks to the events fired by the speech recognizer
    #speech_recognizer.recognizing.connect(update_message)
    speech_recognizer.recognized.connect(finish_message)
    #speech_recognizer.session_started.connect(start_session)
    #speech_recognizer.session_stopped.connect(finish_session)
    # speech_recognizer.canceled.connect(lambda evt: logger.info('CANCELED {}'.format(evt)))
    # stop continuous recognition on either session stopped or canceled events
    speech_recognizer.session_stopped.connect(stop_cb)
    #speech_recognizer.canceled.connect(stop_cb)

    # Start continuous speech recognition
    speech_recognizer.start_continuous_recognition_async()
    await msg.edit_text('Recognizing...')
    while not done:
        await context.bot.send_chat_action(chat_id=chat_id,action=ChatAction.TYPING)
        await sleep(2)
    speech_recognizer.stop_continuous_recognition_async()
    await msg.edit_text(current_message)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Forward me a voice message and I'll transcribe it!")

if __name__ == '__main__':
    load_dotenv()
    global speech_config
    speech_config = speechsdk.SpeechConfig(subscription=getenv('SPEECH_KEY'), region=getenv('SPEECH_REGION'))
    pers = PicklePersistence(filepath='bot.pickle')
    bot_token = getenv('TELEGRAM_BOT_TOKEN')
    application = ApplicationBuilder().token(bot_token).persistence(persistence=pers).build()
    start_handler = CommandHandler('start', start)
    voice_handler = MessageHandler(VOICE, handle_voice)
    application.add_handler(start_handler)
    application.add_handler(voice_handler)
    
    application.run_polling()
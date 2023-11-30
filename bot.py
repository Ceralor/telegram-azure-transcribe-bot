from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, PicklePersistence
from telegram.ext.filters import VOICE, Chat
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
    status_msg = await context.bot.send_message(chat_id=chat_id, text="Working on it!", 
                                         reply_to_message_id=voice_id)
    
    new_file = await context.bot.get_file(update.message.voice.file_id)
    await status_msg.edit_text("Converted!")
    
    global speech_config
    audio_config = speechsdk.audio.AudioConfig(filename=wav_path)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    done = False
    transcription = ""
    ### 
    # Commented code here is intended for whenever I figure out how
    # best to run async calls (send message/edit/delete) from a
    # synchronous function call, nested inside an async function.
    # Azure speech won't call functions async even when doing 'async
    #  recognition', annoyingly.
    ###
    # async def update_message_async(evt, current_message=current_message):
    #     """Takes event from Azure and updates a message object to show realtime transcribing"""
    #     logger.info(f"Async Message: {evt.result.text}")
    #     if not current_message:
    #         current_message = await context.bot.send_message(chat_id=chat_id, 
    #                                                    text=evt.result.text,
    #                                                    reply_to_message_id=voice_id)
    #     else:
    #         await current_message.edit_text(evt.result.text)
    def stop_cb(evt):
        """callback that signals to stop continuous recognition upon receiving an event `evt`"""
        logger.debug('CLOSING on {}'.format(evt))
        nonlocal done
        done = True
    def finish_message(evt):
        nonlocal transcription
        transcription += evt.result.text + " "
    speech_recognizer.recognized.connect(finish_message)
    # stop continuous recognition on either session stopped or canceled events
    speech_recognizer.session_stopped.connect(stop_cb)
    speech_recognizer.canceled.connect(stop_cb)

    # Start continuous speech recognition
    speech_recognizer.start_continuous_recognition_async()
    if update.message.voice.duration > 120:
        await status_msg.edit_text("Recognizing. Due to audio length, this could take a few minutes. Please be patient. You'll get notified when it's completed.")
    else:
        await status_msg.edit_text('Recognizing...')
    while not done:
        await context.bot.send_chat_action(chat_id=chat_id,action=ChatAction.TYPING)
        await sleep(5)
    speech_recognizer.stop_continuous_recognition_async()
    await status_msg.delete()
    await context.bot.send_message(chat_id=chat_id, text=transcription, 
                                    reply_to_message_id=voice_id)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Forward me a voice message and I'll transcribe it!")
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Forward me a voice message. It may take a few minutes to transcribe. I'll reply to the voice message with a new one containing the transcription, so you can go do something else while you're waiting.")

if __name__ == '__main__':
    lg = logging.getLogger('main')
    load_dotenv()
    global speech_config
    speech_config = speechsdk.SpeechConfig(subscription=getenv('SPEECH_KEY'), region=getenv('SPEECH_REGION'))
    pers = PicklePersistence(filepath='bot.pickle')
    bot_token = getenv('TELEGRAM_BOT_TOKEN')
    application = ApplicationBuilder().token(bot_token)
    application = application.persistence(persistence=pers)
    application = application.build()
    start_handler = CommandHandler('start', start)
    help_handler = CommandHandler('help', help)
    voice_handler = MessageHandler(VOICE, handle_voice, block=True)
    if getenv('TELEGRAM_BOT_ALLOWED_CHAT_IDS'):
        chat_ids = [int(x) for x in getenv('TELEGRAM_BOT_ALLOWED_CHAT_IDS').split(',')]
        lg.info(f"Restricting to these chats: {chat_ids}")
        start_handler.filters = Chat(chat_id=chat_ids)
        help_handler.filters = Chat(chat_id=chat_ids)
        voice_handler.filters = VOICE & Chat(chat_id=chat_ids)
    application.add_handler(start_handler)
    application.add_handler(help_handler)
    application.add_handler(voice_handler)
    
    application.run_polling()
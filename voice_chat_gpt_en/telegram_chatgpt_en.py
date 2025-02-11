from revChatGPT.V3 import Chatbot
from issai.asr import ASR
from issai.tts import TTS
from issai import utils
import subprocess
import telebot
import json
import os
import time


# create directories to save
# input and output files
utils.make_dir("input/voice")
utils.make_dir("output")
config = json.load(open("config.json"))
# initialize telegram bot
isRunning = False
tele_token = config["tele_token"]
tele_bot = telebot.TeleBot(tele_token, threaded=True)


# connect to the OpenAI's ChatGPT
chatbot = Chatbot(api_key=config["ChatGPT_token"])
#chatbot.reset_chat()
#chatbot.refresh_session()

# initialize ASR and TTS models
asr = ASR(lang='en', model='google') # to use offline vosk asr: 'google' -> 'vosk'
tts = TTS('google') # to use offline pyttsx3 tts: 'google' -> 'other'

@tele_bot.message_handler(commands=["start", "go"])
def start_handler(message):
    global isRunning
    if not isRunning:
        tele_bot.send_message(message.chat.id, "Welcome to Voice ChatGPT!")
        isRunning = True

@tele_bot.message_handler(content_types=['text'])
def text_processing(message):
    response = chatbot.ask(message.text)
    tele_bot.send_message(message.chat.id, response)
    # create a path to save the audio
    output_audio_path = os.path.join('output', str(time.time()*1000000)+'text_answer.mp3')

    # convert the answer to speech
    tts.convert(response, output_audio_path)

    # send the voice response to the telegram
    tele_bot.send_voice(message.chat.id, voice=open(output_audio_path, "rb"))

    # remove input and output files
    if os.path.exists(output_audio_path):
        os.remove(output_audio_path)

@tele_bot.message_handler(content_types=['voice'])
def voice_processing(message):
    # reset the chat to preserve privacy
    # process the voice message
    file_info = tele_bot.get_file(message.voice.file_id)
    file_data = tele_bot.download_file(file_info.file_path)

    raw_audio_path = './input/' + file_info.file_path
    with open(raw_audio_path, 'wb') as f:
        f.write(file_data)

    #tele_bot.reply_to(message, "Processing...")
    input_audio_path = raw_audio_path + ".wav"
    process = subprocess.run(['ffmpeg', '-i', raw_audio_path, input_audio_path])
    if process.returncode != 0:
        raise Exception("Something went wrong")

    # convert the audio input to text
    asr.convert(input_audio_path)

    tele_bot.reply_to(message, "You: " + asr.message)
    print("User:", asr.message)

    # send the message to ChatGPT
    response = chatbot.ask(asr.message)
    print("ChatGPT:", response)

    # send the text response to telegram
    tele_bot.send_message(message.chat.id, response)

    # create a path to save the audio
    output_audio_path = os.path.join('output', str(time.time()*1000000)+'voice_answer.mp3')

    # convert the answer to speech
    tts.convert(response, output_audio_path)

    # send the voice response to the telegram
    tele_bot.send_voice(message.chat.id, voice=open(output_audio_path, "rb"))

    # remove input and output files
    if os.path.exists(raw_audio_path):
        os.remove(raw_audio_path)
    if os.path.exists(input_audio_path):
        os.remove(input_audio_path)
    if os.path.exists(output_audio_path):
        os.remove(output_audio_path)

# run the telegram bot
tele_bot.polling(none_stop=True)

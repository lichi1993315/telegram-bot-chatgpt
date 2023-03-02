from revChatGPT.V3 import Chatbot

import json

chatbot = Chatbot(api_key="")

response = ""

while True:
    prompt = input("You: ")
    if prompt == 'q':
        break

    response = chatbot.ask(prompt)

    print("ChatGPT:", response)
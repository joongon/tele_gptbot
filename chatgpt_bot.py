import os
import openai
from telegram.ext import Updater
import requests
# from bs4 import BeautifulSoup
from telegram.ext import MessageHandler, Filters
import re
import random
import urllib.request
import subprocess
from transformers import GPT2Tokenizer

#=========== Telegram Bot Info =========================================
TOKEN = "TELEGRAM BOT TOKEN HERE" #Telegram bot의 TOKEN 입력, 보안상 환경변수로 설정을 해도 된다.
approved_id = []#봇 사용이 허가된 대화방 id 리스트, 반드시 정수형을 입력, "" or '' 삽입금지
#ex) approved_id = [23456, -123445, 112333] --> 23456 or -123445, 112222 3개의 채팅방에 대해 본 chatbot 사용허가
#대화방 chat_id 확인 주소 : https://api.telegram.org/bot토큰/getUpdates
bot_name = "BOT NAME" #Telegram bot name을 입력한다.

#========== Telegram bot Trigger 설정 ===================================
enableTrigger = True #Trigger 없이 모든 메세지를 트리거로 할 경우 False
#False일 경우 아래 Trigger 설정은 적용 안되며, GPT3.5 Turbo만 사용, 기타 DALL.E / 

CHAT = "/t" #GPT3.5 Turbo 엔진을 사용한 채팅 트리거 ex) /t
# CODE = "/c" #code-davinci-002 엔진을 사용한 코딩 트리거 ex) /c deprecated now
DRAW = "/p" #DALL.E 엔진을 이용 Image 생성기 트리거 ex) /p 
TEXT = "/txt4" #gpt-4-32k 엔진을 활용한 문장완성 트리거 ex) /txt
#======================================================================

#===========OPENAI API Info =========================================
API_KEY = "" #OPENAI API KEY를 입력한다.
openai.api_key = API_KEY
#=====================================================================

triggers = [CHAT, DRAW, TEXT]
messages = [{"role": "system", "content": "You are a helpful assistant."}]

def tokenizer(sequence):
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    tokens = tokenizer.tokenize(sequence)
    ntokens = len(tokens)
    return ntokens

def img_maker(prompt):
    response = openai.Image.create(prompt=prompt, n=1, size="1024x1024")
    image_url = response['data'][0]['url']
    postfix = str(random.random())[2:]
    local_path = "/home/joongon/sh/openai"
    image_path = local_path + f"openai{postfix}.png"
    urllib.request.urlretrieve(image_url, image_path)
    print(image_path)
    return image_path

def chat_completion(query):
    try:
        messages.append({"role": "user", "content": query})
        token_source = ""
        for msg_dict in messages:
            token_source += msg_dict["content"]
        ntoken = tokenizer(token_source)
        print(ntoken, "==================> TOKEN Q'ty")
        print(messages, "-----------> 1st messages")
        if int(ntoken) > 4096:
            del messages[1:-2]
            for msg_dict in messages:
                token_source += msg_dict["content"]
            ntoken = tokenizer(token_source)
            if int(ntoken) <= 4096:
                res = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
                assistant_message = res['choices'][0]['message']
                print(assistant_message['content'].strip())
                messages.append(assistant_message)
                qty_message = len(messages)
                print(qty_message, "===================> messages 배열 멤버 수")
                total_token_usage = res['usage']['total_tokens']
                print(f'[Tokens Used(Accumulated) : {total_token_usage}]')
                if qty_message > 9:
                    del messages[3:6]

                response = f'*[ Tokens Used {total_token_usage} ]*\n\n' + assistant_message['content'].strip()
           
            else:
                del messages[1:-2]
                res = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
                assistant_message = res['choices'][0]['message']
                print(assistant_message['content'].strip())
                messages.append(assistant_message)
                qty_message = len(messages)
                print(qty_message, "===================> messages 배열 멤버 수")
                total_token_usage = res['usage']['total_tokens']
                print(f'[Tokens Used(Accumulated) : {total_token_usage}]')
                response = f'*[ Tokens Used {total_token_usage} ]*\n\n' + assistant_message['content'].strip()

        else:
            try:
                res = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
                assistant_message = res['choices'][0]['message']
                print(assistant_message['content'].strip())
                messages.append(assistant_message)
                qty_message = len(messages)
                print(qty_message, "===================> messages 배열 멤버 수")
                total_token_usage = res['usage']['total_tokens']
                print(f'[Tokens Used(Accumulated) : {total_token_usage}]')
                if qty_message > 9:
                    del messages[3:6]

                response = f'*[ Tokens Used {total_token_usage} ]*\n\n' + assistant_message['content'].strip()
            except Exception as e:
                response = e        
            
    except Exception as e:
        print(e)
        response = e
    return response

def text_completer2(prompt):
    response = openai.Completion.create(\
    model="gpt-4-32k",\
    prompt=prompt,\
    temperature=0.4,\
    max_tokens=32768,\
    top_p=1,\
    frequency_penalty=0.4,\
    presence_penalty=0\
    )
    text = response['choices'][0]['text']
    return text

def text_completer(prompt):
    response = openai.Completion.create(\
    model="text-davinci-003",\
    prompt=prompt,\
    temperature=0.4,\
    max_tokens=4000,\
    top_p=1,\
    frequency_penalty=0,\
    presence_penalty=0\
    )
    text = response['choices'][0]['text']
    return text

# def code_maker(prompt):
#     response = openai.Completion.create(model="code-davinci-002",\
#     prompt=prompt,\
#     temperature=0,\
#     max_tokens=4000,\
#     top_p=1.0,\
#     frequency_penalty=1.0,\
#     presence_penalty=0.0,\
#     stop=["\"\"\""])
#     code = response['choices'][0]['text']
#     return code

def trash_remover(target):
    p = re.compile('[+]')
    cleaned = p.sub('', target)
    return cleaned

def converter(code):
    pass

updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

def echo(update, context):
    user_id = update.effective_chat.id
    print("Chat_id = ", user_id)
    user_text = update.message.text
    user_text = user_text.split()
    
    

    if user_id in approved_id:
        
        if enableTrigger == True:
            
            if user_text[0] == triggers[1]:
                final_text = ""
                
                for i in range(1, len(user_text)):
                    final_text += user_text[i] + " "
                    print(final_text)
                path = img_maker(final_text)
                context.bot.sendPhoto(chat_id=user_id, photo=open(path, 'rb'))
                subprocess.call(["rm", path])
    #triggers = [CHAT, DRAW, TEXT]
                
            elif user_text[0] == triggers[0]:
                final_text = ""
                
                for i in range(1, len(user_text)):
                    final_text += user_text[i] + " "
                    print(final_text)
                text = chat_completion(final_text)
                context.bot.send_message(chat_id=user_id, text=text, parse_mode='Markdown')

            elif user_text[0] == triggers[2]:
                final_text = ""
                
                for i in range(1, len(user_text)):
                    final_text += user_text[i] + " "
                    print(final_text)
                try:
                    text = text_completer2(final_text)
                except:
                    text = "현재 ChatGPT4 API Beta 모델 엔진 사용신청중이며, Capacity 확부 후 사용 가능해 집니다. 시간이 다소 걸릴 것 같습니다."
                context.bot.send_message(chat_id=user_id, text=text)  
        elif enableTrigger == False:
            final_text = ""
            for i in range(1, len(user_text)):
                final_text += user_text[i] + " "
                print(final_text)
            text = chat_completion(final_text)
            context.bot.send_message(chat_id=user_id, text=text, parse_mode='Markdown')
        else:
            pass

    else:
        text = f"You or this group is not allowed to use the bot({bot_name}). I warn you no to use this bot anymore."
        context.bot.send_message(chat_id=user_id, text=text)

echo_handler = MessageHandler(Filters.text, echo)
dispatcher.add_handler(echo_handler)

updater.start_polling(timeout=3, drop_pending_updates=True)
updater.idle()
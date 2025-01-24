import telebot
import re
from collections import defaultdict
from supabase import create_client
import sys
from dotenv import load_dotenv
import os
from scrapper import processList, generate_file_td

load_dotenv()

API_TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = telebot.TeleBot(API_TOKEN)

# ms = defaultdict(list)


url_s = os.getenv("URL_SUPA")
key_s = os.getenv("KEY_SUPA")

try:
    supabase = create_client(url_s, key_s)
except:
    print("Erro ao conectar ao banco de dados")
    sys.exit(1)

print("Iniciando bot")

# TODO: Adicionar coisas de tratamento de erro
def addLink(user, link):
    supabase.table("links").insert({"url": link, "user_id": user}).execute()

def getLinks(user):
    r = supabase.table("links").select("*").eq("user_id", user).execute()
    # exclui 
    supabase.table("links").delete().eq("user_id", user).execute()
    return r.data

@bot.message_handler(commands=['ola', 'start'])
def send_welcome(message):
    bot.reply_to(message, "Mande links que serão guardados e use o comanod /links ou /l para retornar todos eles(serão apagados depois)")


@bot.message_handler(commands=['links', 'l'])
def a(m):
    r = getLinks(m.chat.id)
    urls = [i["url"] for i in r]

    if len(urls) == 0:
        bot.send_message(m.chat.id, "Sem links guardados")
    else:
        bot.send_message(m.chat.id, "Links selecionados:")
        for i in urls:
            bot.send_message(m.chat.id, i)

    temp_file = generate_file_td() + "_" + str(m.chat.id) + ".md"
    print(f"Arquivo {temp_file} criado")
    processList(urls, temp_file)

    with open(temp_file, "r") as f:
        bot.send_document(m.chat.id, f)

    try: 
        os.remove(temp_file)
    except:
        print(f"Erro ao remover {temp_file}")

link_r = r'https?:\/\/[^\s/$.?#].[^\s]*'
@bot.message_handler(func=lambda m: True)
def link_add(m):
    if re.search(link_r, m.text):
        addLink(m.chat.id, m.text)
        bot.reply_to(m, "Link adicionado")
    else:
        bot.reply_to(m, "Não foi reconhecido como um link")

bot.infinity_polling()

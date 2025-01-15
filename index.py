import requests
from bs4 import BeautifulSoup
import random
import string
import os
import html2text as htmd
from datetime import date
import sys

def generate_file_td():
    return date.today().strftime("%d_%m")

def generate_random_filename(extension="html", length=8):
    letters = string.ascii_lowercase
    random_filename = ''.join(random.choice(letters) for i in range(length)) + f".{extension}"
    return random_filename

def getHtmlFromX(tweet_url):
    # URL base e parâmetros
    base_url = "https://threadnavigator.com/thread/"

    # Cabeçalhos simulando um navegador
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/91.0.4472.124 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://threadnavigator.com/",
    }

    # Parâmetros da query string
    params = {"url": tweet_url}

    # Fazer a requisição
    try:
        response = requests.get(base_url, headers=headers, params=params, timeout=10)
        response.raise_for_status()  # Levanta exceções para códigos de erro HTTP
        
        soup = BeautifulSoup(response.text, "html.parser")

        content =  soup.find("div", {"id": "thread"})
        if content:
            # print(content)
            random_filename = generate_random_filename()
            with open(random_filename, "w", encoding="utf-8") as html_file:
                html_file.write(f"<a href='{tweet_url}'>Link</a>")
                html_file.write(str(content.prettify()))
            return random_filename
        else:
            return -1
    except requests.exceptions.RequestException as e:
        return -1

def saveMd(prefix="", ori=None, des=None):
    with open(ori, "r") as f:
        md = htmd.HTML2Text()
        md.mark_code = True
        h = f.read()
        l = md.handle(h)
        with open(des, "a") as m:
            m.write(prefix)
            m.write(str(l).replace("* * *", "\n"))

def main():
    # print(sys.argv)
    if len(sys.argv) != 2:
        print("Passar apenas o nome do txt")
        return
    md_name = generate_file_td() + ".md"
    linhas = []
    with open(sys.argv[1], "r") as t:
        linhas = [linha.strip() for linha in t]
    if len(linhas) <= 0:
        print(f"Erro nas linhas de txt, {len(linhas)}")
    for idx, i in enumerate(linhas):
        h = getHtmlFromX(i)
        saveMd(f"***\n# {idx}\n", h, md_name)
        try: 
            os.remove(h)
        except e:
            print(f"erro ao remover arquivo {h}")
    print(f"Arquivo {md_name} criado")


if __name__ == "__main__":
    main()

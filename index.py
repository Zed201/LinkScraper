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
    random_filename = ''.join(random.choice(letters) for _ in range(length)) + f".{extension}"
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
        
        # TODO: Pegar videos
        content =  soup.find("div", {"id": "thread"})
        if content:
            # print(content)
            return writeHtml(tweet_url, str(content.prettify()))
        else:
            return -1
    except requests.exceptions.RequestException:
        return -1

def saveMd(ori, des, prefix=""):
    with open(ori, "r") as f:
        md = htmd.HTML2Text()
        md.mark_code = True
        h = f.read()
        l = md.handle(h)
        with open(des, "a") as m:
            m.write(prefix)
            m.write(str(l).replace("* * *", "\n"))

def writeHtml(url, content):
   random_filename = generate_random_filename()
   with open(random_filename, "w", encoding="utf-8") as html_file:
        html_file.write(f"<a href='{url}'>Link</a>\n")
        html_file.write(content)
    
   return random_filename



def getHtmlFromReddit(reddit_url):
    try:
        r = requests.get(reddit_url)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        
        # TODO: Pegar videos
        all = soup.find("shreddit-post")
        _author = all.get("author", "Autor Desconhecido") if all else "Autor Desconhecido"
        soup.find("div", {"slot": "credit-bar"}).decompose()

        # Elimina elementos que só carregam mais tarde
        for tag in soup.find_all(attrs={"loading": "lazy"}):
            tag.decompose()  # Remove a tag do documento
        seen_src = set()
        # Ao pegar posts apenas com imagens ele repete as imagens por causa de navegabilidade...
        # assim basicamente estou deixando apenas 1 das imagens
        # TODO: Melhorar isso
        # algum erro com links de imagens, eles ficam com \n no meio aparentemente
        for img in soup.find_all("img"):
            src = img.get("src")
            if src in seen_src:
                img.decompose()  # Remove as imagens duplicadas
            else:
                seen_src.add(src)  # Marca o src como visto 
        

        # h = title + f"<h1>{_author}</h1>\n" + body 
        h = f"<h1>Autor: {_author}</h1>" + all.prettify()
       
        if all != None:
            return writeHtml(reddit_url, h)
        else:
            return -1
    except requests.exceptions.RequestException:
        return -2
    

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
        h = ""
        # TODO: Melhorar isso
        if i.startswith("https://x.com"):
            h = getHtmlFromX(i)
        elif i.startswith("https://www.reddit.com"):
            h = getHtmlFromReddit(i)

        saveMd(h, md_name, f"***\n# {idx}\n")
        try: 
            if isinstance(h, str):
                os.remove(h)
        except:
            print(f"erro ao remover arquivo {h}")
    print(f"Arquivo {md_name} criado")



if __name__ == "__main__":
    main() 

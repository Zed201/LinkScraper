import requests
from bs4 import BeautifulSoup
import random
import string
import os
# from markitdown import MarkItDown

def generate_random_filename(extension="html", length=8):
    letters = string.ascii_lowercase
    random_filename = ''.join(random.choice(letters) for i in range(length)) + f".{extension}"
    return random_filename

def getHtml(tweet_url):
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
                html_file.write(str(content.prettify()))
            return random_filename
        else:
            return -1
    except requests.exceptions.RequestException as e:
        return -1

# def htmlTomd(content_name):
    # m = MarkItDown()
    # res = m.convert(content)
    # print(res.text_content)

tweet_url = "https://x.com/_OtakusBR/status/1859300831297761550"
h = getHtml(tweet_url)
print(h)
# if h != -1:
    # htmlTomd(h)



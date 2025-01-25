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
    random_filename = (
        "".join(random.choice(letters) for _ in range(length)) + f".{extension}"
    )
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
    soup = getSoap(base_url, params, headers)
    if soup == -1:
        return -1

    # TODO: Pegar videos
    content = soup.find("div", {"id": "thread"})
    if content:
        return writeHtml(tweet_url, str(content.prettify()))
    else:
        return -1


def getSoap(url="", params={}, headers={}):
    try:
        r = requests.get(url, headers=headers, params=params, timeout=10)
        r.raise_for_status()

        soup = BeautifulSoup(r.text, "html.parser")
        if soup:
            return soup
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
    soup = getSoap(reddit_url, {}, {})
    if soup == -1:
        return -1

        # TODO: Pegar videos
    all = soup.find("shreddit-post")
    _author = (
        all.get("author", "Autor Desconhecido") if all else "Autor Desconhecido"
    )
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


def getHtmlFromMedium(url):
    soup = getSoap(url, {}, {})
    if soup == -1:
        return -1

    # TODO: Criar ifs
    title_ = soup.find("h1", {"data-testid": "storyTitle"})
    title = title_.prettify() if title_ else "<h1>Sem titulo</h1>"

    subtitle_ = soup.find("h2", {"class": "pw-subtitle-paragraph"})
    subtitle = subtitle_.prettify() if subtitle_ else "<h3>Sem subtitulo</h3>"

    author_ = soup.find("a", {"data-testid": "authorName"})
    author = author_.prettify() if author_ else "<h3>Autor Desconhecido</h3>"

    # text_ = soup.find_all("p", {"class": "pw-post-body-paragraph"})
    # text = " ".join([element.get_text(strip=True) for element in text_])
    # TODO: Melhorar
    f = (
        lambda tag: "data-selectable-paragraph" in tag.attrs
            or tag.name == "pre"
            or "pw-post-body-paragraph" in tag.get("class", [])
            or "picture" == tag.name
            or "figcaption" == tag.name
            or "h1" == tag.name
            or tag.name == "ul"
    )
    text_ = soup.find_all(f)
    text = " ".join([str(element) for element in text_])
    r = title + subtitle + author + text
    return writeHtml(url, r)



def getHtmlFromDevTo(url):
    soup = getSoap(url, {}, {})
    if soup == -1:
        return -1

    r = requests.get(url)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    header_ = soup.find("div", {"class": "crayons-article__header__meta"})
    # pegar apenas o titulo
    header = header_.find("h1").prettify() if header_ else "<h1>Sem Titulo</h1>"

    main_ = soup.find("div", {"class": "crayons-article__main"})
    main = main_.prettify() if main_ else "<h1>Sem main</h1>"

    h = header + main
    return writeHtml(url, h)


sites_prefix = ["x.com", "reddit.com", "dev.to", "medium.com"]
sites_handler = [getHtmlFromX, getHtmlFromReddit, getHtmlFromDevTo, getHtmlFromMedium]


def main():
    if len(sys.argv) != 2:
        print("Passar apenas o nome do txt")
        return

    md_name = generate_file_td() + ".md"

    linhas = []

    with open(sys.argv[1], "r") as t:
        linhas = [linha.strip() for linha in t]

    if len(linhas) <= 0:
        print(f"Erro nas linhas de txt, {len(linhas)}")

    processList(linhas, md_name)
    print(f"Arquivo {md_name} criado")


def processList(lista, md_name):
    for idx, i in enumerate(lista):
        h = ""
        # TODO: nada optimizado mas funciona no momento e nao precisa ser extremamento eficient

        for jdx, j in enumerate(sites_prefix):
            if j in i:
                h = sites_handler[jdx](i)
                saveMd(h, md_name, f"***\n# {idx}\n")

                try:
                    if isinstance(h, str):
                        os.remove(h)
                except Exception:
                    print(f"erro ao remover arquivo {h}")


if __name__ == "__main__":
    main()

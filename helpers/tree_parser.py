from bs4 import BeautifulSoup
from lxml import etree


def get_frame(content_html: str, xpath: str) -> BeautifulSoup | None:
    '''Função para extrair um elemento da página HTML usando um caminho XPath ou Full XPath
    retorná-lo como um objeto BeautifulSoup.'''

    #Verifica se o input é uma string ou um BeautifulSoup Object
    if isinstance(content_html, BeautifulSoup):
        content_html = str(content_html)

    #Parsing do HTML com o lxml
    parser = etree.HTMLParser()
    tree = etree.fromstring(content_html, parser)

    #Busca do elemento com o XPath
    elements = tree.xpath(xpath)
    if len(elements) == 0:
        return None

    element = tree.xpath(xpath)[0]
        
    #Conversão do elemento para um objeto BeautifulSoup
    element_html = etree.tostring(element)
    return BeautifulSoup(element_html, "lxml")

def has_frame(content_html: str, xpath: str) -> bool:
    '''Função para retornar True ou False se um elemento da página HTML existir'''

    element = get_frame(content_html, xpath)

    if element is None:
        return False
    
    return True
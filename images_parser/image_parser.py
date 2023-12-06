import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from typing import List
import os
from pathlib import Path


NSFW_PATH = Path('dataset/nsfw')
NON_NSFW_PATH = Path('dataset/non-nsfw')
NON_NSFW_FILE_PATH = Path('non-nsfw-websites.txt')
MEMORY_LIMIT = 4294967296 #4g
IMAGES_LIMIT = 2500
PARSER_TYPE = 'lxml'


class HTMLParser:
    """
    HTML parser wrapper.
    """
    def __init__(self, html_content: str, parser_type: str):
        self.html_parser = BeautifulSoup(html_content, parser_type)

    def find_images(self, limit: int) -> list:
        return self.html_parser.find_all('img')[:limit]
    

class FileSystemHelper:

    def pull_websites(self, file_path: Path):
        with open(file_path, 'r') as file:
            for website_url in file:
                yield website_url

    def save_image(self, image: bytes, save_path: Path, name: str) -> None:
        """
        This metod saves the image to disk.

        :param image: image to save.
        :param name: name of image.
        """
        with open(save_path/name, 'wb') as file:
            file.write(image)
    
    def create_name(self, website_url: str, image_number: int) -> str:
        """
        This method creates a unique name for an image depend on the website url.

        :param website_url: website url
        :param index: The index of the image on the website.
        :return: A unique name for the image.
        """
        image_name = urlparse(website_url).path[1:].replace('/', '-')
        return f'{image_name}-{image_number}.png'


class RequestHandler:

    def download_image(self, image_url: str) -> bytes:
        return requests.get(image_url).content

    def get_website_html(self, website_url) -> str:
        return requests.get(website_url).text


class URLHandler:
    HTTP_PREFIX = 'http://'
    HTTPS_PREFIX = 'https://'

    def check_source_url(self, image_source: str, website_url) -> str:
        """
        This method checks image source.
        If the source isn't a link, it's added https:// prefix.

        param: image_source: image source link.
        return: modified link to the source of the image if it was originally unavailable for downloading
        """
        if not image_source.startswith((self.HTTP_PREFIX, self.HTTPS_PREFIX)):
            website_url = urlparse(website_url).netloc
            image_source = f'{self.HTTPS_PREFIX}{website_url}{image_source}'
        return image_source


class ImageParser:
    """
    This class allows you parsing images from any website.
    """
    HTTP_PREFIX = 'http://'
    HTTPS_PREFIX = 'https://'

    def __init__(self, website_html: str, html_parser: HTMLParser, parser_type: str, limit: int):
        """
        :param website: website url for parsing.
        :param html_parser: HTMLParser class that implements html parsing.
        :param save_path: path for saving image to disk.
        :param limit: is needed to download a certain number of images from the site.
        """
        self.website_html = website_html
        self.html_parser = html_parser
        self.parser_type = parser_type
        self.limit = limit

    def parse_website_images(self) -> List[str]:
        parsed_page = self.html_parser(self.website_html, self.parser_type)
        image_tags = parsed_page.find_images(self.limit)
        return [self._pull_url(image_tag) for image_tag in image_tags] 

    def _pull_url(self, image_tag) -> str:
        """
        This method pulls image source from <img> tag.

        :param image_tag: <img> tag object.
        :return: image source.
        """
        return image_tag.get('src', 'data-src')

    def _next_page(self) -> None:
        """
        switching pages on website if pagination exists
        """
        pass

# TODO: Логирование, обработка исключений и пагинация
if __name__ == "__main__":

    fsh = FileSystemHelper()
    rh = RequestHandler()
    uh = URLHandler()

    for website_url in fsh.pull_websites(NON_NSFW_FILE_PATH):
        website_html = rh.get_website_html(website_url)
        image_parser = ImageParser(website_html, HTMLParser, PARSER_TYPE, IMAGES_LIMIT)
        for image_number, image_source in enumerate(image_parser.parse_website_images()):
            image_url = uh.check_source_url(image_source, website_url)
            image = rh.download_image(image_url)
            image_name = fsh.create_name(website_url, image_number)
            fsh.save_image(image, NON_NSFW_PATH, image_name)
        print(website_url)

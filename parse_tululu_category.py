import json

import requests
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from main import *


def main():
    os.makedirs("books", exist_ok=True)
    os.makedirs("images", exist_ok=True)

    book_number = 1
    books = []
    for page in range(1, 5):
        try:
            url_to_get_fantastic_genre = f"https://tululu.org/l55/{page}"
            response = requests.get(url_to_get_fantastic_genre)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'lxml')
            fantastic_books = soup.find_all('table', class_='d_book')
            for book_number, book in enumerate(fantastic_books, start=book_number):
                relative_book_url = book.find('a')['href']
                book_id = relative_book_url.split('b')[1].split('/')[0]
                fantastic_book_url = urljoin('https://tululu.org',
                                             relative_book_url)
                book_page = parse_book_page(get_book_html(book_id))
                books.append(book_page)
                url_to_download_book = f"https://tululu.org/txt.php"
                payload = {'id': book_id}
                book_title_with_id = f"{book_number}-я книга. {book_page['title']}"
                filepath = download_txt(url_to_download_book, payload,
                                        book_title_with_id)
                image_book_numberpath = download_image(book_page['image_url'],
                                            book_page['image_name'])
        except requests.exceptions.HTTPError:
            pass
    with open('books.json', 'w') as file:
        json.dump(books, file, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    main()

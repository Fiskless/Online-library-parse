import argparse
import json
import os
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from main import parse_book_page, get_book_html, download_txt, download_image


def create_page_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--start_page',
        help='Укажите номер страницы, с которой начать скачивание книг',
        nargs='?',
        default=1
    )
    parser.add_argument(
        '--end_page',
        help='Укажите номер страницы, на которой закончить скачивание книг',
        nargs='?',
        default=702
    )

    return parser


def main():
    parser = create_page_parser()
    args = parser.parse_args()
    begin_with = int(args.start_page)
    finish_on = int(args.end_page)

    if begin_with > finish_on:
        raise ValueError(
            'start_page должен быть больше end_page. Введите другие значения')

    os.makedirs("books", exist_ok=True)
    os.makedirs("images", exist_ok=True)

    book_number = 1
    books = []
    for page in range(begin_with, finish_on):
        try:
            url_to_get_fantastic_genre = f"https://tululu.org/l55/{page}"
            response = requests.get(url_to_get_fantastic_genre)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'lxml')
            fantastic_books_selector = ".bookimage a"
            fantastic_books = soup.select(fantastic_books_selector)

            for book_number, book in enumerate(fantastic_books, start=book_number):
                relative_book_url = book['href']
                book_id = relative_book_url.split('b')[1].split('/')[0]
                fantastic_book_url = urljoin('https://tululu.org',
                                             relative_book_url)
                print(fantastic_book_url)
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

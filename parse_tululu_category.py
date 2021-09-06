import argparse
import json
import os

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
        default=701
    )
    parser.add_argument(
        '--skip_imgs',
        help='При наличии аргумента не скачивает картинки',
        action='store_true'
    )
    parser.add_argument(
        '--skip_txt',
        help='При наличии аргумента не скачивает книги',
        action='store_true'
    )
    parser.add_argument(
        '--json_path',
        help='Укажите свой путь к *.json файлу с результатами',
        nargs='?',
        default=os.getcwd()
    )
    parser.add_argument(
        '--dest_folder',
        help='Укажите свой путь к каталогу с результатами парсинга: картинкам, книгам, JSON',
        nargs='?',
        default=''
    )

    return parser


def main():
    parser = create_page_parser()
    args = parser.parse_args()
    begin_with = int(args.start_page)
    finish_on = int(args.end_page)
    skip_imgs = args.skip_imgs
    skip_txt = args.skip_txt
    json_path = args.json_path
    dest_folder = args.dest_folder

    if begin_with > finish_on:
        raise ValueError(
            'start_page должен быть больше end_page. Введите другие значения')

    if dest_folder or not skip_txt:
        os.makedirs(f'{dest_folder}books/', exist_ok=True)
    if dest_folder or not skip_imgs:
        os.makedirs(f'{dest_folder}images/', exist_ok=True)
    if json_path:
        os.makedirs(json_path, exist_ok=True)
    book_number = 1
    books = []
    for page in range(begin_with, finish_on):

        url_to_get_fantastic_genre = f"https://tululu.org/l55/{page}"
        response = requests.get(url_to_get_fantastic_genre)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'lxml')
        fantastic_books_selector = ".bookimage a"
        fantastic_books = soup.select(fantastic_books_selector)
        for book_number, book in enumerate(fantastic_books,
                                           start=book_number+1):
            try:
                relative_book_url = book['href']
                book_id = relative_book_url.split('b')[1].split('/')[0]
                book_page = parse_book_page(get_book_html(book_id))
                books.append(book_page)
                url_to_download_book = f"https://tululu.org/txt.php"
                payload = {'id': book_id}
                book_title_with_id = f"{book_number}-я книга. {book_page['title']}"
                if not skip_txt:
                    filepath = download_txt(url_to_download_book,
                                            payload,
                                            book_title_with_id,
                                            f'{dest_folder}books/'
                                         )
                if not skip_imgs:
                    image_book_numberpath = download_image(
                        book_page['image_url'],
                        book_page['image_name'],
                        f'{dest_folder}images/'
                    )
            except requests.exceptions.HTTPError:
                pass

    if dest_folder:
        with open(f'{dest_folder}books.json', 'w') as file:
            json.dump(books, file, ensure_ascii=False, indent=4)
    else:
        with open(f'{json_path}/books.json', 'w') as file:
            json.dump(books, file, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    main()

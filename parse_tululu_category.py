import argparse
import json
import os

import requests
from bs4 import BeautifulSoup

from main import parse_book_page,\
                get_book_html, \
                download_txt, \
                download_image


def create_page_parser():
    parser = argparse.ArgumentParser()

    pages_count = get_pages_count("https://tululu.org/l55/")

    parser.add_argument(
        '--start_page',
        help='Укажите номер страницы, с которой начать скачивание книг',
        nargs='?',
        default=1,
        type=int
    )
    parser.add_argument(
        '--end_page',
        help='Укажите номер страницы, на которой закончить скачивание книг',
        nargs='?',
        default=pages_count,
        type=int
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


def get_pages_count(url):
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'lxml')
    page_selector = ".npage:nth-last-child(1)"
    pages_count = soup.select_one(page_selector).text
    return pages_count


def main():
    parser = create_page_parser()
    args = parser.parse_args()

    if args.start_page > args.end_page:
        raise ValueError(
            'start_page должен быть больше end_page. Введите другие значения')

    if args.dest_folder or not args.skip_txt:
        os.makedirs(f'{args.dest_folder}books/', exist_ok=True)
    if args.dest_folder or not args.skip_imgs:
        os.makedirs(f'{args.dest_folder}images/', exist_ok=True)
    if args.json_path:
        os.makedirs(args.json_path, exist_ok=True)
    book_number = 1
    books = []
    for page in range(args.start_page, args.end_page):

        url_to_get_fantastic_genre = f"https://tululu.org/l55/{page}"
        response = requests.get(url_to_get_fantastic_genre)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'lxml')
        fantastic_books_selector = ".bookimage a"
        fantastic_books = soup.select(fantastic_books_selector)
        for book_number, book in enumerate(fantastic_books,
                                           start=book_number):
            try:
                relative_book_url = book['href']
                book_id = relative_book_url.split('b')[1].split('/')[0]
                book_html = get_book_html(book_id)
                book_page = parse_book_page(book_html)
                url_to_download_book = f"https://tululu.org/txt.php"
                payload = {'id': book_id}
                book_title_with_id = f"{book_number}-я книга. {book_page['title']}"
                if not args.skip_txt:
                    correct_book_title, filepath = download_txt(url_to_download_book,
                                            payload,
                                            book_title_with_id,
                                            f'{args.dest_folder}books/'
                                         )
                    book_page['title'] = correct_book_title
                if not args.skip_imgs:
                    image_book_numberpath = download_image(
                        book_page['image_url'],
                        book_page['image_name'],
                        f'{args.dest_folder}images/'
                    )
                books.append(book_page)
            except requests.exceptions.HTTPError:
                pass
    filename = f'{args.dest_folder}books.json' if args.dest_folder else f'{args.json_path}/books.json'
    with open(filename, 'w') as file:
        json.dump(books, file, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    main()

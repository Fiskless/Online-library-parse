import argparse
import json
import math
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


def create_page_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'page_books_count',
        help='Укажите, сколько книг вы хотите видеть на одной странице',
        nargs='?',
        default=10,
        type=int
    )
    return parser


def on_reload(books_on_page):
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('template.html')

    with open("books.json", "r") as file:
        books = json.load(file)

    pages_count = math.ceil(len(books)/books_on_page)
    books_with_pages = list(chunked(books, books_on_page))
    for page_number, page_books in enumerate(books_with_pages, start=1):
        books_in_two_columns = list(chunked(page_books, 2))
        rendered_page = template.render(
            books_in_two_columns=books_in_two_columns,
            current_page=page_number,
            pages_count=pages_count,
        )

        with open(f'pages/index{page_number}.html', 'w', encoding="utf8") as file:
            file.write(rendered_page)


def main():
    os.makedirs("pages", exist_ok=True)

    parser = create_page_parser()
    args = parser.parse_args()

    on_reload(args.page_books_count)

    server = Server()
    server.watch('template.html', on_reload)

    server.serve(root='.')


if __name__ == '__main__':
    main()

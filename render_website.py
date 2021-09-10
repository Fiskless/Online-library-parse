import json
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


def on_reload():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('template.html')

    with open("books.json", "r") as file:
        books_json = file.read()

    books = json.loads(books_json)

    books_with_pages = list(chunked(books, 10))
    for page_number, page_books in enumerate(books_with_pages, start=1):
        books_in_two_columns = list(chunked(page_books, 2))
        rendered_page = template.render(
            books_in_two_columns=books_in_two_columns,
        )

        with open(f'pages/index{page_number}.html', 'w', encoding="utf8") as file:
            file.write(rendered_page)


def main():
    os.makedirs("pages", exist_ok=True)

    on_reload()

    server = Server()
    server.watch('template.html', on_reload)

    server.serve(root='.')


if __name__ == '__main__':
    main()

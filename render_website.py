import json

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server


def on_reload():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('template.html')

    with open("books.json", "r") as file:
        books_json = file.read()

    books = json.loads(books_json)

    rendered_page = template.render(
        books=books
    )
    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)


def main():

    on_reload()

    server = Server()
    server.watch('template.html', on_reload)

    server.serve(root='.')


if __name__ == '__main__':
    main()

import requests
import os
from pathvalidate import sanitize_filename, sanitize_filepath
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlsplit, unquote
import argparse


def get_book_html(book_id):
    url_to_get_title = f"https://tululu.org/b{book_id}/"
    response = requests.get(url_to_get_title)
    response.raise_for_status()
    check_for_redirect(response)

    return response.text


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'start_id',
        help='Укажите номер книги, с которой начать скачивание',
        nargs='?',
        default=1,
        type=int
    )
    parser.add_argument(
        'end_id',
        help='Укажите номер книги, на которой закончить скачивание',
        nargs='?',
        default=10,
        type=int
    )

    return parser


def parse_book_page(html):
    soup = BeautifulSoup(html, 'lxml')

    title_and_author_selector = "h1"
    book_title_and_author = soup\
        .select_one(title_and_author_selector)\
        .text\
        .split('::')
    book_title = book_title_and_author[0].strip()

    picture_selector = '.bookimage img'
    relative_picture_address = soup.select_one(picture_selector)['src']
    img_url = urljoin('https://tululu.org', relative_picture_address)
    image_name = unquote(urlsplit(img_url)[2].split('/')[-1])

    comments_selector = '.texts span'
    book_comments = soup.select(comments_selector)
    book_comments = [book_comment.text
                     for book_comment in book_comments]

    genres_selector = 'span.d_book a'
    book_genres_tag = soup.select(genres_selector)
    book_genres = [book_genre_tag.text for book_genre_tag in book_genres_tag]

    book_page = {
        'title': book_title,
        'image_name': image_name,
        'image_url': img_url,
        'book_comments': book_comments,
        'book_genres': book_genres
    }

    return book_page


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError


def download_txt(url, params_book_url, filename, folder='books/'):
    correct_filename = sanitize_filename(filename)
    correct_folder = sanitize_filepath(folder)
    path_to_book = os.path.join(correct_folder, f'{correct_filename}.txt')

    response = requests.get(url, params=params_book_url)
    response.raise_for_status()
    check_for_redirect(response)

    with open(path_to_book, "w") as file:
        file.write(response.text)
    return path_to_book


def download_image(url, filename, folder='images/'):
    correct_filename = sanitize_filename(filename)
    correct_folder = sanitize_filepath(folder)
    image_path = os.path.join(correct_folder, correct_filename)

    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)

    with open(image_path, "wb") as file:
        file.write(response.content)
    return image_path


def main():
    parser = create_parser()
    args = parser.parse_args()

    if args.start_id > args.end_id:
        raise ValueError(
            'start_id должен быть больше end_id. Введите другие значения'
        )

    os.makedirs("books", exist_ok=True)
    os.makedirs("images", exist_ok=True)

    for book_id in range(args.start_id, args.end_id+1):
        try:
            book_page = parse_book_page(get_book_html(book_id))
            url_to_download_book = f"https://tululu.org/txt.php"
            payload = {'id': book_id}
            book_title_with_id = f"{book_id}-я книга. {book_page['title']}"
            filepath = download_txt(url_to_download_book,
                                    payload,
                                    book_title_with_id)
            image_path = download_image(book_page['image_url'],
                                        book_page['image_name'])
        except requests.exceptions.HTTPError:
            pass


if __name__ == '__main__':
    main()

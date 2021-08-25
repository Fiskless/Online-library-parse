import requests
import os
from pathvalidate import sanitize_filename, sanitize_filepath
from bs4 import BeautifulSoup


def get_book_title(book_id):
    url_to_get_title = f"https://tululu.org/b{book_id}/"
    response = requests.get(url_to_get_title)
    response.raise_for_status()
    check_for_redirect(response)

    soup = BeautifulSoup(response.text, 'lxml')
    book_title_and_author = soup.find('h1').text.split('::')
    book_title = f'{book_id}. {book_title_and_author[0].strip()}'
    return book_title


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError


def download_txt(url, filename, folder='books/'):
    correct_filename = sanitize_filename(filename)
    correct_folder = sanitize_filepath(folder)
    path_to_book = os.path.join(correct_folder, f'{correct_filename}.txt')

    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)

    with open(path_to_book, "w") as file:
        file.write(response.text)
    return path_to_book


def main():
    os.makedirs("books", exist_ok=True)
    for book_id in range(1, 11):
        try:
            book_title = get_book_title(book_id)
            url_to_download_book = f"https://tululu.org/txt.php?id={book_id}"
            filepath = download_txt(url_to_download_book, book_title)
        except requests.exceptions.HTTPError:
            pass


if __name__ == '__main__':

    main()

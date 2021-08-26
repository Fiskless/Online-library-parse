import requests
import os
from pathvalidate import sanitize_filename, sanitize_filepath
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlsplit


def get_book_title(book_id):
    url_to_get_title = f"https://tululu.org/b{book_id}/"
    response = requests.get(url_to_get_title)
    response.raise_for_status()
    check_for_redirect(response)

    soup = BeautifulSoup(response.text, 'lxml')

    book_title_and_author = soup.find('h1').text.split('::')
    book_title = f'{book_id}. {book_title_and_author[0].strip()}'
    print(book_title)
    relative_picture_address = soup.find('div', class_='bookimage').find('img')['src']
    url_to_download_image = urljoin('https://tululu.org', relative_picture_address)
    image_name = urlsplit(url_to_download_image)[2].split('/')[-1]

    book_comments_tag = soup.find_all('div', class_='texts')
    book_comments = [book_comment_tag.find('span').text
                     for book_comment_tag in book_comments_tag]

    book_genres_tag = soup.find('span', class_='d_book').find_all('a')
    book_genres = [book_genre_tag.text for book_genre_tag in book_genres_tag]


    return book_title, image_name, url_to_download_image


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

    # with open(path_to_book, "w") as file:
    #     file.write(response.text)
    return path_to_book


def download_image(url, filename, folder='images/'):
    correct_filename = sanitize_filename(filename)
    correct_folder = sanitize_filepath(folder)
    image_path = os.path.join(correct_folder, correct_filename)

    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)

    # with open(image_path, "wb") as file:
    #     file.write(response.content)
    return image_path


def main():
    os.makedirs("books", exist_ok=True)
    os.makedirs("images", exist_ok=True)
    for book_id in range(1, 11):
        try:
            book_title, image_name, url_to_download_image = get_book_title(book_id)
            url_to_download_book = f"https://tululu.org/txt.php?id={book_id}"
            filepath = download_txt(url_to_download_book, book_title)
            image_path = download_image(url_to_download_image, image_name)
        except requests.exceptions.HTTPError:
            pass


if __name__ == '__main__':

    main()

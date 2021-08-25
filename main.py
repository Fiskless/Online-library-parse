import requests
import os


def get_and_save_book(book_id):
    response = requests.get(f"https://tululu.org/txt.php?id={book_id}")
    response.raise_for_status()
    check_for_redirect(response)

    with open(f"books/id{book_id}.txt", "w") as file:
        file.write(response.text)


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError


def main():
    os.makedirs("books", exist_ok=True)
    for book_id in range(1, 11):
        try:
            get_and_save_book(book_id)
        except requests.exceptions.HTTPError:
            pass


if __name__ == '__main__':

    main()

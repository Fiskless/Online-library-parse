import requests
import os


def get_and_save_book(book_id):
    response = requests.get(f"https://tululu.org/txt.php?id={book_id}")
    response.raise_for_status()

    with open(f"books/id{book_id}.txt", "w") as file:
        file.write(response.text)


if __name__ == '__main__':

    os.makedirs("books", exist_ok=True)

    for book_id in range(1, 11):
        get_and_save_book(book_id)

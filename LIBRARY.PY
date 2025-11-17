import csv
from datetime import datetime

# ======================
# BOOK CLASS
# ======================
class Book:
    def __init__(self, book_id, name, author, year, copies, status=True):
        self.book_id = book_id
        self.name = name
        self.author = author
        self.year = year
        self.copies = int(copies)
        self.status = status  # True if available

    def to_dict(self):
        return {
            "book_id": self.book_id,
            "book_name": self.name,
            "author_name": self.author,
            "year_published": self.year,
            "number_of_copies": self.copies,
            "status": self.status
        }

    @staticmethod
    def from_dict(data):
        # Safely get status (default True if missing)
        status = data.get("status", True)
        if isinstance(status, str):
            status = status.lower() in ["true", "yes", "1"]
        return Book(
            data["book_id"],
            data["book_name"],
            data["author_name"],
            data["year_published"],
            int(data["number_of_copies"]),
            status
        )

# ======================
# USER CLASS
# ======================
class User:
    def __init__(self, name):
        self.name = name

    def to_csv(self):
        return [self.name]

# ======================
# LIBRARY CLASS
# ======================
class Library:
    def __init__(self):
        self.books_file = "books.csv"
        self.users_file = "users.csv"
        self.borrowed_file = "borrowed_books.csv"
        self.returned_file = "returned_books.csv"

        self.books = {}  # book_id : Book
        self.users = []  # list of usernames

        self.load_books()
        self.load_users()

    # ------------------
    # LOAD BOOKS
    # ------------------
    def load_books(self):
        self.books = {}
        try:
            with open(self.books_file, "r", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Skip empty rows
                    if not row.get("book_id"):
                        continue
                    book = Book.from_dict(row)
                    self.books[book.book_id] = book
        except FileNotFoundError:
            # Default books
            default_books = {
                "101": Book("101", "The Jungle Book", "Rudyard Kipling", "1894", 5),
                "102": Book("102", "To Kill a Mockingbird", "Harper Lee", "1960", 5),
                "103": Book("103", "1984", "George Orwell", "1949", 5),
                "104": Book("104", "Pride and Prejudice", "Jane Austen", "1813", 5),
                "105": Book("105", "The Great Gatsby", "F. Scott Fitzgerald", "1925", 5)
            }
            self.books = default_books
            self.save_books()

    # ------------------
    # SAVE BOOKS
    # ------------------
    def save_books(self):
        with open(self.books_file, "w", newline="") as f:
            fieldnames = ["book_id", "book_name", "author_name", "year_published", "number_of_copies", "status"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for book in self.books.values():
                writer.writerow(book.to_dict())

    # ------------------
    # LOAD USERS
    # ------------------
    def load_users(self):
        self.users = []
        try:
            with open(self.users_file, "r", newline="") as f:
                reader = csv.reader(f)
                for row in reader:
                    if row:
                        self.users.append(row[0])
        except FileNotFoundError:
            pass

    # ------------------
    # SAVE USER
    # ------------------
    def save_user(self, user_name):
        if user_name not in self.users:
            self.users.append(user_name)
            with open(self.users_file, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([user_name])

    # ------------------
    # CHECK USER
    # ------------------
    def check_user(self):
        user_name = input("Enter your name: ").strip()
        if user_name in self.users:
            print(f"Welcome back, {user_name}!")
        else:
            print(f"Welcome, {user_name}! You are now registered.")
            self.save_user(user_name)
        return user_name

    # ------------------
    # ADD BOOK
    # ------------------
    def add_book(self):
        book_id = input("Enter book ID: ").strip()
        if book_id in self.books:
            print("Book already exists!")
            return
        name = input("Enter book name: ").strip()
        author = input("Enter author name: ").strip()
        year = input("Enter year published: ").strip()
        copies = int(input("Enter number of copies: "))
        self.books[book_id] = Book(book_id, name, author, year, copies)
        self.save_books()
        print("Book added successfully.")

    # ------------------
    # FIND BOOK
    # ------------------
    def find_book(self):
        book_id = input("Enter book ID to find: ").strip()
        if book_id in self.books:
            book = self.books[book_id]
            print(f"Book ID: {book.book_id}\nName: {book.name}\nAuthor: {book.author}\nYear: {book.year}\nCopies: {book.copies}\nStatus: {'Available' if book.status else 'Borrowed'}")
        else:
            print("Book not found.")

    # ------------------
    # BORROW BOOK
    # ------------------
    def borrow_book(self, user_name):
        book_id = input("Enter book ID to borrow: ").strip()
        if book_id in self.books:
            book = self.books[book_id]
            if book.copies > 0:
                book.copies -= 1
                if book.copies == 0:
                    book.status = False
                self.save_books()
                # record borrowed book
                with open(self.borrowed_file, "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow([user_name, book.book_id, book.name, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
                print(f"You borrowed '{book.name}'. Copies left: {book.copies}")
            else:
                print("No copies left.")
        else:
            print("Book ID not found.")

    # ------------------
    # RETURN BOOK
    # ------------------
    def return_book(self, user_name):
        book_id = input("Enter book ID to return: ").strip()
        if book_id in self.books:
            book = self.books[book_id]
            book.copies += 1
            book.status = True
            self.save_books()
            with open(self.returned_file, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([user_name, book.book_id, book.name, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
            print(f"Book '{book.name}' returned successfully. Copies now: {book.copies}")
        else:
            print("Book ID not found.")

    # ------------------
    # SHOW ALL BOOKS
    # ------------------
    def show_all_books(self):
        print("\nAll Books in Library:")
        for book in self.books.values():
            print(f"{book.book_id} - {book.name} by {book.author} ({book.year}) | Copies: {book.copies} | {'Available' if book.status else 'Borrowed'}")

    # ------------------
    # SHOW BORROWED RECORDS
    # ------------------
    def show_borrowed_records(self):
        try:
            with open(self.borrowed_file, "r", newline="") as f:
                reader = csv.reader(f)
                print("\nBorrowed Books Records:")
                print("User | Book ID | Book Name | Date & Time")
                print("-" * 50)
                for row in reader:
                    print(" | ".join(row))
        except FileNotFoundError:
            print("No borrowed books record found.")

    # ------------------
    # SHOW AVAILABLE BOOKS
    # ------------------
    def show_available_books(self):
        print("\nAvailable Books:")
        found = False
        for book in self.books.values():
            if book.status:
                found = True
                print(f"{book.book_id} - {book.name} ({book.copies} copies available)")
        if not found:
            print("No books available.")

# ======================
# MAIN MENU
# ======================
def main():
    library = Library()
    user_name = library.check_user()

    while True:
        print("\n--- LIBRARY MENU ---")
        print("1. Add Book")
        print("2. Find Book")
        print("3. Borrow Book")
        print("4. Return Book")
        print("5. Show Available Books")
        print("6. Show All Books")
        print("7. Show Borrowed Records")
        print("8. Exit")

        choice = input("Enter your choice (1-8): ").strip()
        if choice == "1":
            library.add_book()
        elif choice == "2":
            library.find_book()
        elif choice == "3":
            library.borrow_book(user_name)
        elif choice == "4":
            library.return_book(user_name)
        elif choice == "5":
            library.show_available_books()
        elif choice == "6":
            library.show_all_books()
        elif choice == "7":
            library.show_borrowed_records()
        elif choice == "8":
            print("Exiting Library System. Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()
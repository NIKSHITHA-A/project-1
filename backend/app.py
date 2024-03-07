from flask_cors import CORS 
from flask import Flask, jsonify, request
from pymongo import MongoClient
from bson import ObjectId
import requests
import random
import string

app = Flask(__name__)
CORS(app)

# Connect to MongoDB Atlas
client = MongoClient('mongodb+srv://primary_librarian:stanchlibrary2020@stanchbook.ewjpt23.mongodb.net/?retryWrites=true&w=majority&appName=StanchBook')
db = client['StanchBook']
users_collection = db['Users']
books_collection = db['BooksCollection']


FRAPPE_API_URL = "https://frappe.io/api/method/frappe-library"
class Book:
    def __init__(self, book_data):
        self.title = book_data.get('title')
        self.authors = book_data.get('authors')
        self.isbn = book_data.get('isbn')
        self.publisher = book_data.get('publisher')
        self.page_count = book_data.get('num_pages')
        self.publication_date = book_data.get('publication_date')
        self.available = True  
        self.rent_fee = 50 

class Member:
    def __init__(self, username, password, max_debt=500):
        self.username = username
        self.password = password
        self.max_debt = max_debt
        self.books_borrowed = []

@app.route('/books',methods=['GET'])
def fetch_books_from_api(title="", authors="", isbn="", publisher="", page=1):
    params = {
        "page": page,
        "title": title,
        "authors": authors,
        "isbn": isbn,
        "publisher": publisher
    }
    response = requests.get(FRAPPE_API_URL, params=params)
    print(response.json())
    if response.status_code == 200:
        return response.json().get("message", [])
    else:
        return []

@app.route('/')
def index():
    return "Welcome to Library Management System"






@app.route('/books', methods=['POST'])
def create_book():
    data = request.json
    book_id = data.get('bookID')

    if books_collection.find_one({'bookID': book_id}):
        return jsonify({'error': 'Book with the same ID already exists'}), 400

    
    books_collection.insert_one(data)

    return jsonify({'message': 'Book created successfully'})


@app.route('/books/<book_id>', methods=['GET'])
def read_book(book_id):
    book = books_collection.find_one({'bookID': book_id})

    if not book:
        return jsonify({'error': 'Book not found'}), 404

    return jsonify({'book': book})


@app.route('/books/<book_id>', methods=['PUT'])
def update_book(book_id):
    data = request.json
    book = books_collection.find_one({'bookID': book_id})

    if not book:
        return jsonify({'error': 'Book not found'}), 404

    
    books_collection.update_one({'bookID': book_id}, {'$set': data})

    return jsonify({'message': 'Book updated successfully'})


@app.route('/books/<book_id>', methods=['DELETE'])
def delete_book(book_id):
    result = books_collection.delete_one({'bookID': book_id})

    if result.deleted_count == 0:
        return jsonify({'error': 'Book not found'}), 404

    return jsonify({'message': 'Book deleted successfully'})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = users_collection.find_one({'username': username, 'password': password})

    if user:
        return jsonify({'message': 'Login successful', 'username': username})
    else:
        return jsonify({'error': 'Invalid credentials'}), 401
def borrow_book():
    data = request.json
    book_id = data.get('book_id')
    member_id = data.get('member_id')

    
    book = mongo.db.books.find_one({'bookID': book_id})
    member = mongo.db.members.find_one({'member_id': member_id})

    if not book or not member:
        return jsonify({'error': 'Book or member not found'}), 404

    
    if member['outstanding_debt'] >= 500:
        return jsonify({'error': 'Member has outstanding debt exceeding Rs. 500. Cannot borrow a book.'}), 400

    

    return jsonify({'message': 'Book borrowed successfully'})


@app.route('/return', methods=['POST'])
def return_book():
    data = request.json
    book_id = data.get('book_id')
    member_id = data.get('member_id')

    
    book = mongo.db.books.find_one({'bookID': book_id})
    member = mongo.db.members.find_one({'member_id': member_id})

    if not book or not member:
        return jsonify({'error': 'Book or member not found'}), 404

   

    return jsonify({'message': 'Book returned successfully'}) 
def generate_random_id():
    return ''.join(random.choices(string.hexdigits, k=24))    
@app.route('/books/import', methods=['GET'])
def import_books():
    title = request.args.get('title', '')
    page = request.args.get('page', 1)
    
    
    response = requests.get(FRAPPE_API_URL, params={"title": title, "page": page})
    
    if response.status_code == 200:
        books_data = response.json().get("message", [])
        for book in books_data:
            book['_id'] = generate_random_id()
        books_collection.insert_many(books_data)    
        

        
        
   

        return jsonify({'books': books_data, 'message': 'Books imported successfully'})
    else:
        return jsonify({'error': 'Failed to fetch books from Frappe API'}), 500
@app.route('/members', methods=['POST'])
def create_member():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    max_debt = data.get('max_debt', 500)

    new_member = Member(username, password, max_debt)

    
    users_collection.insert_one(new_member.__dict__)

    return jsonify({'message': 'Member created successfully'})


@app.route('/members', methods=['GET'])
def read_all_members():
    members = list(users_collection.find({}, {'_id': 0}))
    return jsonify({'members': members})


@app.route('/members/<username>', methods=['GET'])
def read_member(username):
    member = users_collection.find_one({'username': username}, {'_id': 0})
    
    if not member:
        return jsonify({'error': 'Member not found'}), 404

    return jsonify({'member': member})


@app.route('/members/<username>', methods=['PUT'])
def update_member(username):
    data = request.json
    updated_member = users_collection.find_one_and_update(
        {'username': username},
        {'$set': data},
        return_document=True
    )

    if not updated_member:
        return jsonify({'error': 'Member not found'}), 404

    return jsonify({'message': 'Member updated successfully'})


@app.route('/members/<username>', methods=['DELETE'])
def delete_member(username):
    result = users_collection.delete_one({'username': username})

    if result.deleted_count == 0:
        return jsonify({'error': 'Member not found'}), 404

    return jsonify({'message': 'Member deleted successfully'})
@app.route('/search', methods=['POST'])
def search():
    try:
        data = request.get_json()
        title = data.get('title', '')
        author = data.get('author', '')

        # Construct the API URL with the provided title and author
        api_url = f'https://frappe.io/api/method/frappe-library?title={title}&authors={author}'

        # Make the API request to frappe-library
        response = requests.get(api_url)
        results = response.json()

        return jsonify({'message': results})

    except Exception as e:
        return jsonify({'error': str(e)})
@app.route('/lend-book', methods=['POST'])
def lend_book():
    data = request.json
    username = data.get('username')
    title = data.get('title')
    start_date = data.get('start_date')
    last_date = data.get('last_date')

    # Check if the user exists
    user = users_collection.find_one({'username': username})
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Check if the book exists
    book = books_collection.find_one({'title': title})
    if not book:
        return jsonify({'error': 'Book not found'}), 404

    # Create a new entry for the book in the user's borrowed books
    borrowed_book = {
        'bookId': str(book["_id"]),  # Convert ObjectId to string
        'start_date': start_date,
        'last_date': last_date
    }
    users_collection.update_one(
        {'username': username},
        {'$push': {'books_borrowed': borrowed_book}}
    )

    return jsonify({'message': 'Book lent successfully'})
@app.route('/listBooks', methods=['POST'])
def list_books():
    username = request.form.get('username')
    user_data = users_collection.find_one({'username': username})
    # print(user_data)
    if user_data:
        books_borrowed = user_data.get('books_borrowed', [])
        return jsonify(books_borrowed)
    else:
        return jsonify([])
@app.route('/returnBook', methods=['POST'])
def return_books():
    username = request.form.get('username')
    book_id = request.form.get('bookId')

    # Search for the user in the 'Users' collection
    user = users_collection.find_one({'username': username})

    if user:
        # Remove the book with matching bookId from the 'borrowed_books' array
        users_collection.update_one({'username': username}, {'$pull': {'books_borrowed': {'bookId': book_id}}})
        
        return jsonify({'message': 'Book returned successfully for user ' + username})
    else:
        return jsonify({'message': 'User not found.'})        

           

if __name__ == '__main__':
    app.run(debug=True)
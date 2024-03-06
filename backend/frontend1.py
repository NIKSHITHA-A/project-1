from flask import Flask, render_template, request
import requests
app = Flask(__name__)

# Dummy data for books (replace with your database)
books = [
    {"title": "Book 1", "author": "Author 1"},
    {"title": "Book 2", "author": "Author 2"},
]
books = requests.get("https://frappe.io/api/method/frappe-library?page=2&title=and")
print(books)

@app.route('/')
def stanch():
    return render_template('stanch.html')

@app.route('/module1')
def module1():
    return render_template('module1.html')
@app.route('/librarian')
def librarian():
    return render_template('librarian.html')    




@app.route('/search', methods=['POST'])
def search():
    search_title = request.form.get('book_title')
    search_results = [book for book in books if search_title.lower() in book['title'].lower()]

    return render_template('module1.html', search_results=search_results)

if __name__ == '__main__':
    app.run(debug=True)

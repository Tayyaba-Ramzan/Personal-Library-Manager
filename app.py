import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

# Set up Streamlit page configuration
st.set_page_config(page_title="Personal Library Manager", page_icon="📖", layout="wide")

# Database setup
def init_db():
    conn = sqlite3.connect("library.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            genre TEXT NOT NULL,
            year INTEGER CHECK(year >= 1000 AND year <= 9999)
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Database Functions
def add_book(title, author, genre, year):
    conn = sqlite3.connect("library.db")
    c = conn.cursor()
    c.execute("INSERT INTO books (title, author, genre, year) VALUES (?, ?, ?, ?)", (title, author, genre, year))
    conn.commit()
    conn.close()
    st.cache_data.clear()  # Clear cache to refresh data

@st.cache_data
def get_books():
    conn = sqlite3.connect("library.db")
    c = conn.cursor()
    c.execute("SELECT * FROM books")
    books = c.fetchall()
    conn.close()
    return books

def delete_book(book_id):
    conn = sqlite3.connect("library.db")
    c = conn.cursor()
    c.execute("DELETE FROM books WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()
    st.cache_data.clear()  # Clear cache to refresh data

def update_book(book_id, title, author, genre, year):
    conn = sqlite3.connect("library.db")
    c = conn.cursor()
    c.execute("UPDATE books SET title = ?, author = ?, genre = ?, year = ? WHERE id = ?", (title, author, genre, year, book_id))
    conn.commit()
    conn.close()
    st.cache_data.clear()  # Clear cache to refresh data

# Define genre options globally
genre_options = ["Fiction", "Non-Fiction", "Science Fiction", "Biography", "Self-Help", "Mystery", "Romance", "Fantasy", "Horror", "Thriller", "History", "Other"]

# Sidebar Styling and Navigation
with st.sidebar:
    st.image("https://i.imgur.com/OvMZBs9.png", width=200)
    st.markdown("<h2>📖 Library Manager</h2>", unsafe_allow_html=True)
    
    menu = ["🏠 Home", "➕ Add Book", "📖 View Books", "✏️ Update Book", "🗑 Delete Book", "📊 Analytics"]
    choice = st.radio("📌 Navigation", menu, label_visibility="collapsed")
    st.markdown('<hr>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:14px;">💡 Organize your personal book collection easily!</div>', unsafe_allow_html=True)

st.title("📚 Advanced Personal Library Manager")

# Home Section
if choice == "🏠 Home":
    st.subheader("📖 Welcome to Your Personal Library Manager!")
    st.markdown("""
        - 📌 **Add** your favorite books
        - 🔍 **Search** and **update** book details
        - 📊 Get **analytics** on your book collection
        - 🗑 **Remove** books you no longer need
    """)
    st.info("Navigate using the sidebar to manage your library! 🚀")

# Add Book Section
elif choice == "➕ Add Book":
    st.subheader("➕ Add a New Book")
    title = st.text_input("📖 Title", placeholder="Enter book title...")
    author = st.text_input("✍️ Author", placeholder="Enter author's name...")
    genre = st.selectbox("📚 Genre", genre_options, index=None, placeholder="Select a genre...")
    year = st.slider("📆 Year", min_value=1000, max_value=9999, step=1)
    
    if st.button("➕ Add Book", use_container_width=True):
        if title and author and genre:
            add_book(title, author, genre, year)
            st.success(f"🎉 Book '{title}' added successfully!")
        else:
            st.warning("⚠️ Please fill in all fields.")

# View Books Section
elif choice == "📖 View Books":
    st.subheader("📖 Your Book Collection")
    books = get_books()

    if books:
        df = pd.DataFrame(books, columns=["ID", "Title", "Author", "Genre", "Year"])
        search_query = st.text_input("🔍 Search by title or author", placeholder="Type to search...")

        if search_query:
            df = df[df["Title"].str.contains(search_query, case=False, na=False) | df["Author"].str.contains(search_query, case=False, na=False)]

        st.dataframe(df, use_container_width=True)
    else:
        st.warning("📭 No books found in the library.")

# Update Book Section
elif choice == "✏️ Update Book":
    st.subheader("✏️ Update Book Details")
    books = get_books()

    if books:
        book_dict = {f"{book[0]} - {book[1]}": book[0] for book in books}
        selected_book = st.selectbox("📌 Select a Book", list(book_dict.keys()))
        book_id = book_dict.get(selected_book)

        title = st.text_input("✏️ New Title", placeholder="Enter new title...")
        author = st.text_input("✍️ New Author", placeholder="Enter new author...")
        genre = st.selectbox("📚 New Genre", genre_options, index=None, placeholder="Select a new genre...")
        year = st.slider("📆 New Year", min_value=1000, max_value=9999, step=1)
        
        if st.button("✅ Update Book", use_container_width=True):
            if title and author and genre:
                update_book(book_id, title, author, genre, year)
                st.success("🎉 Book updated successfully!")
            else:
                st.warning("⚠️ Please fill in all fields.")
    else:
        st.warning("📭 No books available to update.")

# Delete Book Section
elif choice == "🗑 Delete Book":
    st.subheader("🗑 Delete a Book")
    books = get_books()

    if books:
        book_dict = {f"{book[0]} - {book[1]}": book[0] for book in books}
        selected_book = st.selectbox("📌 Select a Book to Delete", list(book_dict.keys()))
        book_id = book_dict.get(selected_book)
        
        if st.button("❌ Delete Book", use_container_width=True):
            delete_book(book_id)
            st.success("📕 Book deleted successfully!")
    else:
        st.warning("📭 No books available to delete.")

# Analytics Section
elif choice == "📊 Analytics":
    st.subheader("📊 Library Analytics")
    books = get_books()

    if books:
        df = pd.DataFrame(books, columns=["ID", "Title", "Author", "Genre", "Year"])
        genre_count = df["Genre"].value_counts().reset_index()
        genre_count.columns = ["Genre", "Count"]
        fig = px.bar(genre_count, x="Genre", y="Count", title="📊 Books by Genre", color="Genre")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("📭 No books available for analytics.")

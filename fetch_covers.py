import sqlite3
import requests

DB_NAME = "database.db"

# Gutenberg book IDs (same as before) - covers follow a predictable URL pattern
gutenberg_ids = {
    "Pride and Prejudice": 1342,
    "Alice in Wonderland": 11,
    "Frankenstein": 84,
    "Dracula": 345,
    "The Adventures of Sherlock Holmes": 1661,
    "The Great Gatsby": 64317,
    "Moby Dick": 2701,
    "Jane Eyre": 1260,
    "White Nights": 600,
    "Crime and Punishment": 2554,
    "Metamorphosis": 5200,
}

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

for title, gid in gutenberg_ids.items():
    book_row = cursor.execute("SELECT id, cover_image FROM books WHERE title = ?", (title,)).fetchone()
    if not book_row:
        continue

    filename = book_row[1]
    url = f"https://www.gutenberg.org/cache/epub/{gid}/pg{gid}.cover.medium.jpg"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            filepath = f"static/book_covers/{filename}"
            with open(filepath, 'wb') as f:
                f.write(response.content)
            print(f"Saved cover for {title}")
        else:
            print(f"No cover found for {title} (status {response.status_code})")
    except Exception as e:
        print(f"Error for {title}: {e}")

conn.close()
print("Done!")
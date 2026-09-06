import sqlite3
import requests
import re

DB_NAME = "database.db"

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

def download_text(gutenberg_id):
    url = f"https://www.gutenberg.org/files/{gutenberg_id}/{gutenberg_id}-0.txt"
    response = requests.get(url)
    if response.status_code != 200:
        url = f"https://www.gutenberg.org/cache/epub/{gutenberg_id}/pg{gutenberg_id}.txt"
        response = requests.get(url)
    response.encoding = 'utf-8'
    return response.text

def clean_and_split_chapters(raw_text):
    start_marker = "*** START OF"
    end_marker = "*** END OF"

    start_idx = raw_text.find(start_marker)
    end_idx = raw_text.find(end_marker)

    if start_idx != -1:
        raw_text = raw_text[start_idx:]
        raw_text = raw_text[raw_text.find('\n')+1:]
    if end_idx != -1:
        raw_text = raw_text[:raw_text.find(end_marker)]

    chapters = re.split(r'\n(?=CHAPTER\s+[IVXLCDM0-9]+)', raw_text, flags=re.IGNORECASE)
    chapters = [c.strip() for c in chapters if len(c.strip()) > 200]

    return chapters

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

for title, gutenberg_id in gutenberg_ids.items():
    print(f"Fetching: {title}...")

    book_row = cursor.execute("SELECT id FROM books WHERE title = ?", (title,)).fetchone()
    if not book_row:
        print(f"  Skipped — '{title}' not found in books table.")
        continue
    book_id = book_row[0]

    try:
        raw_text = download_text(gutenberg_id)
        chapters = clean_and_split_chapters(raw_text)

        if len(chapters) == 0:
            print(f"  Warning: no chapters split for {title}, skipping.")
            continue

        cursor.execute("DELETE FROM chapters WHERE book_id = ?", (book_id,))

        for i, chapter_text in enumerate(chapters, start=1):
            first_line = chapter_text.split('\n')[0].strip()
            chapter_title = first_line if len(first_line) < 60 else f"Chapter {i}"

            cursor.execute(
                "INSERT INTO chapters (book_id, chapter_number, title, content) VALUES (?, ?, ?, ?)",
                (book_id, i, chapter_title, chapter_text)
            )

        conn.commit()
        print(f"  Added {len(chapters)} chapters for {title}.")

    except Exception as e:
        print(f"  Error fetching {title}: {e}")

conn.close()
print("Done!")
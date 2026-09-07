import sqlite3
import requests
import re

DB_NAME = "database.db"

books_to_fix = {
    "The Adventures of Sherlock Holmes": 1661,
    "The Great Gatsby": 64317,
    "White Nights": 600,
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

def strip_boilerplate(raw_text):
    start_marker = "*** START OF"
    end_marker = "*** END OF"

    start_idx = raw_text.find(start_marker)
    end_idx = raw_text.find(end_marker)

    if start_idx != -1:
        raw_text = raw_text[start_idx:]
        raw_text = raw_text[raw_text.find('\n')+1:]
    if end_idx != -1:
        raw_text = raw_text[:raw_text.find(end_marker)]

    return raw_text

def try_split(raw_text, pattern):
    parts = re.split(pattern, raw_text, flags=re.IGNORECASE | re.MULTILINE)
    parts = [p.strip() for p in parts if len(p.strip()) > 300]
    return parts

# Different books use different chapter-marker styles.
# We try several patterns and use whichever gives the most reasonable split.
patterns_to_try = [
    r'\n(?=CHAPTER\s+[IVXLCDM0-9]+)',      # CHAPTER I, CHAPTER 1
    r'\n(?=Chapter\s+[IVXLCDM0-9]+)',      # Chapter I (mixed case)
    r'\n(?=[IVXLCDM]+\.\s)',               # I.  II.  III. (roman numeral + period)
    r'\n(?=\d+\.\s)',                       # 1.  2.  3.
    r'\n(?=ADVENTURE\s+[IVXLCDM0-9]+)',    # Sherlock Holmes uses "ADVENTURE" sometimes
]

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

for title, gutenberg_id in books_to_fix.items():
    print(f"Fixing: {title}...")

    book_row = cursor.execute("SELECT id FROM books WHERE title = ?", (title,)).fetchone()
    if not book_row:
        print(f"  Skipped — not found in books table.")
        continue
    book_id = book_row[0]

    try:
        raw_text = download_text(gutenberg_id)
        cleaned = strip_boilerplate(raw_text)

        best_chapters = [cleaned]  # fallback: whole book as one chapter
        best_count = 1

        for pattern in patterns_to_try:
            result = try_split(cleaned, pattern)
            if len(result) > best_count:
                best_chapters = result
                best_count = len(result)

        cursor.execute("DELETE FROM chapters WHERE book_id = ?", (book_id,))

        for i, chapter_text in enumerate(best_chapters, start=1):
            first_line = chapter_text.split('\n')[0].strip()
            chapter_title = first_line if len(first_line) < 60 else f"Chapter {i}"

            cursor.execute(
                "INSERT INTO chapters (book_id, chapter_number, title, content) VALUES (?, ?, ?, ?)",
                (book_id, i, chapter_title, chapter_text)
            )

        conn.commit()
        print(f"  Added {best_count} chapters for {title}.")

    except Exception as e:
        print(f"  Error fixing {title}: {e}")

conn.close()
print("Done!")
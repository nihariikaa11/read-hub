import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Popular books - cover/description only (copyrighted, no full text)
popular_books = [
    ("The Alchemist", "Paulo Coelho", "A shepherd boy's journey to find his personal legend and treasure in the Egyptian desert.", "alchemist.jpg"),
    ("The Psychology of Money", "Morgan Housel", "Timeless lessons on wealth, greed, and happiness through the lens of behavior, not finance textbooks.", "psychology_of_money.jpg"),
    ("The Mountain Is You", "Brianna Wiest", "A guide to self-sabotage and transforming self-destructive behavior into personal growth.", "mountain_is_you.jpg"),
    ("Atomic Habits", "James Clear", "A practical guide to building good habits and breaking bad ones through tiny changes.", "atomic_habits.jpg"),
    ("It Ends With Us", "Colleen Hoover", "A powerful story about love, resilience, and breaking generational cycles.", "it_ends_with_us.jpg"),
    ("The Silent Patient", "Alex Michaelides", "A psychological thriller about a woman's shocking act of violence and the therapist obsessed with treating her.", "silent_patient.jpg"),
    ("Ikigai", "Hector Garcia", "A Japanese concept of finding purpose and joy in everyday life.", "ikigai.jpg"),
    ("Rich Dad Poor Dad", "Robert Kiyosaki", "Lessons on financial literacy and building wealth through smart money mindset.", "rich_dad_poor_dad.jpg"),
    ("Who Moved My Cheese", "Spencer Johnson", "A simple parable about handling change in work and life.", "who_moved_my_cheese.jpg"),
    ("To Kill a Mockingbird", "Harper Lee", "A powerful story of racial injustice and childhood innocence in the American South.", "mockingbird.jpg"),
    ("And Then There Were None", "Agatha Christie", "Ten strangers trapped on an island, each hiding a secret, are killed one by one.", "and_then_there_were_none.jpg"),
    ("Gone Girl", "Gillian Flynn", "A marriage turns dark and twisted after a wife's mysterious disappearance.", "gone_girl.jpg"),
    ("Project Hail Mary", "Andy Weir", "A lone astronaut must save humanity in this gripping science fiction survival story.", "project_hail_mary.jpg"),
    ("Harry Potter and the Philosopher's Stone", "J.K. Rowling", "A young boy discovers he's a wizard and begins his journey at Hogwarts.", "harry_potter_1.jpg"),
    ("Steve Jobs", "Walter Isaacson", "The definitive biography of Apple's co-founder, based on exclusive interviews.", "steve_jobs.jpg"),
    ("The Little Prince", "Antoine de Saint-Exupery", "A poetic tale of a young prince exploring life, love, and loss across the universe.", "little_prince.jpg"),
    ("Wings of Fire", "A.P.J. Abdul Kalam", "The inspiring autobiography of India's Missile Man and former President.", "wings_of_fire.jpg"),
    ("My Journey", "A.P.J. Abdul Kalam", "Transforming dreams into actions — reflections from Dr. Kalam's remarkable life.", "my_journey.jpg"),
    ("Only Dull People Are Brilliant at Breakfast", "Oscar Wilde", "Witty essays and reflections capturing Wilde's sharp humor and observations on life.", "dull_people.jpg"),
]

for title, author, desc, cover in popular_books:
    cursor.execute(
        "INSERT INTO books (title, author, description, cover_image, uploaded_by) VALUES (?, ?, ?, ?, ?)",
        (title, author, desc, cover, None)
    )

# Public domain books - full readable content (from Project Gutenberg)
gutenberg_books = [
    ("Pride and Prejudice", "Jane Austen", "A witty exploration of manners, upbringing, morality, and marriage in Georgian England.", "pride_and_prejudice.jpg"),
    ("Alice in Wonderland", "Lewis Carroll", "A young girl falls through a rabbit hole into a fantastical world of curious creatures.", "alice.jpg"),
    ("Frankenstein", "Mary Shelley", "A scientist creates a living being, unleashing a story of ambition, horror, and humanity.", "frankenstein.jpg"),
    ("Dracula", "Bram Stoker", "The classic gothic horror tale of Count Dracula's terrifying reach from Transylvania to England.", "dracula.jpg"),
    ("The Adventures of Sherlock Holmes", "Arthur Conan Doyle", "The legendary detective solves mysteries no one else can crack.", "sherlock.jpg"),
    ("The Great Gatsby", "F. Scott Fitzgerald", "A tragic tale of wealth, love, and the American Dream in the Jazz Age.", "gatsby.jpg"),
    ("Moby Dick", "Herman Melville", "Captain Ahab's obsessive hunt for the great white whale.", "moby_dick.jpg"),
    ("Jane Eyre", "Charlotte Bronte", "An orphan's journey through hardship to independence and love.", "jane_eyre.jpg"),
    ("White Nights", "Fyodor Dostoevsky", "A lonely dreamer falls in love over four nights in St. Petersburg.", "white_nights.jpg"),
    ("Metamorphosis", "Franz Kafka", "A man wakes up transformed into a giant insect, and must confront his new reality.", "metamorphosis.jpg"),
    ("Crime and Punishment", "Fyodor Dostoevsky", "A poor student's descent into guilt and redemption after committing murder.", "crime_and_punishment.jpg"),
    ("As a Man Thinketh", "James Allen", "A short, powerful essay on how thoughts shape character and destiny.", "as_a_man_thinketh.jpg"),
]

for title, author, desc, cover in gutenberg_books:
    cursor.execute(
        "INSERT INTO books (title, author, description, cover_image, uploaded_by) VALUES (?, ?, ?, ?, ?)",
        (title, author, desc, cover, None)
    )
    book_id = cursor.lastrowid

    cursor.execute(
        "INSERT INTO chapters (book_id, chapter_number, title, content) VALUES (?, ?, ?, ?)",
        (book_id, 1, "Chapter 1", "Sample chapter content will go here — we'll replace this with real text from Project Gutenberg.")
    )

conn.commit()
conn.close()

print("Books added successfully!")
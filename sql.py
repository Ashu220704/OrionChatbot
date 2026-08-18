import sqlite3

connection = sqlite3.connect(
    "AI_chatbot.db",
    check_same_thread=False
)

cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS Conversations
(
    ThreadId TEXT PRIMARY KEY,
    Title TEXT NOT NULL,
    CreatedOn DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

connection.commit()
import sqlite3

connection = sqlite3.connect("habeshago.db")
cursor = connection.cursor()

MY_TELEGRAM_ID = 1253795281

cursor.execute(
    """
    DELETE FROM drivers
    WHERE telegram_id != ?
    """,
    (MY_TELEGRAM_ID,),
)

connection.commit()

print(f"✅ Deleted {cursor.rowcount} test driver(s).")

connection.close()
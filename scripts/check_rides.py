from app.database.database import create_connection

connection = create_connection()
cursor = connection.cursor()

cursor.execute("SELECT * FROM rides")

rows = cursor.fetchall()

print("\n===== RIDES TABLE =====")

for row in rows:
    print(row)

connection.close()
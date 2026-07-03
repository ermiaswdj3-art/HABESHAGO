from app.database.database import create_connection

connection = create_connection()
cursor = connection.cursor()

cursor.execute("""
UPDATE drivers
SET is_available = 1
""")

connection.commit()

print("✅ All drivers are AVAILABLE again.")

connection.close()
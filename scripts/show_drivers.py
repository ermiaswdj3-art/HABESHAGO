from app.database.database import create_connection

connection = create_connection()
cursor = connection.cursor()

cursor.execute("""
SELECT
    telegram_id,
    full_name,
    plate_number,
    is_available
FROM drivers
""")

print("\n===== DRIVERS TABLE =====")

for row in cursor.fetchall():
    print(row)

connection.close()
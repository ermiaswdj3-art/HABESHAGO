from app.database.database import create_connection

connection = create_connection()
cursor = connection.cursor()

cursor.execute(
    """
    DELETE FROM drivers
    WHERE telegram_id = 809111423
    """
)

connection.commit()

print("✅ Driver (telegram_id=809111423) deleted.")

connection.close()
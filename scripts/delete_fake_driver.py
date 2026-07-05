from app.database.database import create_connection

connection = create_connection()
cursor = connection.cursor()

cursor.execute(
    """
    DELETE FROM drivers
    WHERE telegram_id = 1001
    """
)

connection.commit()

print("✅ Fake driver (telegram_id=1001) deleted.")

connection.close()
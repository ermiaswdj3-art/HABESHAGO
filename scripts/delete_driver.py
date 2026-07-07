from app.database.database import create_connection

connection = create_connection()
cursor = connection.cursor()

telegram_id = 1253795281

cursor.execute(
    "DELETE FROM drivers WHERE telegram_id = ?",
    (telegram_id,),
)

connection.commit()

print("✅ Driver deleted successfully.")

connection.close()
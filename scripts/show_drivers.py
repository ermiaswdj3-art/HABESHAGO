from app.database.database import create_connection

connection = create_connection()
cursor = connection.cursor()

cursor.execute("""
SELECT
    telegram_id,
    full_name,
    phone_number,
    vehicle,
    vehicle_year,
    vehicle_color,
    plate_number,
    rating,
    is_available,
    latitude,
    longitude
FROM drivers
""")

print("\n================== DRIVERS TABLE ==================\n")

for row in cursor.fetchall():

    print(f"Telegram ID : {row[0]}")
    print(f"Name        : {row[1]}")
    print(f"Phone       : {row[2]}")
    print(f"Vehicle     : {row[3]}")
    print(f"Year        : {row[4]}")
    print(f"Color       : {row[5]}")
    print(f"Plate       : {row[6]}")
    print(f"Rating      : {row[7]}")
    print(f"Available   : {bool(row[8])}")
    print(f"Latitude    : {row[9]}")
    print(f"Longitude   : {row[10]}")
    print("-" * 50)

connection.close()
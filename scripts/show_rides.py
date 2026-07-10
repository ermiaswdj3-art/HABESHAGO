from app.database.database import create_connection

connection = create_connection()
cursor = connection.cursor()

cursor.execute("""
SELECT
    id,
    passenger_id,
    driver_id,
    status,
    distance,
    fare
FROM rides
ORDER BY id DESC
""")

rides = cursor.fetchall()

print("\n================ RIDES TABLE ================\n")

if not rides:
    print("No rides found.")

for ride in rides:
    print(f"Ride ID      : {ride[0]}")
    print(f"Passenger ID : {ride[1]}")
    print(f"Driver ID    : {ride[2]}")
    print(f"Status       : {ride[3]}")
    print(f"Distance     : {ride[4]}")
    print(f"Fare         : {ride[5]}")
    print("-------------------------------------------")

connection.close()
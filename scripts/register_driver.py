from app.database.driver_repository import register_driver


def main():
    register_driver(
        telegram_id=1001,
        full_name="Abebe",
        phone_number="+251911111111",
        vehicle="Toyota Vitz",
        vehicle_color="White",
        plate_number="AA-12345",
        latitude=8.960000,
        longitude=38.770000,
    )

    print("✅ Driver registered successfully!")


if __name__ == "__main__":
    main()
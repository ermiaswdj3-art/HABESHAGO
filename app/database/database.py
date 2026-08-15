import os
import sqlite3

from app.database.backend import (
    POSTGRESQL_BACKEND,
    SQLITE_BACKEND,
    get_database_backend,
    validate_database_configuration,
)

from app.database.postgresql import (
    create_postgresql_connection,
)

from app.database.postgresql_schema import (
    create_postgresql_tables,
)

from app.database.errors import (
    HABESHAGODatabaseError,
)

DATABASE_NAME = "habeshago.db"




# Backend-neutral database failure contract.
#
# SQLite currently exposes its native DB-API error family,
# while PostgreSQL failures crossing the compatibility
# boundary use HABESHAGODatabaseError.
DATABASE_ERROR_TYPES = (
    sqlite3.Error,
    HABESHAGODatabaseError,
)

def create_connection():
    """
    Create and return the canonical HABESHAGO
    database connection.

    SQLite remains the active development backend.

    PostgreSQL configuration is recognized by the
    platform contract but is intentionally rejected
    until the production PostgreSQL connection adapter
    and SQL compatibility layer are installed.
    """

    backend = validate_database_configuration()

    if backend == POSTGRESQL_BACKEND:
        return create_postgresql_connection()

    if backend != SQLITE_BACKEND:
        raise RuntimeError(
            "Unsupported HABESHAGO database backend."
        )

    database_path = os.path.abspath(
        DATABASE_NAME
    )

    print(
        "\n=============================="
    )
    print(
        "DATABASE BACKEND:",
        backend,
    )
    print(
        "DATABASE:",
        database_path,
    )
    print(
        "==============================\n"
    )

    return sqlite3.connect(
        database_path
    )


def get_table_columns(
    cursor,
    table_name,
):
    """
    Return the names of all columns in a database table.
    """

    cursor.execute(
        f"PRAGMA table_info({table_name})"
    )

    return {
        row[1]
        for row in cursor.fetchall()
    }


def add_column_if_missing(
    cursor,
    table_name,
    column_name,
    column_definition,
):
    """
    Add a database column only when it does not exist.

    The table name, column name and definition are supplied
    internally by HABESHAGO—not from user input.
    """

    existing_columns = get_table_columns(
        cursor,
        table_name,
    )

    if column_name in existing_columns:
        return False

    cursor.execute(
        f"""
        ALTER TABLE {table_name}
        ADD COLUMN {column_name} {column_definition}
        """
    )

    print(
        "✅ Database migration added column: "
        f"{table_name}.{column_name}"
    )

    return True


def migrate_rides_table(
    cursor,
):
    """
    Safely upgrade an existing rides table.

    This migration may run every time HABESHAGO starts.
    Existing columns are never added twice.
    """

    add_column_if_missing(
        cursor,
        "rides",
        "created_at",
        "TIMESTAMP",
    )

    # ==========================================
    # RIDE SETTLEMENT PLATFORM
    # ==========================================

    settlement_status_added = (
        add_column_if_missing(
            cursor,
            "rides",
            "settlement_status",
            "TEXT DEFAULT 'not_settled'",
        )
    )

    add_column_if_missing(
        cursor,
        "rides",
        "settled_at",
        "TIMESTAMP",
    )

    add_column_if_missing(
        cursor,
        "rides",
        "settlement_reference",
        "TEXT",
    )

    add_column_if_missing(
        cursor,
        "rides",
        "requested_at",
        "TIMESTAMP",
    )

    add_column_if_missing(
        cursor,
        "rides",
        "accepted_at",
        "TIMESTAMP",
    )

    add_column_if_missing(
        cursor,
        "rides",
        "arrived_at",
        "TIMESTAMP",
    )

    add_column_if_missing(
        cursor,
        "rides",
        "started_at",
        "TIMESTAMP",
    )

    add_column_if_missing(
        cursor,
        "rides",
        "completed_at",
        "TIMESTAMP",
    )

    add_column_if_missing(
        cursor,
        "rides",
        "cancelled_at",
        "TIMESTAMP",
    )

    add_column_if_missing(
        cursor,
        "rides",
        "expired_at",
        "TIMESTAMP",
    )

    cursor.execute(
        """
        UPDATE rides
        SET requested_at = created_at
        WHERE requested_at IS NULL
          AND created_at IS NOT NULL
        """
    )

    cursor.execute(
        """
        UPDATE rides
        SET completed_at = created_at
        WHERE completed_at IS NULL
          AND created_at IS NOT NULL
          AND status = 'TRIP_COMPLETED'
        """
    )

    # Preserve historically completed rides as settled
    # only when their stored financial arithmetic is
    # already internally consistent.
    #
    # Legacy exceptions such as Ride #1 remain
    # not_settled and are not silently rewritten.
    if settlement_status_added:
        cursor.execute(
            """
            UPDATE rides
            SET
                settlement_status = 'settled',
                settled_at = COALESCE(
                    completed_at,
                    created_at
                ),
                settlement_reference = (
                    'LEGACY-RIDE-' || id
                )
            WHERE status = 'TRIP_COMPLETED'
              AND commission_amount > 0
              AND ABS(
                    driver_earnings
                    - (
                        fare
                        - commission_amount
                    )
                  ) <= 0.01
            """
        )


def migrate_drivers_table(
    cursor,
):
    """
    Safely upgrade the drivers table with the
    HABESHAGO registration and verification contract.

    Existing development drivers are preserved as
    approved when the verification columns are first
    introduced.

    New registrations use pending verification defaults.
    """

    registration_status_added = (
        add_column_if_missing(
            cursor,
            "drivers",
            "registration_status",
            "TEXT DEFAULT 'verification_pending'",
        )
    )

    identity_status_added = (
        add_column_if_missing(
            cursor,
            "drivers",
            "identity_verification_status",
            "TEXT DEFAULT 'pending'",
        )
    )

    vehicle_status_added = (
        add_column_if_missing(
            cursor,
            "drivers",
            "vehicle_verification_status",
            "TEXT DEFAULT 'pending'",
        )
    )

    add_column_if_missing(
        cursor,
        "drivers",
        "registration_submitted_at",
        "TIMESTAMP",
    )

    add_column_if_missing(
        cursor,
        "drivers",
        "verified_at",
        "TIMESTAMP",
    )

    add_column_if_missing(
        cursor,
        "drivers",
        "rejection_reason",
        "TEXT",
    )

    # ==========================================
    # DRIVER AVAILABILITY & LIFECYCLE PLATFORM
    # ==========================================

    operational_status_added = (
        add_column_if_missing(
            cursor,
            "drivers",
            "operational_status",
            "TEXT DEFAULT 'offline'",
        )
    )

    add_column_if_missing(
        cursor,
        "drivers",
        "operational_status_updated_at",
        "TIMESTAMP",
    )

    # ==========================================
    # SHARED LIVE LOCATION AUTHORITY
    # ==========================================

    add_column_if_missing(
        cursor,
        "drivers",
        "live_location_updated_at",
        "TIMESTAMP",
    )

        # Preserve the existing operational meaning of
    # drivers created before Commit #76.
    #
    # This runs only when operational_status is first
    # introduced, so later platform transitions are
    # never overwritten during application startup.
    if operational_status_added:
        cursor.execute(
            """
            UPDATE drivers
            SET
                operational_status = CASE
                    WHEN is_online = 0
                        THEN 'offline'

                    WHEN is_online = 1
                         AND is_available = 1
                        THEN 'available'

                    ELSE 'unavailable'
                END,

                operational_status_updated_at = COALESCE(
                    operational_status_updated_at,
                    CURRENT_TIMESTAMP
                )
            """
        )

    # Preserve drivers created before Commit #73.
    # These updates run only when the related status
    # columns are introduced for the first time.

    if registration_status_added:
        cursor.execute(
            """
            UPDATE drivers
            SET registration_status = 'approved',
                registration_submitted_at = COALESCE(
                    registration_submitted_at,
                    created_at
                ),
                verified_at = COALESCE(
                    verified_at,
                    created_at
                )
            """
        )

    if identity_status_added:
        cursor.execute(
            """
            UPDATE drivers
            SET identity_verification_status = 'verified'
            """
        )

    if vehicle_status_added:
        cursor.execute(
            """
            UPDATE drivers
            SET vehicle_verification_status = 'verified'
            """
        )


def migrate_existing_driver_vehicles(
    cursor,
):
    """
    Create canonical vehicle records for drivers that
    existed before the Vehicle Platform was introduced.

    Existing driver vehicle columns remain available for
    backward compatibility during the migration period.
    """

    cursor.execute(
        """
        SELECT
            telegram_id,
            vehicle,
            vehicle_year,
            vehicle_color,
            plate_number,
            vehicle_verification_status,
            created_at
        FROM drivers
        """
    )

    driver_records = cursor.fetchall()

    for driver_record in driver_records:
        (
            driver_id,
            vehicle_name,
            vehicle_year,
            vehicle_color,
            plate_number,
            verification_status,
            created_at,
        ) = driver_record

        clean_vehicle_name = str(
            vehicle_name or ""
        ).strip()

        vehicle_parts = clean_vehicle_name.split(
            maxsplit=1
        )

        if len(vehicle_parts) == 2:
            brand = vehicle_parts[0]
            model = vehicle_parts[1]
        elif len(vehicle_parts) == 1:
            brand = vehicle_parts[0]
            model = "Unknown"
        else:
            brand = "Unknown"
            model = "Unknown"

        clean_verification_status = (
            verification_status
            if verification_status
            in {
                "pending",
                "verified",
                "rejected",
                "suspended",
            }
            else "pending"
        )

        cursor.execute(
            """
            INSERT OR IGNORE INTO vehicles (
                driver_id,
                vehicle_type,
                brand,
                model,
                manufacturing_year,
                color,
                plate_number,
                category,
                verification_status,
                is_active,
                created_at,
                updated_at
            )
            VALUES (
                ?,
                'legacy',
                ?,
                ?,
                ?,
                ?,
                ?,
                'standard',
                ?,
                1,
                COALESCE(
                    ?,
                    CURRENT_TIMESTAMP
                ),
                CURRENT_TIMESTAMP
            )
            """,
            (
                driver_id,
                brand,
                model,
                vehicle_year,
                vehicle_color,
                plate_number,
                clean_verification_status,
                created_at,
            ),
        )

def create_tables():
    """
    Create and safely upgrade all HABESHAGO database tables.

    SQLite retains the historical migration authority.

    PostgreSQL uses only the canonical fresh-schema
    authority and never executes legacy SQLite migrations.
    """

    backend = validate_database_configuration()

    if backend == POSTGRESQL_BACKEND:
        connection = create_connection()

        try:
            return create_postgresql_tables(
                connection
            )

        finally:
            connection.close()

    connection = create_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "PRAGMA foreign_keys = ON"
        )

        # ======================================
        # PASSENGERS TABLE
        # ======================================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS passengers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                phone_number TEXT,

                created_at TIMESTAMP
                    DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # ======================================
        # DRIVERS TABLE
        # ======================================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS drivers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,

                full_name TEXT NOT NULL,
                phone_number TEXT,

                vehicle TEXT NOT NULL,
                vehicle_year INTEGER NOT NULL,
                vehicle_color TEXT NOT NULL,
                plate_number TEXT UNIQUE NOT NULL,

                rating REAL DEFAULT 5.0,

                registration_status TEXT
                    DEFAULT 'verification_pending',

                identity_verification_status TEXT
                    DEFAULT 'pending',

                vehicle_verification_status TEXT
                    DEFAULT 'pending',

                registration_submitted_at TIMESTAMP,
                verified_at TIMESTAMP,
                rejection_reason TEXT,

                is_available INTEGER DEFAULT 0,
                is_online INTEGER DEFAULT 0,

                operational_status TEXT
                    DEFAULT 'offline',

                operational_status_updated_at TIMESTAMP,

                latitude REAL NOT NULL,
                longitude REAL NOT NULL,

                live_location_updated_at TIMESTAMP,

                created_at TIMESTAMP
                    DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # Safely upgrade databases created before
        # the Driver Registration and Verification
        # Platform was introduced.
        migrate_drivers_table(
            cursor
        )

        # ======================================
        # VEHICLES TABLE
        # ======================================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS vehicles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                driver_id INTEGER NOT NULL,

                vehicle_type TEXT NOT NULL,
                brand TEXT NOT NULL,
                model TEXT NOT NULL,

                manufacturing_year INTEGER NOT NULL,
                color TEXT NOT NULL,

                plate_type TEXT,
                plate_region TEXT,
                plate_number TEXT UNIQUE NOT NULL,

                category TEXT NOT NULL
                    DEFAULT 'standard',

                verification_status TEXT NOT NULL
                    DEFAULT 'pending',

                is_active INTEGER NOT NULL
                    DEFAULT 1,

                created_at TIMESTAMP
                    DEFAULT CURRENT_TIMESTAMP,

                updated_at TIMESTAMP
                    DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (driver_id)
                    REFERENCES drivers (telegram_id)
            )
            """
        )

        # Safely migrate vehicle information from
        # driver records created before Commit #74.
        migrate_existing_driver_vehicles(
            cursor
        )

        # ======================================
        # RIDES TABLE
        # ======================================
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS rides (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                passenger_id INTEGER NOT NULL,
                driver_id INTEGER NOT NULL,

                pickup_latitude REAL NOT NULL,
                pickup_longitude REAL NOT NULL,

                destination_latitude REAL NOT NULL,
                destination_longitude REAL NOT NULL,

                distance REAL NOT NULL,
                fare REAL NOT NULL,

                service_type TEXT DEFAULT 'fuel',

                commission_rate REAL DEFAULT 0.10,
                commission_amount REAL DEFAULT 0,
                driver_earnings REAL DEFAULT 0,

                settlement_status TEXT
                    DEFAULT 'not_settled',

                settled_at TIMESTAMP,

                settlement_reference TEXT,

                status TEXT DEFAULT 'REQUESTED',

                driver_rating INTEGER,
                passenger_rating INTEGER,

                created_at TIMESTAMP
                    DEFAULT CURRENT_TIMESTAMP,

                requested_at TIMESTAMP
                    DEFAULT CURRENT_TIMESTAMP,

                accepted_at TIMESTAMP,
                arrived_at TIMESTAMP,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                cancelled_at TIMESTAMP,
                expired_at TIMESTAMP,

                FOREIGN KEY (passenger_id)
                    REFERENCES passengers (telegram_id),

                FOREIGN KEY (driver_id)
                    REFERENCES drivers (telegram_id)
            )
            """
        )

        # Safely upgrade databases created by
        # earlier HABESHAGO commits.
        migrate_rides_table(
            cursor
        )

        # ======================================
        # RIDE FINANCIAL ALLOCATIONS TABLE
        # ======================================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS
            ride_financial_allocations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                ride_id INTEGER UNIQUE NOT NULL,

                passenger_fare TEXT NOT NULL,

                commission_rate TEXT NOT NULL,

                commission_amount TEXT NOT NULL,

                driver_earnings TEXT NOT NULL,

                currency TEXT NOT NULL,

                commission_policy_version TEXT NOT NULL,

                commission_policy_reference TEXT NOT NULL,

                created_at TIMESTAMP
                    DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (ride_id)
                    REFERENCES rides (id)
            )
            """
        )

        # ======================================
        # RIDE OFFERS TABLE
        # ======================================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ride_offers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                offer_reference TEXT UNIQUE NOT NULL,

                passenger_id INTEGER NOT NULL,
                driver_id INTEGER NOT NULL,

                pickup_latitude REAL NOT NULL,
                pickup_longitude REAL NOT NULL,

                destination_latitude REAL NOT NULL,
                destination_longitude REAL NOT NULL,

                distance REAL NOT NULL,
                pickup_distance REAL NOT NULL,

                pickup_eta INTEGER NOT NULL,
                trip_eta INTEGER NOT NULL,

                fare REAL NOT NULL,

                payment_method TEXT NOT NULL
                    DEFAULT 'Cash',

                service_type TEXT NOT NULL
                    DEFAULT 'fuel',

                status TEXT NOT NULL
                    DEFAULT 'PENDING',

                accepted_ride_id INTEGER,

                created_at TIMESTAMP
                    DEFAULT CURRENT_TIMESTAMP,

                expires_at TIMESTAMP NOT NULL,

                accepted_at TIMESTAMP,
                rejected_at TIMESTAMP,
                expired_at TIMESTAMP,
                cancelled_at TIMESTAMP,

                FOREIGN KEY (passenger_id)
                    REFERENCES passengers (telegram_id),

                FOREIGN KEY (driver_id)
                    REFERENCES drivers (telegram_id),

                FOREIGN KEY (accepted_ride_id)
                    REFERENCES rides (id)
            )
            """
        )

        # ======================================
        # DRIVER ADMINISTRATION ACTIONS TABLE
        # ======================================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS
            driver_admin_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                action_reference TEXT
                    UNIQUE NOT NULL,

                driver_id INTEGER NOT NULL,
                actor_id INTEGER NOT NULL,

                action_type TEXT NOT NULL,

                previous_registration_status TEXT,
                new_registration_status TEXT,

                previous_identity_status TEXT,
                new_identity_status TEXT,

                previous_vehicle_status TEXT,
                new_vehicle_status TEXT,

                previous_operational_status TEXT,
                new_operational_status TEXT,

                reason TEXT,

                created_at TIMESTAMP
                    DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (driver_id)
                    REFERENCES drivers (telegram_id)
            )
            """
        )

        # ======================================
        # PRICING CONFIGURATIONS TABLE
        # ======================================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS
            pricing_configurations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                configuration_version TEXT
                    UNIQUE NOT NULL,

                city TEXT NOT NULL,

                service_type TEXT NOT NULL,
                ride_category TEXT NOT NULL,

                currency TEXT NOT NULL,

                base_fare TEXT NOT NULL,
                price_per_km TEXT NOT NULL,
                price_per_minute TEXT NOT NULL,

                waiting_price_per_minute TEXT
                    NOT NULL,

                minimum_fare TEXT NOT NULL,

                rounding_policy TEXT NOT NULL,
                rounding_multiple TEXT NOT NULL,

                pricing_policy TEXT NOT NULL,
                surge_policy TEXT NOT NULL,

                effective_from TEXT NOT NULL,
                effective_until TEXT,

                is_active INTEGER NOT NULL
                    DEFAULT 1
                    CHECK (
                        is_active IN (0, 1)
                    ),

                created_at TIMESTAMP
                    DEFAULT CURRENT_TIMESTAMP,

                updated_at TIMESTAMP
                    DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # ======================================
        # PAYMENT OBLIGATIONS TABLE
        # ======================================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS
            payment_obligations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                obligation_reference TEXT
                    UNIQUE NOT NULL,

                source_type TEXT NOT NULL,
                source_reference TEXT NOT NULL,

                amount TEXT NOT NULL,
                currency TEXT NOT NULL,

                pricing_quote_id TEXT,
                pricing_request_id TEXT,

                created_at TEXT NOT NULL,

                contract_version TEXT NOT NULL
            )
            """
        )

        # ======================================
        # PAYMENT REQUESTS TABLE
        # ======================================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS
            payment_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                request_reference TEXT
                    UNIQUE NOT NULL,

                obligation_reference TEXT NOT NULL,

                payer_id INTEGER NOT NULL,

                payment_method TEXT NOT NULL,
                status TEXT NOT NULL,

                requested_at TEXT NOT NULL,

                contract_version TEXT NOT NULL,

                FOREIGN KEY (
                    obligation_reference
                )
                    REFERENCES payment_obligations (
                        obligation_reference
                    )
            )
            """
        )

        # ======================================
        # PAYMENT INTENTS TABLE
        # ======================================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS
            payment_intents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                intent_reference TEXT
                    UNIQUE NOT NULL,

                request_reference TEXT NOT NULL,

                provider TEXT NOT NULL,
                status TEXT NOT NULL,

                created_at TEXT NOT NULL,
                expires_at TEXT,

                contract_version TEXT NOT NULL,

                FOREIGN KEY (
                    request_reference
                )
                    REFERENCES payment_requests (
                        request_reference
                    )
            )
            """
        )

        # ======================================
        # PAYMENT TRANSACTIONS TABLE
        # ======================================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS
            payment_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                transaction_reference TEXT
                    UNIQUE NOT NULL,

                intent_reference TEXT NOT NULL,

                provider TEXT NOT NULL,
                payment_method TEXT NOT NULL,

                amount TEXT NOT NULL,
                currency TEXT NOT NULL,

                status TEXT NOT NULL,

                payer_id INTEGER NOT NULL,

                obligation_reference TEXT NOT NULL,

                created_at TEXT NOT NULL,

                provider_reference TEXT,
                failure_reason TEXT,

                contract_version TEXT NOT NULL,

                FOREIGN KEY (
                    intent_reference
                )
                    REFERENCES payment_intents (
                        intent_reference
                    ),

                FOREIGN KEY (
                    obligation_reference
                )
                    REFERENCES payment_obligations (
                        obligation_reference
                    )
            )
            """
        )

        # ======================================
        # PAYMENT VERIFICATIONS TABLE
        # ======================================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS
            payment_verifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                transaction_reference TEXT
                    UNIQUE NOT NULL,

                provider TEXT NOT NULL,

                provider_reference TEXT NOT NULL,

                status TEXT NOT NULL,

                verified_at TEXT NOT NULL,

                matched_fields TEXT NOT NULL,

                mismatched_fields TEXT NOT NULL,

                reason TEXT,

                FOREIGN KEY (
                    transaction_reference
                )
                    REFERENCES payment_transactions (
                        transaction_reference
                    )
            )
            """
        )

        # ======================================
        # PAYMENT RECONCILIATIONS TABLE
        # ======================================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS
            payment_reconciliations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                transaction_reference TEXT
                    UNIQUE NOT NULL,

                provider TEXT NOT NULL,

                provider_reference TEXT NOT NULL,

                status TEXT NOT NULL,

                reconciled_at TEXT NOT NULL,

                reason TEXT,

                FOREIGN KEY (
                    transaction_reference
                )
                    REFERENCES payment_transactions (
                        transaction_reference
                    )
            )
            """
        )

        # ======================================
        # PASSENGER PLACES TABLE
        # ======================================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS passenger_places (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                passenger_id INTEGER NOT NULL,

                place_type TEXT NOT NULL,
                place_name TEXT NOT NULL,
                full_address TEXT,

                latitude REAL NOT NULL,
                longitude REAL NOT NULL,

                created_at TIMESTAMP
                    DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (passenger_id)
                    REFERENCES passengers (telegram_id)
            )
            """
        )

        # ======================================
        # DATABASE INDEXES
        # ======================================

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_rides_passenger_id
            ON rides (passenger_id)
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_rides_driver_id
            ON rides (driver_id)
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_rides_status
            ON rides (status)
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_rides_created_at
            ON rides (created_at)
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_rides_completed_at
            ON rides (completed_at)
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_passenger_places_passenger
            ON passenger_places (
                passenger_id,
                place_type
            )
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_drivers_registration_status
            ON drivers (
                registration_status
            )
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_drivers_dispatch_eligibility
            ON drivers (
                registration_status,
                identity_verification_status,
                vehicle_verification_status,
                is_online,
                is_available
            )
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_vehicles_driver_id
            ON vehicles (
                driver_id
            )
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_vehicles_active
            ON vehicles (
                driver_id,
                is_active
            )
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_vehicles_verification
            ON vehicles (
                verification_status
            )
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_vehicles_category
            ON vehicles (
                category
            )
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_rides_settlement_status
            ON rides (
                settlement_status
            )
            """
        )

        cursor.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS
            idx_rides_settlement_reference
            ON rides (
                settlement_reference
            )
            WHERE settlement_reference IS NOT NULL
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_rides_driver_settlement
            ON rides (
                driver_id,
                settlement_status,
                settled_at
            )
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_drivers_operational_status
            ON drivers (
                operational_status
            )
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_drivers_operational_eligibility
            ON drivers (
                registration_status,
                identity_verification_status,
                vehicle_verification_status,
                operational_status,
                is_online,
                is_available
            )
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_ride_offers_driver_status
            ON ride_offers (
                driver_id,
                status
            )
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_driver_admin_actions_driver
            ON driver_admin_actions (
                driver_id,
                created_at
            )
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_driver_admin_actions_actor
            ON driver_admin_actions (
                actor_id,
                created_at
            )
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_driver_admin_actions_type
            ON driver_admin_actions (
                action_type,
                created_at
            )
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_pricing_config_scope
            ON pricing_configurations (
                city,
                service_type,
                ride_category
            )
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_pricing_config_active_scope
            ON pricing_configurations (
                city,
                service_type,
                ride_category,
                is_active
            )
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_pricing_config_effective_window
            ON pricing_configurations (
                effective_from,
                effective_until
            )
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_pricing_config_policy
            ON pricing_configurations (
                pricing_policy,
                surge_policy
            )
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_ride_offers_passenger_status
            ON ride_offers (
                passenger_id,
                status
            )
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_ride_offers_expiration
            ON ride_offers (
                status,
                expires_at
            )
            """
        )

        cursor.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS
            idx_ride_offers_pending_driver
            ON ride_offers (
                driver_id
            )
            WHERE status = 'PENDING'
            """
        )

        cursor.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS
            idx_ride_offers_pending_passenger
            ON ride_offers (
                passenger_id
            )
            WHERE status = 'PENDING'
            """
        )

        cursor.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS
            idx_ride_financial_allocations_ride
            ON ride_financial_allocations (
                ride_id
            )
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_payment_obligations_source
            ON payment_obligations (
                source_type,
                source_reference
            )
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_payment_requests_obligation
            ON payment_requests (
                obligation_reference
            )
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_payment_requests_payer
            ON payment_requests (
                payer_id,
                status
            )
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_payment_intents_request
            ON payment_intents (
                request_reference
            )
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_payment_intents_status
            ON payment_intents (
                status,
                expires_at
            )
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_payment_transactions_intent
            ON payment_transactions (
                intent_reference
            )
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_payment_transactions_obligation
            ON payment_transactions (
                obligation_reference
            )
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_payment_transactions_status
            ON payment_transactions (
                status,
                created_at
            )
            """
        )

        cursor.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS
            idx_payment_provider_reference
            ON payment_transactions (
                provider,
                provider_reference
            )
            WHERE provider_reference IS NOT NULL
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_payment_verifications_status
            ON payment_verifications (
                status,
                verified_at
            )
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_payment_verifications_provider
            ON payment_verifications (
                provider,
                provider_reference
            )
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_payment_reconciliations_status
            ON payment_reconciliations (
                status,
                reconciled_at
            )
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_payment_reconciliations_provider
            ON payment_reconciliations (
                provider,
                provider_reference
            )
            """
        )

        connection.commit()

    except sqlite3.Error:
        connection.rollback()
        raise

    finally:
        connection.close()
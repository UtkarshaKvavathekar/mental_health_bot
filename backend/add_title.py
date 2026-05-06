from database import engine

with engine.connect() as conn:
    conn.exec_driver_sql(
        "ALTER TABLE chat_history ADD COLUMN title TEXT"
    )
    conn.commit()

print("title column added successfully")
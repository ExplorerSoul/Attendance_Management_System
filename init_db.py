from db_config import get_connection

def init_database():
    conn = get_connection()
    cursor = conn.cursor()

    # Create students table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        roll_no VARCHAR(20) PRIMARY KEY,
        name VARCHAR(100)
    )
    """)

    # Create classes table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS classes (
        class_id INT AUTO_INCREMENT PRIMARY KEY,
        class_name VARCHAR(50) UNIQUE
    )
    """)

    # Create attendance table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        roll_no VARCHAR(20),
        name VARCHAR(100),
        class_id INT,
        time TIME,
        date DATE,
        PRIMARY KEY (roll_no, date, class_id),
        FOREIGN KEY (roll_no) REFERENCES students(roll_no),
        FOREIGN KEY (class_id) REFERENCES classes(class_id)
    )
    """)

    # Insert default classes if not already there
    cursor.execute("""
    INSERT INTO classes (class_name)
    VALUES ('CS'), ('MATHS'), ('ML')
    ON DUPLICATE KEY UPDATE class_name=class_name
    """)

    conn.commit()
    conn.close()
    print("✅ Tables created and classes inserted successfully.")

if __name__ == "__main__":
    init_database()

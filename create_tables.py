import psycopg2

conn = psycopg2.connect(
    host="your_host",
    database="your_db",
    user="your_user",
    password="your_password"
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS Customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    city VARCHAR(100),
    notes TEXT
);

CREATE TABLE IF NOT EXISTS Orders (
    id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES Customers(id),
    order_date DATE,
    payment_status VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS OrderItems (
    id SERIAL PRIMARY KEY,
    order_id INT REFERENCES Orders(id),
    item_name VARCHAR(255),
    quantity INT,
    price NUMERIC(10,2)
);
""")

conn.commit()
cursor.close()
conn.close()
print("Tables created successfully!")

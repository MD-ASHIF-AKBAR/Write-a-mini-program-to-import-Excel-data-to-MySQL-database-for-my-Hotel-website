from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import pandas as pd
import psycopg2
import os

load_dotenv()  # load from .env file

DB_HOST = os.getenv("host")
DB_USER = os.getenv("user")
DB_PASSWORD = os.getenv("password")
DB_NAME = os.getenv("database")
DB_PORT = os.getenv("port")

app = Flask(__name__)
CORS(app)

def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT
    )
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'excel_file' not in request.files:
        return jsonify({"message": "No file received"}), 400

    file = request.files['excel_file']
    if file:
        df = pd.read_excel(file)
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            for _, row in df.iterrows():
                cursor.execute("""
                    INSERT INTO Customers (name, email, phone, city, notes)
                    VALUES (%s, %s, %s, %s, %s) RETURNING id
                """, (row['CustomerName'], row['Email'], row['Phone'], row['City'], row['Notes']))
                customer_id = cursor.fetchone()[0]

                cursor.execute("""
                    INSERT INTO Orders (customer_id, order_date, payment_status)
                    VALUES (%s, %s, %s) RETURNING id
                """, (customer_id, row['OrderDate'], row['PaymentStatus']))
                order_id = cursor.fetchone()[0]

                cursor.execute("""
                    INSERT INTO OrderItems (order_id, item_name, quantity, price)
                    VALUES (%s, %s, %s, %s)
                """, (order_id, row['ItemName'], row['Quantity'], row['Price']))

            conn.commit()
        except Exception as e:
            conn.rollback()
            return jsonify({"message": f"Error inserting data: {e}"}), 500
        finally:
            cursor.close()
            conn.close()

        return jsonify({"message": "File uploaded and data inserted successfully!"})
    
    return jsonify({"message": "No file received"}), 400

@app.route('/doubt/<table_name>')
def view_table(table_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    cursor.close()
    conn.close()
    return render_template('view_table.html', columns=columns, rows=rows, table_name=table_name)

@app.route('/test-db')
def test_db():
    try:
        conn = get_db_connection()
        conn.close()
        return "Database connection successful!"
    except Exception as e:
        return f"DB connection failed: {e}"

@app.route('/create_tables')
def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Customers (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255),
        email VARCHAR(255),
        phone VARCHAR(50),
        city VARCHAR(100),
        notes TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Orders (
        id SERIAL PRIMARY KEY,
        customer_id INT REFERENCES Customers(id),
        order_date DATE,
        payment_status VARCHAR(50)
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS OrderItems (
        id SERIAL PRIMARY KEY,
        order_id INT REFERENCES Orders(id),
        item_name VARCHAR(255),
        quantity INT,
        price NUMERIC(10,2)
    )
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
    return "Tables created successfully!"

@app.route('/clear_data')
def clear_data():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("TRUNCATE TABLE OrderItems, Orders, Customers RESTART IDENTITY CASCADE;")
        conn.commit()
        cursor.close()
        conn.close()
        return "All data cleared successfully!"
    except Exception as e:
        return f"Error clearing data: {e}"

if __name__ == "__main__":
    app.run(debug=True)





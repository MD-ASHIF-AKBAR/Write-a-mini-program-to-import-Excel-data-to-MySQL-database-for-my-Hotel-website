from flask import Flask, request, render_template, jsonify
from flask_cors import CORS

import pandas as pd
import psycopg2

app = Flask(__name__)
CORS(app)

# -----------------------
# MySQL Connection
# -----------------------
def get_db_connection():
    conn = psycopg2.connector.connect(
        host="dpg-d3jbk7i4d50c73f31jq0-a",       # change if using remote DB
        user="storage_u6e8_user",            # your DB username
        password="6i0Us6xp0G5hPgoNfiUewnWbSma4L86C",    # your DB password
        database="storage_u6e8"     # database name
        port=5432 
    )
    return conn

# -----------------------
# Homepage
# -----------------------
@app.route('/')
def index():
    return render_template('index.html')

# -----------------------
# Upload Excel File
# -----------------------
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'excel_file' not in request.files:
        return jsonify({"message": "No file received"}), 400

    file = request.files['excel_file']
    if file:
        df = pd.read_excel(file)

        conn = get_db_connection()
        cursor = conn.cursor()

        for index, row in df.iterrows():
            # Insert customer
            cursor.execute("""
                INSERT INTO Customers (name, email, phone, city, notes)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (row['CustomerName'], row['Email'], row['Phone'], row['City'], row['Notes']))
            customer_id = cursor.fetchone()[0]
            
            # Insert order
            cursor.execute("""
                INSERT INTO Orders (customer_id, order_date, payment_status)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (customer_id, row['OrderDate'], row['PaymentStatus']))
            order_id = cursor.fetchone()[0]

            # Insert order item
            cursor.execute("""
                INSERT INTO OrderItems (order_id, item_name, quantity, price)
                VALUES (%s,%s,%s,%s)
            """, (order_id, row['ItemName'], row['Quantity'], row['Price']))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "File uploaded and data inserted successfully!"})
    
    return jsonify({"message": "No file received"}), 400

# -----------------------
# View Table Data
# -----------------------
@app.route('/view/<table_name>')
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


# -----------------------
# Run App
# -----------------------
if __name__ == "__main__":
    app.run(debug=True)






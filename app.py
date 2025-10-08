from flask import Flask, request, render_template
import pandas as pd
import mysql.connector

app = Flask(__name__)

# -----------------------
# MySQL Connection
# -----------------------
def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",       # change if remote DB
        user="root",            # your DB username
        password="password",    # your DB password
        database="hotel_db"     # database name
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
    file = request.files['excel_file']
    if file:
        # Read Excel into pandas
        df = pd.read_excel(file)

        conn = get_db_connection()
        cursor = conn.cursor()

        for index, row in df.iterrows():
            # Insert customer
            cursor.execute("""
                INSERT INTO Customers (name, email, phone, city, notes)
                VALUES (%s,%s,%s,%s,%s)
            """, (row['CustomerName'], row['Email'], row['Phone'], row['City'], row['Notes']))
            customer_id = cursor.lastrowid

            # Insert order
            cursor.execute("""
                INSERT INTO Orders (customer_id, order_date, payment_status)
                VALUES (%s,%s,%s)
            """, (customer_id, row['OrderDate'], row['PaymentStatus']))
            order_id = cursor.lastrowid

            # Insert order item
            cursor.execute("""
                INSERT INTO OrderItems (order_id, item_name, quantity, price)
                VALUES (%s,%s,%s,%s)
            """, (order_id, row['ItemName'], row['Quantity'], row['Price']))

        conn.commit()
        cursor.close()
        conn.close()

        return "File uploaded and data inserted successfully!"
    return "No file received"

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

# -----------------------
# Run App
# -----------------------
if __name__ == "__main__":
    app.run(debug=True)

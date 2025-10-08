from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sqlite3

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize SQLite database
DB_FILE = "files.db"
conn = sqlite3.connect(DB_FILE)
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS uploaded_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL
)
""")
conn.commit()
conn.close()

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"message": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    # Save filename to database
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO uploaded_files (filename) VALUES (?)", (file.filename,))
    conn.commit()
    conn.close()

    return jsonify({"message": f"File uploaded successfully: '{file.filename}'"}), 200

@app.route('/files', methods=['GET'])
def list_files():
    # Return list of uploaded files from database
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT filename FROM uploaded_files")
    files = [row[0] for row in c.fetchall()]
    conn.close()
    return jsonify({"files": files})

if __name__ == "__main__":
    app.run()

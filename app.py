from flask import Flask, request, render_template, jsonify
import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Database configuration
db_config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

# Test connection
def test_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        print("✅ Database connection successful")
        conn.close()
    except mysql.connector.Error as err:
        print("❌ Database connection failed:", err)

# Function to create database connection
def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None

# Create the contacts table if it doesn't exist
def setup_database():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL,
                phone VARCHAR(20),
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Database setup completed")
    else:
        print("❌ Failed to set up database")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone', '')
    message = request.form.get('message', '')

    if not name or not email:
        return jsonify({'success': False, 'message': 'Name and email are required'}), 400

    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
                INSERT INTO contacts (name, email, phone, message)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (name, email, phone, message))
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'success': True, 'message': 'Contact information saved successfully'})
        except mysql.connector.Error as err:
            return jsonify({'success': False, 'message': f'Database error: {err}'}), 500
    else:
        return jsonify({'success': False, 'message': 'Could not connect to database'}), 500

@app.route('/view_contacts')
def view_contacts():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM contacts")
            contacts = cursor.fetchall()
            cursor.close()
            conn.close()
            return jsonify({'contacts': contacts})
        except mysql.connector.Error as err:
            return jsonify({'error': str(err)}), 500
    else:
        return jsonify({'error': 'Database connection failed'}), 500

if __name__ == '__main__':
    test_connection()
    setup_database()
    app.run(debug=True)

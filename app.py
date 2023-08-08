from flask import Flask, render_template, request, jsonify, g
import mysql.connector
from functools import wraps


app = Flask(__name__, static_folder='static', template_folder='templates')


VALID_API_KEYS = ['calculate1234']




def api_key_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('API-Key')

        if api_key not in VALID_API_KEYS:
            return jsonify({'error': 'Invalid API key'}), 401  # Unauthorized

        return func(*args, **kwargs)

    return decorated_function


# Connect to the MariaDB database
db_config = {
    'host': 'localhost',
    'port': 3308,
    'user': 'root',
    'password': 'nishika1234',
    'database': 'calculator'
}

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = mysql.connector.connect(**db_config)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    return render_template('calculator.html')

@app.route('/view_calculations', methods=['GET'])
def view_calculations():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM calculations')
    rows = cursor.fetchall()
    cursor.close()

    calculations = [{'expression': row[1], 'result': row[2]} for row in rows]
    return jsonify({'calculations': calculations})

@app.route('/calculate', methods=['POST'])
def calculate():
    expression = request.form['expression']
    
    try:
        result = eval(expression)
    except Exception as e:
        return jsonify({'error': str(e)})

    db = get_db()
    cursor = db.cursor()
    cursor.execute('INSERT INTO calculations (expression, result) VALUES (%s, %s)', (expression, result))
    db.commit()
    cursor.close()

    return jsonify({'result': result})

if __name__ == '__main__':
    app.run(debug=True,port=8080)

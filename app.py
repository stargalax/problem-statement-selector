from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Initialize SQLite Database
def init_db():
    with sqlite3.connect('project.db') as conn:
        cursor = conn.cursor()
        cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS teams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lead_name TEXT NOT NULL,
                team_name TEXT NOT NULL
            )
        ''')
        cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS problem_statements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                problem_statement TEXT NOT NULL,
                is_selected BOOLEAN DEFAULT 0
            )
        ''')
        cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS selections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_name TEXT NOT NULL,
                lead_name TEXT NOT NULL,
                problem_statement_id INTEGER,
                FOREIGN KEY (problem_statement_id) REFERENCES problem_statements (id)
            )
        ''')
        conn.commit()
        print("Database initialized!")


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_type = request.form['user_type']
        if user_type == 'professor':
            return redirect(url_for('add_problem'))
        else:
            return redirect(url_for('student_selection'))
    return render_template('login.html')

@app.route('/student_selection', methods=['GET', 'POST'])
def student_selection():
    if request.method == 'POST':
        lead_name = request.form['lead_name']
        team_name = request.form['team_name']
        problem_id = request.form['problem_statement']
        
        with sqlite3.connect('project.db') as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO selections (team_name, lead_name, problem_statement_id) VALUES (?, ?, ?)', 
                           (team_name, lead_name, problem_id))
            cursor.execute('UPDATE problem_statements SET is_selected = 1 WHERE id = ?', (problem_id,))
            conn.commit()
        return redirect(url_for('student_selection'))
    
    with sqlite3.connect('project.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM problem_statements WHERE is_selected = 0')
        problems = cursor.fetchall()
    return render_template('index.html', problems=problems)


@app.route('/add_problem', methods=['GET', 'POST'])
def add_problem():
    if request.method == 'POST':
        problem_statement = request.form['problem_statement']
        with sqlite3.connect('project.db') as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO problem_statements (problem_statement) VALUES (?)', 
                           (problem_statement,))
            conn.commit()
        return redirect(url_for('add_problem'))
    
    return render_template('add_problem.html')


@app.route('/view_selections')
def view_selections():
    with sqlite3.connect('project.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT team_name, lead_name, problem_statements.problem_statement 
            FROM selections 
            JOIN problem_statements ON selections.problem_statement_id = problem_statements.id
        ''')
        selections = cursor.fetchall()
    return render_template('view_selection.html', selections=selections)

if __name__ == '__main__':
    init_db()  # Initialize the database
    app.run(debug=True)

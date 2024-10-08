from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
import sqlite3
import os
import io

app = Flask(__name__)
app.secret_key = 'ny-key-pair'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, 'mydatabase.db')

conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS file_users 
             (username TEXT, password TEXT, firstname TEXT, lastname TEXT, email TEXT, word_count INTEGER, file_content BLOB)''')
conn.commit()
conn.close()

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
      username = request.form['username']
      password = request.form['password']
      firstname = request.form['firstname']
      lastname = request.form['lastname']
      email = request.form['email']

      file = request.files['limerick_file']
      file_content = None
      word_count = 0

      if file:
        file_content = file.read()  # Read the file content as binary
        word_count = len(file_content.decode('utf-8').split())

      conn = sqlite3.connect(db_path)
      c = conn.cursor()
      c.execute("INSERT INTO file_users (username, password, firstname, lastname, email, word_count, file_content) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (username, password, firstname, lastname, email, word_count, file_content))
      conn.commit()
      conn.close()
    
      session['username'] = username
      return redirect(url_for('profile', username=username))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM file_users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            session['username'] = username  # Store username in session
            return redirect(url_for('profile', username=username))
        else:

            return "Invalid username or password. Please try again."
    return render_template('login.html')



@app.route('/profile/<username>')
def profile(username):
    if 'username' not in session or session['username'] != username:
        return redirect(url_for('login'))
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT * FROM file_users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()

    return render_template('profile.html', user=user)

@app.route('/download/<username>')
def download(username):
    if 'username' not in session or session['username'] != username:
        return redirect(url_for('login'))  # Redirect to login if not logged in

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT file_content FROM file_users WHERE username=?", (username,))
    file_content = c.fetchone()
    conn.close()

    if file_content and file_content[0]:
        # Create a BytesIO object to serve the file
        return send_file(io.BytesIO(file_content[0]), 
                         download_name='Limerick-1.txt', 
                         as_attachment=True)
    else:
        return "No file available for download."

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)

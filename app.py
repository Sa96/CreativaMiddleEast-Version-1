import random
import string
from flask import Flask, render_template
import pyodbc
import logging
import requests
from powerbiclient import Report, models

from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mail import Mail, Message
from flask_session import Session
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import bcrypt

log = logging.getLogger()

app = Flask(__name__, static_url_path='/static')

wsgi_app = app.wsgi_app

app.config['SESSION_TYPE'] = 'filesystem'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////site.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'
app.config['SECURITY_PASSWORD_HASH'] = 'bcrypt'
app.config['SECURITY_PASSWORD_SALT'] = b'$2b$12$wqKlYjmOfXPghx3FuC3Pu.'

Session(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    
    def __init_(self, username, email, password):
        self.username = username
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
    def check_password(self, password):
        pwhash = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
        self.password_hash = pwhash.decode('utf8')
    
with app.app_context():
    db.create_all()
    
admin = Admin(app, name='Admin Panel', template_mode='bootstrap5')
admin.add_view(ModelView(User, db.session))

users = {'your_username': 'your_password', 'user@example.com': 'user_password'}
mail = Mail(app)

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    # Handle login form submission
    username = request.form.get('username')
    password = request.form.get('password')

    # Initialize connection and cursor
    connection = pyodbc.connect("DRIVER={ODBC Driver 17 for SQL SERVER};SERVER=68.178.163.254\\SQLEXPRESS;DATABASE=PBI_Dashboard_DB;UID=sa;PWD=Ngtech@2021")
    cursor = connection.cursor()
    print("Database is connected. here is the connection : ", cursor, sep='\n')

    query = "SELECT * FROM dbo.Users WHERE username = ? AND password = ?"
    result = cursor.execute(query, (username, password)).fetchone()

    if result:
        session['username'] = username
        cursor.close()
        connection.close()
        return redirect(url_for('dashboard'))
    else:
        cursor.close()
        connection.close()
        return render_template('login.html', error="Invalid Details")


@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        username = session['username']
        access_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6IjVCM25SeHRRN2ppOGVORGMzRnkwNUtmOTdaRSIsImtpZCI6IjVCM25SeHRRN2ppOGVORGMzRnkwNUtmOTdaRSJ9.eyJhdWQiOiJodHRwczovL21hbmFnZW1lbnQuY29yZS53aW5kb3dzLm5ldC8iLCJpc3MiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC9jODg5N2Q1ZC0zYjhmLTQxY2ItOGY0Yy1hYTNhZGYwNTliZmQvIiwiaWF0IjoxNzA0NjExMjE5LCJuYmYiOjE3MDQ2MTEyMTksImV4cCI6MTcwNDYxNTM0MCwiYWNyIjoiMSIsImFpbyI6IkFUUUF5LzhWQUFBQVQzVmVahNkdna2lhNXBXSW8xdWVMZUZNcEFRVUdFRENJODUybTRiQ0VOSGo2QjJ1YmgyQWxua05yaGZ0ZDZPYkwiLCJhbXIiOlsicHdkIl0sImFwcGlkIjoiMDRiMDc3OTUtOGRkYi00NjFhLWJiZWUtMDJmOWUxYmY3YjQ2IiwiYXBwaWRhY3IiOiIwIiwiZmFtaWx5X25hbWUiOiJuZ3RlY2giLCJnaXZlbl9uYW1lIjoiTmd0ZWNoIENvbXB1dGVyIFNvZnR3YXJlIEhvdXNlIiwiZ3JvdXBzIjpbIjI5NmY4YTYyLWFlZmUtNDViNy04MGI3LWYzMTE5YzRmZjFiNiJdLCJpZHR5cCI6InVzZXIiLCJpcGFkZHIiOiIyMDAxOjhmODoxNDYxOjIzOWE6NmM1MDphNTc3OmZjZDM6YTBjMiIsIm5hbWUiOiJOZ3RlY2ggQ29tcHV0ZXIgU29mdHdhcmUgSG91c2Ugbmd0ZWNoIiwib2lkIjoiY2JiNjIwYzgtNjk5Yi00MzgyLWFiMjktODNhZDY2YTllNmJlIiwicHVpZCI6IjEwMDMyMDAxQzJCMTMwOTYiLCJwd2RfZXhwIjoiMzE1MzI0NjgwIiwicHdkX3VybCI6Imh0dHBzOi8vcHJvZHVjdGl2aXR5LnNlY3VyZXNlcnZlci5uZXQvbWljcm9zb2Z0P21hcmtldGlkPWVuLVVTXHUwMDI2ZW1haWw9aW5mbyU0MG5ndGVjaHVhZS5jb21cdTAwMjZzb3VyY2U9Vmlld1VzZXJzXHUwMDI2YWN0aW9uPVJlc2V0UGFzc3dvcmQiLCJyaCI6IjAuQVU4QVhYMkp5STg3eTBHUFRLbzYzd1diX1VaSWYza0F1dGRQdWtQYXdmajJNQk5QQURJLiIsInNjcCI6InVzZXJfaW1wZXJzb25hdGlvbiIsInN1YiI6IktxaTktNFlsbk9RNXl2ZkVrQXF1V1NUcUVRby1ORmJLTXEtXzZ1SDQtR0kiLCJ0aWQiOiJjODg5N2Q1ZC0zYjhmLTQxY2ItOGY0Yy1hYTNhZGYwNTliZmQiLCJ1bmlxdWVfbmFtZSI6ImluZm9Abmd0ZWNodWFlLmNvbSIsInVwbiI6ImluZm9Abmd0ZWNodWFlLmNvbSIsInV0aSI6Ik9ndGptZEp0ajBHU2hqenp3ekhUQkEiLCJ2ZXIiOiIxLjAiLCJ3aWRzIjpbIjYyZTkwMzk0LTY5ZjUtNDIzNy05MTkwLTAxMjE3NzE0NWUxMCIsImI3OWZiZjRkLTNlZjktNDY4OS08MTQzLTc2YjE5NGU4NTUwOSJdLCJ4bXNfY2FlIjoiMSIsInhtc19jYyI6WyJDUDEiXSwieG1zX2ZpbHRlcl9pbmRleCI6WyI3OSJdLCJ4bXNfcmQiOiIwLjQyTGxZQlJpOUFjQSIsInhtc19zc20iOiIxIiwieG1zX3RjZHQiOjE2Mzk4OTgwNTR9.TVv3fWNInAgRJxvtP8Y-oO2VokJ4Jz17ncQn2Uqg3BJoUTX8AmSxHAo8f9MwTAybrEXQ9zjhGZWJiZmtYElVCaHZZjDFOmI5Jbqop2lTQdnKuy2LoXclPARcDj2RxdpTuMwk9Uk_SFD6BO4iL8bPfxQnFyS5gbQioxxM3tdeG8r6Xr6D_C2Pgf7JNbAGwrcZDAPHAoSpXHA9QkLoqkdNBjlq_USItKHl61s3KripE-WAW7JwTfkPG71ETDqHEghHp8g0Gc8vBiA9EVEJJfIVTlbQjFwVVKVA3xWbTSRBGOKFBWv0nO4oMIdyrY6cJdLVdKA7ni4GH8V0Q9k1eVjYrA"
        
        report = Report(report_id='dda3cb1c-7400-4408-b480-aeaecda0bc7a', workspace_id='936fa150-dea4-4e49-abc4-734623c59e23', access_token=access_token)
        embed_url = "https://app.powerbi.com/reportEmbed?reportId=dda3cb1c-7400-4408-b480-aeaecda0bc7a&autoAuth=true&ctid=c8897d5d-3b8f-41cb-8f4c-aa3adf059bfd"

        print(username, access_token, embed_url, sep="\n")

        return render_template('Dashboard.html', username=username, access_token=access_token)
    else:
        return redirect(url_for('index'))

@app.route('/forget_password')
def forget_password():
    if request.method == 'POST':
        email = request.form['Email']
        if email in users[1]:
            temporary_password = ''.join(random.choices(string.ascii_letters+string.digits, k=8))
            users[email] = temporary_password
            send_reset_email(email, temporary_password)
            flash('Password reset link sent to your email.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Email not found. Please check your email address.', 'error')
    return render_template('forget_password.html')

def send_reset_email(email, temp_password):
    message = Message('Password Reset', sender='your-email@example.com', recipients=[email])
    message.body = f'Your temporary password is: {temp_password}. Please login and change your password.'
    mail.send(message)

@app.route('/create_account', methods=['POST'])
def create_account():
    if request.method == 'POST':
        # Process the form data to create a new user account
        username = request.form['Username']
        email = request.form['Email']
        password = request.form['Password']

        # Add your logic to store the new user in the database or any other storage mechanism
        user = User(username=username,email=email, password=password)

        # After creating the account, you might want to redirect to the login page
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Logout successful.', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
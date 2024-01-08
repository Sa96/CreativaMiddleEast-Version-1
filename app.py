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
        access_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6IjVCM25SeHRRN2ppOGVORGMzRnkwNUtmOTdaRSIsImtpZCI6IjVCM25SeHRRN2ppOGVORGMzRnkwNUtmOTdaRSJ9.eyJhdWQiOiJodHRwczovL21hbmFnZW1lbnQuY29yZS53aW5kb3dzLm5ldC8iLCJpc3MiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC9jODg5N2Q1ZC0zYjhmLTQxY2ItOGY0Yy1hYTNhZGYwNTliZmQvIiwiaWF0IjoxNzA0NzA0NDQ3LCJuYmYiOjE3MDQ3MDQ0NDcsImV4cCI6MTcwNDcxMDA2OCwiYWNyIjoiMSIsImFpbyI6IkFUUUF5LzhWQUFBQWVZTHhqNGVJaVNIM0lOeUMyT1lHQXNadTBvWEEyV0NhUEwybkdkMTJNQk45T1BiOGd0K2x5VnlTQzlHSVZHekMiLCJhbXIiOlsicHdkIiwicnNhIl0sImFwcGlkIjoiMDRiMDc3OTUtOGRkYi00NjFhLWJiZWUtMDJmOWUxYmY3YjQ2IiwiYXBwaWRhY3IiOiIwIiwiZGV2aWNlaWQiOiI1MzgzNDE2NS03ZmIxLTRmYTYtYjZlZS0wZGExYmI0MjdjMDgiLCJmYW1pbHlfbmFtZSI6Im5ndGVjaCIsImdpdmVuX25hbWUiOiJOZ3RlY2ggQ29tcHV0ZXIgU29mdHdhcmUgSG91c2UiLCJncm91cHMiOlsiMjk2ZjhhNjItYWVmZS00NWI3LTgwYjctZjMxMTljNGZmMWI2Il0sImlkdHlwIjoidXNlciIsImlwYWRkciI6IjIwMDE6OGY4OjE0NjE6MjM5YTo2YzUwOmE1Nzc6ZmNkMzphMGMyIiwibmFtZSI6Ik5ndGVjaCBDb21wdXRlciBTb2Z0d2FyZSBIb3VzZSBuZ3RlY2giLCJvaWQiOiJjYmI2MjBjOC02OTliLTQzODItYWIyOS04M2FkNjZhOWU2YmUiLCJwdWlkIjoiMTAwMzIwMDFDMkIxMzA5NiIsInB3ZF9leHAiOiIzMTUzMzQ3NzQiLCJwd2RfdXJsIjoiaHR0cHM6Ly9wcm9kdWN0aXZpdHkuc2VjdXJlc2VydmVyLm5ldC9taWNyb3NvZnQ_bWFya2V0aWQ9ZW4tVVNcdTAwMjZlbWFpbD1pbmZvJTQwbmd0ZWNodWFlLmNvbVx1MDAyNnNvdXJjZT1WaWV3VXNlcnNcdTAwMjZhY3Rpb249UmVzZXRQYXNzd29yZCIsInJoIjoiMC5BVThBWFgySnlJODd5MEdQVEtvNjN3V2JfVVpJZjNrQXV0ZFB1a1Bhd2ZqMk1CTlBBREkuIiwic2NwIjoidXNlcl9pbXBlcnNvbmF0aW9uIiwic3ViIjoiS3FpOS00WWxuT1E1eXZmRWtBcXVXU1RxRVFvLU5GYktNcS1fNnVINC1HSSIsInRpZCI6ImM4ODk3ZDVkLTNiOGYtNDFjYi04ZjRjLWFhM2FkZjA1OWJmZCIsInVuaXF1ZV9uYW1lIjoiaW5mb0BuZ3RlY2h1YWUuY29tIiwidXBuIjoiaW5mb0BuZ3RlY2h1YWUuY29tIiwidXRpIjoic25JYlNXR0s2VUc5RGkya0Z2Y1JBQSIsInZlciI6IjEuMCIsIndpZHMiOlsiNjJlOTAzOTQtNjlmNS00MjM3LTkxOTAtMDEyMTc3MTQ1ZTEwIiwiYjc5ZmJmNGQtM2VmOS00Njg5LTgxNDMtNzZiMTk0ZTg1NTA5Il0sInhtc19jYWUiOiIxIiwieG1zX2NjIjpbIkNQMSJdLCJ4bXNfZmlsdGVyX2luZGV4IjpbIjc5Il0sInhtc19yZCI6IjAuNDJMbFlCUmk5QWNBIiwieG1zX3NzbSI6IjEiLCJ4bXNfdGNkdCI6MTYzOTg5ODA1NH0.b7MomYhATV2riuxkN_GRYl5As09SzktxeXONiifXrpA8w0wzn4dWCeQJvY9OBbEY6myQh30NF65ggTmfeHmonaL5oB0Ak5I753rdeEwZVPKxHWhVZpJKCc6BDjpRB79P6QhjCfH9uFYvLzQrh443VTJ3Fktn9qYQsWUZTlY8zXbXRlO3pVCp0t18wX8pft5Xvssj_v8RNz8iM_eByTxPNEqI9A5WmZ2ahLE-tjhjUP74kg7OP8zVsrG1HyrCjvKfLKXASx4qrgo-yhTzXamydRr_5r6mycwvpBfswU5eh9XWR8bnXRP56X-mZes-8ZVvjwn6SVjidAGp2FT_W1w38Q"        
        report = Report(report_id='dda3cb1c-7400-4408-b480-aeaecda0bc7a', workspace_id='936fa150-dea4-4e49-abc4-734623c59e23', access_token=access_token)
        embed_url = "https://app.powerbi.com/reportEmbed?reportId=dda3cb1c-7400-4408-b480-aeaecda0bc7a&autoAuth=true&ctid=c8897d5d-3b8f-41cb-8f4c-aa3adf059bfd"
        return render_template('Dashboard.html', username=username, access_token=access_token, report=report, embed_url=embed_url
                                )
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
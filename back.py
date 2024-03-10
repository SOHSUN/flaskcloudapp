import os
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder='C:/SJK/fe/fe/static', static_url_path='/static')

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'C:/SJK/fe/fe/uploads'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB size limit for file uploads
app.config['TEMPLATES_AUTO_RELOAD'] = True

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    files = db.relationship('File', backref='owner', lazy=True)

# File model
class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    file_type = db.Column(db.String(20), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)  # New column for file size in bytes
    created_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    modified_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    app.logger.info(f"Login request method: {request.method}")
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        app.logger.info(f"Attempting login for {username}")
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return jsonify({"success": True, "message": "Login successful"})
        else:
            return jsonify({"success": False, "message": "Invalid username or password"}), 401
    else:
        # This block should not be reached since the route allows GET requests
        return jsonify({"success": False, "message": "Method not allowed"}), 405

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    app.logger.info(f"Signup request method: {request.method}")
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        app.logger.info(f"Received signup for {username}")
        
        user_exists = User.query.filter_by(username=username).first()
        if user_exists:
            app.logger.error(f"Username {username} already exists")  # More detailed logging
            return jsonify({"success": False, "message": "Username already exists"}), 400

        if not username or not password:  # Example check for empty fields
            app.logger.error(f"Missing username or password")
            return jsonify({"success": False, "message": "Missing username or password"}), 400
        
        # Additional validation checks can be added here

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"success": True, "message": "Signup successful"})
    else:
        return jsonify({"success": False, "message": "Method not allowed"}), 405


@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    app.logger.info("Upload file request")
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "message": "No selected file"}), 400

    # Save the file temporarily
    temp_file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
    file.save(temp_file_path)

    # Get the size of the temporary file
    file_size = os.path.getsize(temp_file_path)

    # Calculate user's total storage usage
    user_files = File.query.filter_by(user_id=current_user.id).all()
    total_usage = sum(f.file_size for f in user_files)

    # Check if adding the new file exceeds the storage limit (10 MB)
    if total_usage + file_size > 10 * 1024 * 1024:
        os.remove(temp_file_path)  # Remove the temporary file
        return jsonify({"success": False, "message": "Storage full. You have reached the maximum storage limit."}), 400

    # Move the temporary file to the final destination
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    os.rename(temp_file_path, filepath)

    new_file = File(filename=filename, file_type=file.content_type, file_size=file_size, user_id=current_user.id)
    db.session.add(new_file)
    db.session.commit()

    return jsonify({"success": True, "message": "File uploaded successfully", "filename": filename, "fileId": new_file.id})


@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"success": True, "message": "Logged out successfully"})

@app.route('/dashboard')
@login_required
def dashboard():
    user_files = File.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', files=user_files)

@app.route('/update_file/<filename>', methods=['PUT'])
@login_required
def update_file(filename):
    app.logger.info(f"Update file request for {filename}")
    new_filename = request.json.get('newFilename')
    if not new_filename:
        return jsonify({"success": False, "message": "New filename not provided"}), 400

    file = File.query.filter_by(filename=filename).first()
    if not file:
        return jsonify({"success": False, "message": "File not found"}), 404

    file.filename = new_filename
    file.modified_time = datetime.utcnow()
    db.session.commit()

    return jsonify({"success": True, "message": "File renamed successfully", "newFilename": new_filename})


if __name__ == '__main__':
    app.run(debug=True)

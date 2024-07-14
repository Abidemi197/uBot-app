#.\.venv\Scripts\Activate.ps1
from flask import Flask, jsonify, request, session, current_app, g
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from dotenv import load_dotenv
from models import db, User, ChatHistory
import os
from summarizer import summarize_transcript
from utils import get_video_id, load_transcript_from_youtube, initialize_pinecone, query_pinecone, summarize_with_gpt, get_pinecone_store, is_valid_youtube_url, clear_pinecone_namespace
import uuid
from datetime import timedelta

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///youtuberag.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ['FLASK_SECRET_KEY']
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key')

# Initialize extensions
db.init_app(app)
jwt = JWTManager(app)

# Create database tables
with app.app_context():
    db.create_all()

# Home route
@app.route('/')
def home():
    return jsonify({"message": "Welcome to YouTube RAG App Backend!"})

# User Registration
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
        return jsonify({"message": "Username or email already exists"}), 400

    new_user = User(username=username, email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

# User Login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username')).first()

    if user and user.check_password(data.get('password')):
        access_token = create_access_token(identity=user.username)
        session['video_uploaded'] = False  # Reset the session variable on login
        session.modified = True  # Mark session as modified
        return jsonify({"access_token": access_token}), 200
    else:
        return jsonify({"message": "Invalid username or password"}), 401

@app.route('/upload-video', methods=['POST'])
@jwt_required()
def upload_video():
    current_user = get_jwt_identity()
    data = request.get_json()
    video_url = data.get('videoUrl')
    print("in upload video")
    
    if not video_url:
        return jsonify({"error": "No YouTube link provided!"}), 400
    
    if not is_valid_youtube_url(video_url):
        return jsonify({"error": "Invalid YouTube link!"}), 400
    
    try:
        # Get video transcript
        transcript = load_transcript_from_youtube(video_url)
        summary = summarize_transcript(video_url, transcript)

        # Generate summary
        summary = summarize_with_gpt(summary)

        user = User.query.filter_by(username=current_user).first()
        user_id = str(user.id)

        # Save summary to chat history
        new_chat = ChatHistory(question="Video Summary", response=summary, user_id=user_id)
        db.session.add(new_chat)
        db.session.commit()

        # Initialize Pinecone with the transcript
        clear_pinecone_namespace(namespace=user_id, index_name="youtube-index", force_clear=False)
        initialize_pinecone(transcript, namespace=user_id)
        #user = User.query.filter_by(username=current_user).first()
        #user.video_uploaded = True
        #db.session.commit()
        #print(user.video_uploaded)
        

        return jsonify({"summary": summary, "message": "Video uploaded and processed successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/ask-question', methods=['POST'])
@jwt_required()
def ask_question():

    current_user = get_jwt_identity()
    data = request.get_json()
    question = data.get('question')

    if len(question) < 1:
        return jsonify({"error": "Question is too short!"}), 400

    try:
        # Retrieve the user's namespace
        user = User.query.filter_by(username=current_user).first()
        user_id = str(user.id)
        namespace = user_id

        # Retrieve chat history from database
        user_chat_history = ChatHistory.query.filter_by(user_id=user_id).all()
        chat_history = [{'question': chat.question, 'response': chat.response} for chat in user_chat_history]

        print("test 1")
        pinecone_store = get_pinecone_store(user.id)
        print("test 2")
        if pinecone_store is None:
            print("error: Pinecone store not initialized. Please upload a video first.")
            return jsonify({"error": "Pinecone store not initialized. Please upload a video first."}), 400
        
        response = query_pinecone(question, pinecone_store, namespace, chat_history)
        
        # Save the new question and response to the database
        new_chat = ChatHistory(user_id=user_id, question=question, response=response)
        db.session.add(new_chat)
        db.session.commit()

        return jsonify({"answer": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/chat-history', methods=['GET'])
@jwt_required()
def get_chat_history():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    user_id = str(user.id)

    chat_history = ChatHistory.query.filter_by(user_id=user_id).order_by(ChatHistory.id).all()
    history = [{'question': chat.question, 'response': chat.response} for chat in chat_history]

    return jsonify({"chat_history": history}), 200

@app.route('/clear-chat-history', methods=['POST'])
@jwt_required()
def clear_chat_history():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    user_id = str(user.id)
    clear_pinecone_namespace(namespace=user_id, index_name="youtube-index", force_clear=True)

    # Clear chat history for the user
    ChatHistory.query.filter_by(user_id=user_id).delete()
    db.session.commit()

    return jsonify({"message": "Chat history cleared"}), 200

@app.route('/verify-token', methods=['POST'])
@jwt_required()
def verify_token():
    try:
        # If this point is reached, it means the token is valid
        current_user = get_jwt_identity()
        print("Token verfied")
        return jsonify({"valid": True, "username": current_user}), 200
    except:
        return jsonify({"valid": False}), 401

if __name__ == '__main__':
    app.run(debug=True)
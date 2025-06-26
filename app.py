import threading
import webbrowser
from flask import Flask, render_template_string
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

document_content = ""
connected_users = 0

@app.route('/')
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Real-Time Collaborative Notes</title>
<style>
  body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    margin: 0; padding: 0; background: #f4f7f9;
    display: flex; flex-direction: column; height: 100vh;
  }
  header {
    background: #007bff; color: white; padding: 15px 20px;
    text-align: center; font-size: 1.5rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  }
  main {
    flex: 1; padding: 20px;
    display: flex; flex-direction: column;
    max-width: 900px; margin: auto; width: 100%;
  }
  #userCount {
    margin-bottom: 10px; font-weight: 600; color: #555;
  }
  textarea {
    flex: 1;
    width: 100%;
    border: 2px solid #ddd;
    border-radius: 8px;
    padding: 15px;
    font-size: 1.1rem;
    line-height: 1.5;
    resize: none;
    box-shadow: inset 0 2px 5px rgba(0,0,0,0.05);
    transition: border-color 0.3s ease;
  }
  textarea:focus {
    border-color: #007bff;
    outline: none;
  }
  footer {
    padding: 10px 20px;
    background: #e9ecef;
    text-align: center;
    font-size: 0.9rem;
    color: #777;
  }
  #status {
    margin-top: 10px;
    font-size: 0.9rem;
    color: #007bff;
    font-style: italic;
  }
</style>
</head>
<body>
  <header>Real-Time Collaborative Note-Taking</header>
  <main>
    <div id="userCount">Connected users: 0</div>
    <textarea id="noteArea" placeholder="Start typing your notes here..."></textarea>
    <div id="status"></div>
  </main>
  <footer>CODTECH Internship Task - Collaborative Tool &copy; 2025</footer>

<script src="https://cdn.socket.io/4.6.1/socket.io.min.js"
        integrity="sha384-o4Ad2DTM5R3jl2+zqUQXHvDhPcCjNQXieKzvn6/nZxXL6f6F1CQzFrlXcf6LM3aE"
        crossorigin="anonymous"></script>
<script>
  const socket = io();

  const textarea = document.getElementById('noteArea');
  const userCount = document.getElementById('userCount');
  const status = document.getElementById('status');

  let timeout = null;

  // Receive updated content from server
  socket.on('update_content', (data) => {
    if (textarea.value !== data) {
      const cursorPos = textarea.selectionStart;
      textarea.value = data;
      textarea.selectionStart = textarea.selectionEnd = cursorPos;
    }
    status.textContent = 'All changes saved';
  });

  // Receive updated user count
  socket.on('user_count', (count) => {
    userCount.textContent = `Connected users: ${count}`;
  });

  // On load, request current content
  socket.on('connect', () => {
    socket.emit('request_content');
  });

  // Notify server when user is typing (with debounce)
  textarea.addEventListener('input', () => {
    status.textContent = 'Saving...';
    if (timeout) clearTimeout(timeout);
    timeout = setTimeout(() => {
      socket.emit('edit_content', textarea.value);
    }, 300);
  });
</script>
</body>
</html>
""")

@socketio.on('connect')
def on_connect():
    global connected_users
    connected_users += 1
    emit('user_count', connected_users, broadcast=True)

@socketio.on('disconnect')
def on_disconnect():
    global connected_users
    connected_users -= 1
    emit('user_count', connected_users, broadcast=True)

@socketio.on('request_content')
def send_content():
    emit('update_content', document_content)

@socketio.on('edit_content')
def handle_edit(new_content):
    global document_content
    document_content = new_content
    emit('update_content', new_content, broadcast=True, include_self=False)

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")

if __name__ == '__main__':
    threading.Timer(1, open_browser).start()
    socketio.run(app, debug=True)

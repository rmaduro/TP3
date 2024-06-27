from flask import Flask, request, jsonify, make_response, abort
from models import Database

app = Flask(__name__)
app.config['STATIC_URL_PATH'] = '/static'
app.config['DEBUG'] = True

db = Database(filename=':memory:', schema='schema.sql')
db.recreate()

def authenticate_user(authentication):
    auth = authentication
    if not auth or not auth.username or not auth.password:
        abort(make_response(jsonify({"error": "Username and password required"}), 401))

    user = db.execute_query('SELECT id FROM user WHERE username=? AND password=?',
                            (auth.username, auth.password)).fetchone()

    if user is not None and user['id'] is not None:
        return user.get('id')

    abort(make_response(jsonify({"error": "Invalid credentials"}), 401))

def get_authenticated_user():
    auth = request.authorization
    if not auth:
        return None

    user_id = authenticate_user(auth)
    if user_id:
        return db.execute_query('SELECT * FROM user WHERE id=?', (user_id,)).fetchone()

    return None

def make_unauthorized_response():
    return make_response(jsonify({'error': 'Unauthorized'}), 403)

def make_not_found_response():
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/user/register/', methods=['POST'])
def user_register():
    data = request.json
    if not data.get('username') or not data.get('password'):
        return make_response(jsonify({'error': 'Missing username or password'}), 400)

    db.execute_update('INSERT INTO user (name, email, username, password) VALUES (?, ?, ?, ?)', (
        data.get('name'), data.get('email'), data['username'], data['password']
    ))
    return make_response(jsonify({'message': 'User registered successfully'}), 201)

@app.route('/api/user/', methods=['GET', 'PUT'])
def user_detail():
    user = get_authenticated_user()
    if not user:
        return make_unauthorized_response()

    if request.method == 'GET':
        return jsonify(user)
    else:
        data = request.json
        if not data.get('name') or not data.get('email'):
            return make_response(jsonify({'error': 'Name and email required'}), 400)

        db.execute_update('UPDATE user SET name=?, email=? WHERE id=?', (
            data['name'], data['email'], user['id']
        ))
        return make_response(jsonify({'message': 'User updated successfully'}), 200)

@app.route('/api/projects/', methods=['GET', 'POST'])
def project_list():
    user = get_authenticated_user()
    if not user:
        return make_unauthorized_response()

    if request.method == 'GET':
        projects = db.execute_query('SELECT * FROM project WHERE user_id=?', (user['id'],)).fetchall()
        return jsonify(projects)
    else:
        data = request.json
        db.execute_update('INSERT INTO project (user_id, title, creation_date, last_updated) VALUES (?, ?, ?, ?)', (
            user['id'], data['title'], data['creation_date'], data['last_updated']
        ))
        return make_response(jsonify({'message': 'Project created successfully'}), 201)

@app.route('/api/projects/<int:id>/', methods=['GET', 'PUT', 'DELETE'])
def project_detail(id):
    user = get_authenticated_user()
    if not user:
        return make_unauthorized_response()

    project = db.execute_query('SELECT * FROM project WHERE id=? AND user_id=?', (id, user['id'])).fetchone()
    if not project:
        return make_not_found_response()

    if request.method == 'GET':
        return jsonify(project)
    elif request.method == 'PUT':
        data = request.json
        db.execute_update('UPDATE project SET title=?, last_updated=? WHERE id=? AND user_id=?', (
            data['title'], data['last_updated'], id, user['id']
        ))
        return make_response(jsonify({'message': 'Project updated successfully'}), 200)
    else:
        db.execute_update('DELETE FROM project WHERE id=? AND user_id=?', (id, user['id']))
        return make_response(jsonify({'message': 'Project deleted successfully'}), 200)

@app.route('/api/projects/<int:id>/tasks/', methods=['GET', 'POST'])
def task_list(id):
    user = get_authenticated_user()
    if not user:
        return make_unauthorized_response()

    project = db.execute_query('SELECT * FROM project WHERE id=? AND user_id=?', (id, user['id'])).fetchone()
    if not project:
        return make_not_found_response()

    if request.method == 'GET':
        tasks = db.execute_query('SELECT * FROM task WHERE project_id=?', (id,)).fetchall()
        return jsonify(tasks)
    else:
        data = request.json
        db.execute_update('INSERT INTO task (project_id, title, creation_date, completed) VALUES (?, ?, ?, ?)', (
            id, data['title'], data['creation_date'], data['completed']
        ))
        return make_response(jsonify({'message': 'Task created successfully'}), 201)

@app.route('/api/projects/<int:id>/tasks/<int:task_id>/', methods=['GET', 'PUT', 'DELETE'])
def task_detail(id, task_id):
    user = get_authenticated_user()
    if not user:
        return make_unauthorized_response()

    task = db.execute_query('SELECT * FROM task WHERE id=? AND project_id=?', (task_id, id)).fetchone()
    if not task:
        return make_not_found_response()

    if request.method == 'GET':
        return jsonify(task)
    elif request.method == 'PUT':
        data = request.json
        db.execute_update('UPDATE task SET title=?, completed=? WHERE id=? AND project_id=?', (
            data['title'], data['completed'], task_id, id
        ))
        return make_response(jsonify({'message': 'Task updated successfully'}), 200)
    else:
        db.execute_update('DELETE FROM task WHERE id=? AND project_id=?', (task_id, id))
        return make_response(jsonify({'message': 'Task deleted successfully'}), 200)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)

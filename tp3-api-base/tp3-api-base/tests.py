import base64
import unittest
from app import app, db

def auth_header(username, password):
    credentials = f'{username}:{password}'
    b64credentials = base64.b64encode(credentials.encode()).decode('utf-8')
    return {'Authorization': f'Basic {b64credentials}'}

class TestBase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        self.db = db
        self.db.recreate()

    def tearDown(self):
        pass

class TestUsers(TestBase):
    def setUp(self):
        super().setUp()

    def test_register_user(self):
        res = self.client.post('/api/user/register/', json={
            'name': 'New User',
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'password'
        })
        self.assertEqual(res.status_code, 201)

    def test_correct_credentials(self):
        credentials = auth_header('homer', '1234')
        res = self.client.get('/api/user/', headers=credentials)
        self.assertEqual(res.status_code, 200)

    def test_wrong_credentials(self):
        credentials = auth_header('no-user', 'no-password')
        res = self.client.get('/api/user/', headers=credentials)
        self.assertEqual(res.status_code, 403)

class TestProjects(TestBase):
    def setUp(self):
        super().setUp()

    def test_create_project(self):
        credentials = auth_header('homer', '1234')
        res = self.client.post('/api/projects/', headers=credentials, json={
            'title': 'New Project',
            'creation_date': '2023-06-01',
            'last_updated': '2023-06-01'
        })
        self.assertEqual(res.status_code, 201)

    def test_get_projects(self):
        credentials = auth_header('homer', '1234')
        res = self.client.get('/api/projects/', headers=credentials)
        self.assertEqual(res.status_code, 200)

    def test_update_project(self):
        credentials = auth_header('homer', '1234')
        res = self.client.put('/api/projects/1/', headers=credentials, json={
            'title': 'Updated Project',
            'last_updated': '2023-06-02'
        })
        self.assertEqual(res.status_code, 200)

    def test_delete_project(self):
        credentials = auth_header('homer', '1234')
        res = self.client.delete('/api/projects/1/', headers=credentials)
        self.assertEqual(res.status_code, 200)

class TestTasks(TestBase):
    def setUp(self):
        super().setUp()

    def test_create_task(self):
        credentials = auth_header('homer', '1234')
        res = self.client.post('/api/projects/1/tasks/', headers=credentials, json={
            'title': 'New Task',
            'creation_date': '2023-06-01',
            'completed': 0
        })
        self.assertEqual(res.status_code, 201)

    def test_get_tasks(self):
        credentials = auth_header('homer', '1234')
        res = self.client.get('/api/projects/1/tasks/', headers=credentials)
        self.assertEqual(res.status_code, 200)

    def test_update_task(self):
        credentials = auth_header('homer', '1234')
        res = self.client.put('/api/projects/1/tasks/1/', headers=credentials, json={
            'title': 'Updated Task',
            'completed': 1
        })
        self.assertEqual(res.status_code, 200)

    def test_delete_task(self):
        credentials = auth_header('homer', '1234')
        res = self.client.delete('/api/projects/1/tasks/1/', headers=credentials)
        self.assertEqual(res.status_code, 200)

if __name__ == '__main__':
    unittest.main()

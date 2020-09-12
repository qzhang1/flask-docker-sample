import json
import pytest
from project import db
from project.api.models import User


# happy path
def test_add_user(test_app, test_database):
    client = test_app.test_client()
    resp = client.post(
        '/users',
        data=json.dumps({
            'username': 'michael',
            'email': 'michael@testdriven.io'
        }),
        content_type='application/json'
    )
    data = json.loads(resp.data.decode())
    assert resp.status_code == 201
    assert 'michael@testdriven.io was added!' in data['message']


@pytest.mark.parametrize('json_input, status_code', [
    ({}, 400),
    ({'hello': 'world', 'username': 'bob'}, 400),
    ({'email': 'abc@xyz.com'}, 400),
    ({'email': '123', 'username': 'bob'}, 400),
    ({'email': 123}, 400)
])
def test_add_user_invalid_json_inputs(json_input, status_code, test_app, test_database):
    # arrange
    client = test_app.test_client()

    # act
    resp = client.post(
        '/users',
        data=json.dumps(json_input),
        content_type='application/json'
    )
    data = json.loads(resp.data.decode())

    # assert
    assert resp.status_code == 400
    assert 'Input payload validation failed' in data['message']


def test_add_user_no_payload_sent(test_app, test_database):
    # arrange
    client = test_app.test_client()

    # act
    resp = client.post('/users', content_type='application/json')
    data = json.loads(resp.data.decode())

    # assert
    assert resp.status_code == 400


def test_add_user_duplicate_email(test_app, test_database):
    client = test_app.test_client()
    # first post, just a throwaway
    client.post(
        '/users',
        data=json.dumps({
            'username': 'michael',
            'email': 'michael@testdriven.io'
        }),
        content_type='application/json'
    )
    resp = client.post(
        '/users',
        data=json.dumps({
            'username': 'michael',
            'email': 'michael@testdriven.io'
        }),
        content_type='application/json'
    )
    data = json.loads(resp.data.decode())
    assert resp.status_code == 400
    assert 'Sorry. That email already exists.' in data['message']


def test_get_single_user(test_app, test_database, add_user):
    """ happy path """
    user = add_user(username='jeffrey', email='jeffrey@testdriven.io')
    client = test_app.test_client()
    resp = client.get(f'/users/{user.id}')
    data = json.loads(resp.data.decode())
    assert resp.status_code == 200
    assert 'jeffrey' in data['username']
    assert 'jeffrey@testdriven.io' in data['email']


def test_get_nonexistent_user(test_app, test_database):
    client = test_app.test_client()

    resp = client.get(f'/users/999')
    data = json.loads(resp.data.decode())

    assert resp.status_code == 404


def test_all_users(test_app, test_database, add_user):
    test_database.session.query(User).delete()
    add_user('michael', 'michael@mherman.org')
    add_user('fletcher', 'fletcher@notreal.com')
    client = test_app.test_client()
    resp = client.get('/users')
    data = json.loads(resp.data.decode())
    assert resp.status_code == 200
    assert len(data) == 2

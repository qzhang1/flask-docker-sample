import pytest
from project import create_app, db
from project.api.models import User

# fixtures for tests to use (create app and database instances)
"""
Fixtures are reusable objects for tests. They have a scope associated with them, which indicates
how often the fixture is invoked:

1. function - once per test function (default)
2. class - once per test class
3. module - once per test module
4. session - once per test session

in each fixture there is proper setup and cleanup of the yielded objects.

Fixtures are by convention defined in conftest. It's recommended to use multiple conftest. One main root.
"""


@pytest.fixture(scope='module')
def test_app():
    app = create_app()
    app.config.from_object('project.config.TestingConfig')
    with app.app_context():
        yield app


@pytest.fixture(scope='module')
def test_database():
    db.create_all()
    yield db
    db.session.remove()
    db.drop_all()


@pytest.fixture(scope='function')
def add_user():
    """dependency that returns a helper function"""
    def _add_user(username, email):
        user = User(username=username, email=email)
        db.session.add(user)
        db.session.commit()
        return user
    return _add_user

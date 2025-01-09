from sqlalchemy import select

from fastzero.models import User


def test_create_user(session):
    user = User(
        username='gabriel', email='gabriel@email.com', password='12345'
    )

    session.add(user)
    session.commit()

    result = session.scalar(select(User).where(User.username == 'gabriel'))

    assert result.username == 'gabriel'

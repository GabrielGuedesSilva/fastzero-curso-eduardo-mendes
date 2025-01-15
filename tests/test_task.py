from http import HTTPStatus

from fastzero.models import Task, TaskState
from tests.conftest import TaskFactory


def test_create_task(client, token, mock_db_time):
    with mock_db_time(model=Task) as time:
        response = client.post(
            '/tasks/',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'title': 'title task',
                'description': 'description task',
                'state': 'draft',
            },
        )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'title': 'title task',
        'description': 'description task',
        'state': 'draft',
        'user_id': 1,
        'created_at': time.isoformat(),
        'updated_at': time.isoformat(),
    }


def test_get_tasks_should_return_5_tasks(session, client, user, token):
    expected_tasks = 5
    session.bulk_save_objects(TaskFactory.create_batch(5, user_id=user.id))
    session.commit()

    response = client.get(
        '/tasks/',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['tasks']) == expected_tasks


def test_get_tasks_pagination_should_return_2_tasks(
    session, client, user, token
):
    expected_tasks = 2
    session.bulk_save_objects(TaskFactory.create_batch(5, user_id=user.id))
    session.commit()

    response = client.get(
        '/tasks/?offset=1&limit=2',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['tasks']) == expected_tasks


def test_list_tasks_filter_title_should_return_5_tasks(
    session, client, user, token
):
    expected_tasks = 5
    session.bulk_save_objects(
        TaskFactory.create_batch(5, user_id=user.id, title='Test Task 1')
    )
    session.commit()

    response = client.get(
        '/tasks/?title=Test Task 1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['tasks']) == expected_tasks


def test_list_tasks_filter_description_should_return_5_tasks(
    session, client, user, token
):
    expected_tasks = 5
    session.bulk_save_objects(
        TaskFactory.create_batch(
            5, user_id=user.id, description='Test Description'
        )
    )
    session.commit()

    response = client.get(
        '/tasks/?description=Test Description',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['tasks']) == expected_tasks


def test_list_tasks_filter_state_should_return_5_tasks(
    session, client, user, token
):
    expected_tasks = 5
    session.bulk_save_objects(
        TaskFactory.create_batch(5, user_id=user.id, state=TaskState.DOING)
    )
    session.commit()

    response = client.get(
        '/tasks/?state=doing',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['tasks']) == expected_tasks


def test_get_tasks_filter_combined_should_return_5_tasks(
    session, user, client, token
):
    expected_tasks = 5
    session.bulk_save_objects(
        TaskFactory.create_batch(
            5,
            user_id=user.id,
            title='Test task combined',
            description='combined description',
            state=TaskState.DONE,
        )
    )

    session.bulk_save_objects(
        TaskFactory.create_batch(
            3,
            user_id=user.id,
            title='Other title',
            description='other description',
            state=TaskState.TODO,
        )
    )
    session.commit()

    response = client.get(
        '/tasks/?title=Test task combined&description=combined&state=done',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['tasks']) == expected_tasks


def test_delete_task(session, client, user, token):
    task = TaskFactory(user_id=user.id)
    session.add(task)
    session.commit()

    response = client.delete(
        f'/tasks/{task.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NO_CONTENT


def test_delete_task_not_found(client, token):
    response = client.delete(
        '/tasks/1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found'}


def test_patch_task_not_found(client, token):
    response = client.patch(
        '/tasks/1',
        headers={'Authorization': f'Bearer {token}'},
        json={},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found'}


def test_patch_task_title(client, session, user, token):
    task = TaskFactory(user_id=user.id)
    session.add(task)
    session.commit()
    session.refresh(task)

    response = client.patch(
        f'/tasks/{task.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'title': 'New title',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['title'] == 'New title'

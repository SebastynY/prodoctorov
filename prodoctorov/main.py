import requests
import os
from datetime import datetime as dt


def load_data(users_url: str, todos_url: str) -> tuple[dict, dict]:
    """Make a request and get data"""
    try:
        users = requests.get(users_url).json()
        todos = requests.get(todos_url).json()
        return users, todos
    except requests.exceptions.RequestException as error:
        raise SystemExit(error)


def create_directory(name: str) -> None:
    """Create a folder with files"""
    if not os.path.isdir(name):
        os.mkdir(name)


def make_user_data(user_info: dict) -> str:
    """Collect information in one line"""
    user_text = (
        f"Company report {user_info['company']['name']}.\n"
        f"{user_info['name']} "
        f"<{user_info['email']}> "
        f"{dt.strftime(dt.now(), '%d.%m.%Y %H:%M')}\n"
    )
    return user_text


def get_user_todos(user_info: dict, todos: dict) -> list:
    """Create a list of all tasks for one user"""
    user_todo = []
    try:
        for todo in todos:
            if todo['userId'] == user_info['id']:
                user_todo.append(todo)
    except KeyError as error:
        print(error)

    return user_todo


def make_user_todos(user_info: dict, todos: dict) -> str:
    """Create a line of todos"""
    todo_text = (
        f"Total tasks: {len(get_user_todos(user_info, todos))} \n"
    )
    completed_todo = list(filter(lambda todo: todo['completed'], get_user_todos(user_info, todos)))
    todo_text += f"\nCompleted tasks ({len(completed_todo)})\n"
    for todo in completed_todo:
        if len((title := todo['title'])) >= 48:
            todo_text += f'{title[:48]}...\n'
        else:
            todo_text += f'{title}\n'

    uncompleted_todo = list(filter(lambda todo: not todo['completed'], get_user_todos(user_info, todos)))
    todo_text += f"\nIncomplete tasks ({len(uncompleted_todo)})\n"
    for todo in uncompleted_todo:
        if len((title := todo['title'])) >= 48:
            todo_text += f'{title[:48]}...\n'
        else:
            todo_text += f'{title}\n'

    return todo_text


def make_general_data(user_info: dict, todos: dict) -> str:
    """Put all the information together"""
    general_data = make_user_data(user_info) + make_user_todos(user_info, todos)
    return general_data


def exist_file(file_name: str, user: dict) -> None:
    if os.path.exists(file_name):
        time_old_file = dt.fromtimestamp(os.path.getmtime(file_name)).strftime('%Y-%m-%dT%H-%M-%S')
        os.rename(file_name, f'./tasks/{user["username"]}_{time_old_file}.txt')


def create_file(users: dict, todos: dict) -> None:
    """ input -> {users} and {todos},
        output -> file (
        'Company report Yost and Sons' \
        'Glenna Reichert <Chaim_McDermott@dana.io> 05.05.2022 20:06'\
        'Total Tasks : 20' ... )"""

    for user in users:
        file_name = f'./tasks/{user["username"]}.txt'
        exist_file(file_name, user)
        with open(file_name, mode='w') as file:
            file.write(make_general_data(user, todos))


def main():
    users, todos = load_data('https://json.medrating.org/users', 'https://json.medrating.org/todos')
    create_directory('tasks')
    create_file(users, todos)


main()

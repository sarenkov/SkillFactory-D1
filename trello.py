import requests
import sys
from datetime import datetime
import json


class TrelloUtils:
    def __init__(self, key: str, token: str, desc: str):
        self.key = key
        self.token = token
        self.desc = desc
        self.base_url = "https://api.trello.com/1/{}"

        self.auth_params = {
            'key': self.key,
            'token': self.token
        }

    # Приветствие и меню
    def greeting(self):
        print('A utility for working with trello has been launched. Welcome!')
        print(
            "Commands:\n\
            \tread - view columns and tasks\n\
            \tcreate - task creation. You must specify the name of the task and the name of the column\n\
            \tmove - moving task. You must indicate the name of the task and the name of the column where you want to transfer\n\
            \tsearch - search for a task by name\n\
            \tadd-column - adding a column to the board\n\
            \ttask - view task content"
        )
        user_choice = input('Enter command:\n')
        print('-'*30)

        if user_choice == 'read':
            print('Columns and tasks:\n\n')
            self.read()

        elif user_choice == 'create':
            task_name = input('Enter name for task:\n')
            column_name = input('Enter name of column:\n')
            if self.check_column_name(column_name):
                self.create(task_name, column_name)
            else:
                print('Incorrect column name')

        elif user_choice == 'move':
            task_name = input('Enter name for task:\n')
            column_name = input('Enter name of column:\n')
            if self.check_column_name(column_name):
                self.move(task_name, column_name)
            else:
                print('Incorrect column name')

        elif user_choice == 'search':
            task_name = input('Enter name for task:\n')
            self.search(task_name)

        elif user_choice == 'add-column':
            column_name = input('Enter name of column:\n')
            self.add_column(column_name)

        elif user_choice == 'task':
            id = input('Enter your task id:\n')
            self.task(id)

        else:
            print('Unknown command\n')

        resume = input('Continue? y/n\n')
        if resume == 'y':
            self.greeting()
        else:
            exit()

    # Получение списка столбцов

    def get_column_data(self):
        return requests.get(self.base_url.format('boards') + '/' + self.desc + '/lists', params=self.auth_params).json()

    # Вывод списка столбцов и задач в них

    def read(self):
        column_data = self.get_column_data()

        for column in column_data:
            task_data = requests.get(self.base_url.format(
                'lists') + '/' + column['id'] + '/cards', params=self.auth_params).json()
            print(column['name'] + f' ({len(task_data)})')

            if not task_data:
                print('\tНет задач')
                continue
            for task in task_data:
                print('\t' + task['name'] + f"\t id: {task['id']}")

    # Создание новой задачи

    def create(self, name, column_name):
        column_data = self.get_column_data()
        all_tasks = []

        for column in column_data:
            task_data = requests.get(self.base_url.format(
                'lists') + '/' + column['id'] + '/cards', params=self.auth_params).json()

            for task in task_data:
                all_tasks.append(task['name'].lower())

            if column['name'] == column_name:
                print(
                    f'I’m checking the name "{name}" to match the ones already entered.')

                # Обработка кейса с созданием задачи с уже имеющимся именем
                if name.lower() not in all_tasks:
                    self.__create_task(name, column)
                else:
                    self.search(name)
                    select = input(
                        'To continue to create a task anyway? y/n\n')
                    if select == 'y':
                        self.__create_task(name, column)
                    else:
                        return

    # Перемещение задач между столбцами

    def move(self, name, column_name):
        column_data = self.get_column_data()

        task_id = None
        task_ids = {}

        for column in column_data:
            column_tasks = requests.get(self.base_url.format(
                'lists') + '/' + column['id'] + '/cards', params=self.auth_params).json()
            for task in column_tasks:
                if task['name'] == name:
                    task_id = task['id']
                    task_ids[task['id']] = task['name'] + '\t column: ' + column['name']
                    break
            if task_id:
                break
        if len(task_ids) == 1:
            for column in column_data:
                if column['name'] == column_name:
                    response = requests.put(self.base_url.format('cards') + '/' + task_id +
                                            '/idList', data={'value': column['id'], **self.auth_params})
                    if response.status_code == 200:
                        print('Task rescheduled')
                    else:
                        print(
                            f'task not rescheduled. Errors:\n{response.status_code}\n{response.text}')
                    break
        else:
            print(f'More tasks named "{name}" were found:\n')
            for pair in task_ids.items():
                print(f'\t{pair[0]}\t id: {pair[1]}')
            choice = input('Specify task id for transfer:\n')
            response = requests.put(self.base_url.format(
                'cards') + '/' + choice + '/idList', data={'value': column['id'], **self.auth_params})
            if response.status_code == 200:
                print('Task rescheduled')
            else:
                print(
                    f'task not rescheduled. Errors:\n{response.status_code}\n{response.text}')

    # Поиск задач по имени

    def search(self, name):
        column_data = self.get_column_data()
        finded = False

        for column in column_data:
            task_data = requests.get(self.base_url.format(
                'lists') + '/' + column['id'] + '/cards', params=self.auth_params).json()

            for task in task_data:
                if name == task['name']:
                    print(
                        f"Task '{name}' found in '{column['name']}'. Date of last activity: {datetime.strptime(task['dateLastActivity'], '%Y-%m-%dT%H:%M:%S.%fZ').date()}. Task id: {task['id']}")
                    finded = True
        if not finded:
            print(f"Tasks with name '{name}' not found")

    def task(self, id):
        response = requests.get(self.base_url.format(
            'cards') + '/' + id, params=self.auth_params)
        print(json.dumps(json.loads(response.text),
                         sort_keys=True, indent=4, separators=(",", ": ")))

    # Добавление колонки

    def add_column(self, name):
        board = self.get_board()
        response = requests.post(self.base_url.format('lists'), data={
            'name': name, 'idBoard': board, **self.auth_params})
        if response.status_code == 200:
            print(f'Column {name} was added')
        else:
            print(
                f'Column not added. Errors:\n{response.status_code}\n{response.text}')

    # Получение id доски

    def get_board(self):
        response = requests.get(self.base_url.format(
            f'boards/{self.desc}'), params=self.auth_params).json()
        return response['id']

    # Проверка имени столбуа при создании задачи

    def check_column_name(self, name):
        column_data = self.get_column_data()
        finded = False
        for column in column_data:
            if name == column['name']:
                finded = True
        return finded

    def __create_task(self, name, column):
        response = requests.post(self.base_url.format('cards'), data={
            'name': name, 'idList': column['id'], **self.auth_params})
        if response.status_code == 200:
            print(
                f"Task '{name}' successfully created in column '{column ['name']}'")
        else:
            print(
                f'Failed to create task. Reasons: \ n {response.text}')


if __name__ == "__main__":
    key = input('Enter your trello key:\n')
    token = input('Enter your trello token:\n')
    desc = input('Enter your trello desc id:\n')
    client = TrelloUtils(key, token, desc)
    client.greeting()

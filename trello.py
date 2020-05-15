import requests
import sys

auth_params = {
    'key': '8754bae918572b62e9828b8e563c5b2c',
    'token': '4ab78cd3eec4cd35c744f533c4818f761f8d095655702f2064b1efdb9dbd21fb'
}

base_url = "https://api.trello.com/1/{}"

board_id = 'b05ht2zO'

def get_column_data(data_type):
    return requests.get(base_url.format(data_type) + '/' + board_id + '/lists', params=auth_params).json() 


def read():
    column_data = get_column_data('boards')      

    for column in column_data:
        print(column['name'])

        task_data = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()      

        if not task_data:
            print('\tНет задач')
            continue
        for task in task_data:
            print('\t' + task['name'])  

def create(name, column_name):
    column_data = get_column_data('boards')     

    for column in column_data:      
        if column['name'] == column_name: 
            requests.post(base_url.format('cards'), data={'name': name, 'idList': column['id'], **auth_params})
            break

def move(name, column_name):
    column_data = get_column_data('boards')

    task_id = None

    for column in column_data:
        column_tasks = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()
        for task in column_tasks:    
            if task['name'] == name:    
                task_id = task['id']    
                break    
        if task_id:    
            break 

    for column in column_data:    
        if column['name'] == column_name:   
            requests.put(base_url.format('cards') + '/' + task_id + '/idList', data={'value': column['id'], **auth_params})    
            break 


if __name__ == "__main__":    
    if len(sys.argv) <= 2:    
        read()    
    elif sys.argv[1] == 'create':    
        create(sys.argv[2], sys.argv[3])    
    elif sys.argv[1] == 'move':    
        move(sys.argv[2], sys.argv[3]) 

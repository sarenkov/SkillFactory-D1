from trello import TrelloApi
import json

api_key = '8754bae918572b62e9828b8e563c5b2c'
token = '4ab78cd3eec4cd35c744f533c4818f761f8d095655702f2064b1efdb9dbd21fb'

trello = TrelloApi(api_key, token)

response = trello.boards.new("New board with API") 
id_board= response["id"]
columns = []
id_list = ''
for column in trello.boards.get_list(id_board):
    columns.append(column['name'])
    if 'Нужно' in column['name']:
        id_list = column['id']

card = trello.cards.new('Надо учиться', id_list)

print(card['id'])

print('\n'.join(columns))


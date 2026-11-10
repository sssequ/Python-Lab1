# слой данных: сущности мессенджера


# пользователь мессенджера
class User:
    def __init__(self, name):
        self.id = None
        self.name = name


# сообщение хранит id отправителя и чата
class Message:
    def __init__(self, sender_id, chat_id, text):
        self.id = None
        self.sender_id = sender_id
        self.chat_id = chat_id
        self.text = text


# чат хранит список участников
class Chat:
    def __init__(self, name, creator_id):
        self.id = None
        self.name = name
        self.user_ids = [creator_id]


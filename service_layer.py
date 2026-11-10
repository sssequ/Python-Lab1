from data_layer import User, Message, Chat
from repository_layer import Repository

# проверяет обязательные текстовые поля
def check_text(text, field):
    if not isinstance(text, str):
        raise TypeError(f"{field} должно быть строкой")
    if not text.strip():
        raise ValueError(f"{field} не должно быть пустым")


# сервисный слой: правила работы мессенджера
class MessengerService:
    def __init__(self, users: Repository, chats: Repository, messages: Repository):
        self.users = users
        self.chats = chats
        self.messages = messages

    # регистрирует пользователя с уникальным именем
    def register_user(self, name):
        check_text(name, "имя пользователя")
        if not name.isascii() or not name.isalpha():
            raise ValueError("имя должно содержать только английские буквы")

        for user in self.users.get_all():
            if user.name.lower() == name.lower():
                raise ValueError("это имя пользователя уже занято")
        return self.users.add(User(name))

    def get_users(self):
        return self.users.get_all()

    def get_user(self, user_id):
        return self.users.get(user_id)

    # создаёт чат и сразу добавляет его создателя
    def create_chat(self, name, creator_id):
        check_text(name, "название чата")
        self.users.get(creator_id)
        return self.chats.add(Chat(name.strip(), creator_id))

    def get_chats(self):
        return self.chats.get_all()

    # добавляет нового участника в чат
    def add_user_to_chat(self, chat_id, user_id):
        chat = self.chats.get(chat_id)
        self.users.get(user_id)
        if user_id in chat.user_ids:
            raise ValueError("пользователь уже состоит в чате")
        chat.user_ids.append(user_id)
        self.chats.update(chat)

    # проверяет, что пользователь состоит в чате
    def _check_member(self, chat_id, user_id):
        chat = self.chats.get(chat_id)
        self.users.get(user_id)
        if user_id not in chat.user_ids:
            raise PermissionError("пользователь не состоит в чате")

    # отправляет сообщение от участника чата
    def send_message(self, chat_id, sender_id, text):
        self._check_member(chat_id, sender_id)
        check_text(text, "сообщение")
        return self.messages.add(Message(sender_id, chat_id, text))

    def get_or_create_chat_between_users(self, first_user_id, second_user_id):
        first_user = self.users.get(first_user_id)
        second_user = self.users.get(second_user_id)

        chat = self.chats.find_chat_between_users(first_user_id, second_user_id)
        if chat is not None:
            return chat

        chat = self.chats.add(Chat(f"first_user_id, second_user_id", first_user_id))
        chat.user_ids.append(second_user_id)
        self.chats.update(chat)
        return chat

    def send_direct_message(self, sender_id, receiver_id, text):
        self.users.get(sender_id)
        self.users.get(receiver_id)
        if sender_id == receiver_id:
            raise ValueError("нельзя отправить сообщение самому себе")

        check_text(text, "сообщение")
        chat = self.get_or_create_chat_between_users(sender_id, receiver_id)
        return self.send_message(chat.id, sender_id, text)

    # возвращает историю сообщений выбранного чата
    def read_messages(self, chat_id, user_id):
        self._check_member(chat_id, user_id)
        return [message for message in self.messages.get_all()
                if message.chat_id == chat_id]

    # разрешает менять и удалять только свои сообщения
    def _get_own_message(self, message_id, user_id):
        message = self.messages.get(message_id)
        self._check_member(message.chat_id, user_id)
        if message.sender_id != user_id:
            raise PermissionError("можно изменять и удалять только свои сообщения")
        return message

    def edit_message(self, message_id, user_id, new_text):
        message = self._get_own_message(message_id, user_id)
        check_text(new_text, "сообщение")
        message.text = new_text
        return self.messages.update(message)

    def delete_message(self, message_id, user_id):
        self._get_own_message(message_id, user_id)
        self.messages.delete(message_id)

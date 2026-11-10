from pathlib import Path

from data_layer import User, Chat, Message
from repository_layer import JsonRepository
from service_layer import MessengerService


# точка входа: консольное меню, ввод и вывод
MENU = """
1. зарегистрировать пользователя
2. показать пользователей
3. создать чат
4. показать чаты
5. добавить участника в чат
6. отправить сообщение
7. показать сообщения
8. изменить сообщение
9. удалить сообщение
10. отправить личное сообщение
0. выйти из программы
"""


# переводит введённый id в число
def read_id(prompt):
    try:
        item_id = int(input(prompt))
    except ValueError:
        raise ValueError("id должен быть целым числом") from None
    if item_id < 1:
        raise ValueError("id должен быть больше нуля")
    return item_id


def main():
    # для каждого вида сущностей используется отдельный репозиторий
    data_path = Path(__file__).resolve().parent
    service = MessengerService(
        JsonRepository(data_path / "users.json", User),
        JsonRepository(data_path / "chats.json", Chat),
        JsonRepository(data_path / "messages.json", Message)
    )

    while True:
        try:
            print(MENU)
            choice = input("выберите действие: ").strip()

            if choice == "0":
                print("программа завершена")
                break

            elif choice == "1":
                user = service.register_user(input("имя английскими буквами: "))
                print(f"пользователь создан, id: {user.id}")

            elif choice == "2":
                users = service.get_users()
                if not users:
                    print("пользователей пока нет")
                for user in users:
                    print(f"{user.id}. {user.name}")

            elif choice == "3":
                name = input("название чата: ")
                user_id = read_id("id создателя: ")
                chat = service.create_chat(name, user_id)
                print(f"чат создан, id: {chat.id}")

            elif choice == "4":
                chats = service.get_chats()
                if not chats:
                    print("чатов пока нет")
                for chat in chats:
                    print(f"{chat.id}. {chat.name} — участников: {len(chat.user_ids)}")

            elif choice == "5":
                chat_id = read_id("id чата: ")
                user_id = read_id("id пользователя: ")
                service.add_user_to_chat(chat_id, user_id)
                print("участник добавлен")

            elif choice == "6":
                chat_id = read_id("id чата: ")
                user_id = read_id("id отправителя: ")
                message = service.send_message(chat_id, user_id, input("сообщение: "))
                print(f"сообщение отправлено, id: {message.id}")

            elif choice == "7":
                chat_id = read_id("id чата: ")
                user_id = read_id("id читателя: ")
                messages = service.read_messages(chat_id, user_id)
                if not messages:
                    print("сообщений пока нет")
                for message in messages:
                    sender = service.get_user(message.sender_id)
                    print(f"{message.id}. {sender.name}: {message.text}")

            elif choice == "8":
                message_id = read_id("id сообщения: ")
                user_id = read_id("id отправителя: ")
                service.edit_message(message_id, user_id, input("новый текст: "))
                print("сообщение изменено")

            elif choice == "9":
                message_id = read_id("id сообщения: ")
                user_id = read_id("id отправителя: ")
                service.delete_message(message_id, user_id)
                print("сообщение удалено")

            elif choice == "10":
                sender_id = read_id("id отправителя: ")
                reciever_id = read_id("id получателя: ")
                text = input("сообщение: ")
                message = service.send_direct_message(sender_id, reciever_id, text)
                print(f"сообщение отправлено. id: {message.id}")

            else:
                print("такого действия нет, выберите пункт меню")

        # ошибки не закрывают меню, можно попробовать ещё раз
        except (ValueError, TypeError, PermissionError) as error:
            print(f"ошибка: {error}")
        except (EOFError, KeyboardInterrupt):
            print("\nпрограмма завершена")
            break


if __name__ == "__main__":
    main()

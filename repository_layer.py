from abc import ABC, abstractmethod
import json
from pathlib import Path


# слой репозитория: общий набор операций для любого хранилища
class Repository(ABC):
    @abstractmethod
    def add(self, item):
        pass

    @abstractmethod
    def get(self, item_id):
        pass

    @abstractmethod
    def get_all(self):
        pass

    @abstractmethod
    def update(self, item):
        pass

    @abstractmethod
    def delete(self, item_id):
        pass


# хранит сущности в словаре до закрытия программы
class MemoryRepository(Repository):
    def __init__(self):
        self._items = {}
        self._next_id = 1

    # сохраняет новый объект и назначает ему id
    def add(self, item):
        if item.id is not None:
            raise ValueError("объект уже был сохранён")

        item.id = self._next_id
        self._items[item.id] = item
        self._next_id += 1
        return item

    # находит объект по id
    def get(self, item_id):
        if item_id not in self._items:
            raise ValueError(f"объект с id {item_id} не найден")

        return self._items[item_id]

    # возвращает список всех объектов
    def get_all(self):
        return list(self._items.values())

    def find_chat_between_users(self, first_user_id, second_user_id):
        for chat in self._items.values():
            if set(chat.user_ids) == {first_user_id, second_user_id}:
                return chat
        return None

    # заменяет сохранённый объект
    def update(self, item):
        self.get(item.id)
        self._items[item.id] = item
        return item

    # удаляет объект по id
    def delete(self, item_id):
        self.get(item_id)
        del self._items[item_id]


# хранит сущности в json и загружает их при запуске
class JsonRepository(MemoryRepository):
    def __init__(self, filename, item_type):
        super().__init__()
        self.filename = Path(filename)
        if self.filename.exists():
            with self.filename.open(encoding="utf-8") as file:
                data = json.load(file)
            self._next_id = data["next_id"]
            for values in data["items"]:
                item = item_type.__new__(item_type)
                item.__dict__.update(values)
                self._items[item.id] = item

    def _save(self):
        data = {"next_id": self._next_id,
                "items": [item.__dict__ for item in self._items.values()]}
        with self.filename.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def add(self, item):
        item = super().add(item)
        self._save()
        return item

    def update(self, item):
        item = super().update(item)
        self._save()
        return item

    def delete(self, item_id):
        super().delete(item_id)
        self._save()

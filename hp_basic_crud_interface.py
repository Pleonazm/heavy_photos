from abc import ABC, abstractmethod

class BasicCRUDInterface(ABC):

    @abstractmethod
    def make(self) -> None:
        raise NotImplementedError("Subclasses must implement this method.")
    def remake(self, data=None):
        raise NotImplementedError("Subclasses must implement this method.")
    @abstractmethod
    def unmake(self) -> bool:
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def add(self, data:dict) -> None:
        raise NotImplementedError("Subclasses must implement this method.")
    @abstractmethod
    def get(self, id:str) -> dict:
        raise NotImplementedError("Subclasses must implement this method.")
    @abstractmethod
    def get_all(self) -> list:
        raise NotImplementedError("Subclasses must implement this method.")
    @abstractmethod
    def find(self, data:dict) -> dict:
        raise NotImplementedError("Subclasses must implement this method.")
    @abstractmethod
    def update(self, data:dict) -> dict:
        raise NotImplementedError("Subclasses must implement this method.")
    @abstractmethod
    def delete(self, id:str):
        raise NotImplementedError("Subclasses must implement this method.")
    @abstractmethod
    def delete_all(self) -> bool:
        raise NotImplementedError("Subclasses must implement this method.")

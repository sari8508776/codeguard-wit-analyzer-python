from abc import ABC, abstractmethod

class Ui(ABC):
    @abstractmethod
    def run(self):
        pass
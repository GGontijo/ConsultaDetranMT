from abc import ABC, abstractmethod

class SeleniumInterface(ABC):

    @abstractmethod
    def run() -> str:
        pass

    @abstractmethod
    def prepare() -> str:
        '''source: detran | secon   
       parameters:
        -> "placa": "XXXXX"
        -> "renavam: "YYYYYY"'''
        pass

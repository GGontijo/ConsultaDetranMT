from fastapi import FastAPI
import uvicorn
from routes.detran_route import detran_router

class Server():
    
    def __init__(self) -> None:
        self.api = FastAPI()
        self.api.include_router(detran_router)
        uvicorn.run(self.api, port=8000)
        

if __name__ == '__main__':
    api = Server()
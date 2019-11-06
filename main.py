from dccontroller import DogCamController
from dcsocket import DogCamWebSocket
import dcserver
import asyncio

async def main():
  CamControl = DogCamController()
  SocketServer = DogCamWebSocket()
  
  while True:
    await asyncio.sleep(5)

if __name__ == "__main__":
  asyncio.run(main())

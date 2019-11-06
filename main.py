from dccontroller import DogCamController
from dcsocket import DogCamWebSocket
import dcserver
import asyncio

async def main():
  CamControl = DogCamController()
  SocketServer = DogCamWebSocket()
  
  while True:
    try:
      await asyncio.sleep(5)
    except KeyboardInterrupt:
      return

if __name__ == "__main__":
  asyncio.run(main())

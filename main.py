from dccontroller import DogCamController
from dcsocket import DogCamWebSocket
import dcserver
import asyncio

async def main():
  CamControl = DogCamController()
  SocketServer = DogCamWebSocket()
  dcserver.StartWebserver()
  
  print(f"Camera Controller at {str(CamControl)} and\nSocket Server at {str(SocketServer)}")
  
  while True:
    try:
      await asyncio.sleep(5)
    except KeyboardInterrupt:
      return

if __name__ == "__main__":
  asyncio.run(main())

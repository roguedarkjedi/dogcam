from dccontroller import DogCamController
from dcwebsocket import DogCamWebSocket
import dcwebserver
import asyncio

async def main():
  CamControl = DogCamController()
  SocketServer = DogCamWebSocket()
  dcwebserver.StartWebserver()

  print(f"Camera Controller at {str(CamControl)} and\nSocket Server at {str(SocketServer)}")

  while True:
    try:
      await asyncio.sleep(5)
    except KeyboardInterrupt:
      return

if __name__ == "__main__":
  asyncio.run(main())

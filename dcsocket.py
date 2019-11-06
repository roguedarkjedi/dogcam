from dccontroller import DogCamController
from datetime import datetime
import asyncio
import websockets
import threading
import json

__all__ = ("DogCamWebSocket")

# This makes a websocket for taking in remote commands
class DogCamWebSocket():
  WSThread = None
  
  def __init__(self):
    print("Starting websocket")
    self.WSThread = threading.Thread(target=self.RunServer, daemon=True)
    self.WSThread.start()
  
  def RunServer(self):
    NewLoop = asyncio.new_event_loop()
    asyncio.set_event_loop(NewLoop)
    NewLoop.run_until_complete(websockets.serve(DCHandler, "0.0.0.0", 5867))
    NewLoop.run_forever()
  
async def DCHandler(websocket, path):
  print("Handling websocket messages")
  async for RawData in websocket:

    try:
      jsonData = json.loads(RawData)
    except Exception as ex:
      print(ex)
      continue

    DCCI = DogCamController.Instance
    ServoName = jsonData["servo"].lower()
    ServoAction = jsonData["action"].lower()
    ServoAngle = jsonData.get("angle")
    ActionHandled = True
    
    if ServoAction == "reset":
      print("Handling reset command")
      DCCI.ResetServo(ServoName)
    elif ServoAction == "moverel":
      print(f"Moving {ServoName} relatively")
      DCCI.MoveServoTo(ServoName, RelativeAngle=ServoAngle)
    elif ServoAction == "moveabs":
      print(f"Moving {ServoName} absolutely")
      DCCI.MoveServoTo(ServoName, AbsoluteAngle=ServoAngle)
    elif ServoAction == "moveinterp":
      print(f"Moving {ServoName} interpretively")
      DCCI.MoveServoTo(ServoName, InterpAngle=ServoAngle)
    elif ServoAction == "resetall":
      print("All servos going to reset")
      DCCI.ResetAllServos()
    else:
      print("Message unhandled!")
      ActionHandled = False
      
    ResponseBlob = {"time": str(datetime.now()),
                    "status": ActionHandled, 
                    "action": ServoAction}
    
    print("Sending reply")
    await websocket.send(json.dumps(ResponseBlob))

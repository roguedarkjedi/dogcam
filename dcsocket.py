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
  WSLoop = None
  
  def __init__(self):
    print("Starting websocket")
    self.WSThread = threading.Thread(target=self.RunServer, daemon=True)
    self.WSThread.start()
  
  def RunServer(self):
    self.WSLoop = asyncio.new_event_loop()
    asyncio.set_event_loop(self.WSLoop)
    self.WSLoop.run_until_complete(websockets.serve(DCHandler, "", 5867))
    self.WSLoop.run_forever()
  
async def DCHandler(websocket, path):
  print("Handling websocket messages")
  async for RawData in websocket:

    try:
      jsonData = json.loads(RawData)
    except Exception as ex:
      print(f"Encountered Exception in WebSock: {str(ex)}\nWith Raw Data {RawData}")
      continue

    # Require flags in request
    if "action" not in jsonData:
      continue
    
    DCCI = DogCamController.Instance
    if "servo" not in jsonData:
      ServoName = "none"
    else:
      ServoName = jsonData["servo"].lower()
    
    ActionSource = jsonData.get("source")
    ServoAction = jsonData["action"].lower()
    ServoAngle = jsonData.get("angle")
    ActionHandled = True
    
    if ActionSource == "dogcamai" and DCCI.AIDisabled is True:
      ActionHandled = False
    elif ServoAction == "disableai":
      DCCI.AIDisabled = True
    elif ServoAction == "enableai":
      DCCI.AIDisabled = False
    elif ServoAction == "left":
      DCCI.MoveServoLeft()
    elif ServoAction == "right":
      DCCI.MoveServoRight()
    elif ServoAction == "up" or ServoAction == "top":
      DCCI.MoveServoUp()
    elif ServoAction == "down" or ServoAction == "bottom":
      DCCI.MoveServoDown()
    elif ServoAction == "reset":
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
    elif ServoAction == "curangles":
      print("Sending back current angles")
    else:
      print("Message unhandled!")
      ActionHandled = False
      
    ResponseBlob = {"time": str(datetime.now()),
                    "status": ActionHandled, 
                    "action": ServoAction,
                    "AIDisabled": DCCI.AIDisabled,
                    "tiltCurrentAngle": DCCI.GetCurrentAngle("tilt"),
                    "panCurrentAngle": DCCI.GetCurrentAngle("pan")}
    
    print("Sending reply")
    await websocket.send(json.dumps(ResponseBlob))

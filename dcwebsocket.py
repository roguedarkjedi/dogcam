from dccontroller import DogCamController
from datetime import datetime
import asyncio
import websockets
import threading
import json

# This makes a websocket for taking in remote commands
class DogCamWebSocket():
  WSThread = None
  WSLoop = None
  __clients = set()

  def __init__(self):
    print("Starting websocket")
    self.WSThread = threading.Thread(target=self.RunServer, daemon=True)
    self.WSThread.start()

  def RunServer(self):
    self.WSLoop = asyncio.new_event_loop()
    asyncio.set_event_loop(self.WSLoop)
    self.WSLoop.run_until_complete(websockets.serve(self.__ClientConnection, "", 5867))
    self.WSLoop.run_forever()

  async def SendToAllClients(self, Message, MsgType="info"):
    if len(self.__clients) == 0:
      return

    await asyncio.wait([self.SendMessageToClient(client, Message, MsgType) for client in self.__clients])

  async def SendMessageToClient(self, websocket, Msg, MsgType="info", WasHandled=True, AttachAngles=False):
    if websocket is None:
      return

    DCCI = DogCamController.Instance

    # Generate response message JSON for clients that need to know current status
    ResponseBlob = {"time": str(datetime.now()),
                    "status": WasHandled,
                    "type": MsgType,
                    "data": Msg,
                    "AIDisabled": DCCI.AIDisabled}

    if AttachAngles:
      ResponseBlob.update({
        "tiltCurrentAngle": DCCI.GetCurrentAngle("tilt"),
        "panCurrentAngle": DCCI.GetCurrentAngle("pan")
      })

    print(f"Sending reply to {websocket.remote_address}")
    # Push the message back.
    await websocket.send(json.dumps(ResponseBlob))

  # Handles the lifetime of all the clients
  async def __ClientConnection(self, websocket, path):
    # While unlikely, if we hit any exceptions, we need to make sure to get rid of the socket data
    try:
      await self.__RegisterClient(websocket)
      await self.__ClientUpdate(websocket, path)
    finally:
      await self.__UnregisterClient(websocket)

  # Websocket message handler, basically the general loop of this entire thing
  async def __ClientUpdate(self, websocket, path):
    print(f"Handling websocket messages for new client {websocket.remote_address}")

    # Poll messages forever
    async for RawData in websocket:
      try:
        jsonData = json.loads(RawData)
      except Exception as ex:
        print(f"Encountered Exception in WebSock: {str(ex)}\nWith Raw Data {RawData}")
        continue

      DCCI = DogCamController.Instance

      # Attempt to figure out what servo this should target
      if "servo" not in jsonData:
        # Likely a both command then
        ServoName = "none"
      else:
        ServoName = jsonData["servo"].lower()

      # Attempt to figure out what this is supposed to do
      if "type" in jsonData:
        ActionType = jsonData["type"].lower()
      else:
        # Backwards compatibility with previous code and projects
        ActionType = "action"

      # Pull some general data flags from the message
      ActionSource = jsonData.get("source")
      ActionHandled = True
      SendAngles = True

      # Backwards compatibility
      if "action" in jsonData:
        ServoAction = jsonData["action"].lower()
      else:
        ServoAction = "none"

      # Attempt to handle different forms of data
      if ActionType == "message":
        # Pull the message data out
        if not "message" in jsonData:
          # Doesn't exist so don't even bother
          continue
        MessageData = str(str(jsonData["message"]).encode(encoding="ascii", errors="replace"))
        await self.SendToAllClients(MessageData, ActionType)
        continue
      elif ActionType == "status":
        # Essentially a "curangles" command
        ActionHandled = True
        SendAngles = True
      # The ugliest branch conditional ever
      elif ActionType == "action":
        ServoAngle = jsonData.get("angle")

        if ActionSource == "dogcamai" and DCCI.AIDisabled is True:
          ActionHandled = False
          SendAngles = False
        elif ServoAction == "disableai":
          DCCI.AIDisabled = True
          SendAngles = False
        elif ServoAction == "enableai":
          DCCI.AIDisabled = False
          SendAngles = False

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
          SendAngles = True
          # Change the ActionType flag to early signal deprecation but no enforcement yet.
          ActionType="status"
        else:
          print("Message unhandled!")
          ActionHandled = False
          SendAngles = False
          ServoAction = f"Unhandled Action: {ActionType}: {ServoAction}"
          ActionType = "info"
      else:
        print(f"Unhandled action type: {ActionType}!")
        ActionHandled = False
        SendAngles = False
        ServoAction = f"Unhandled action type: {ActionType}"
        ActionType = "info"

      await self.SendMessageToClient(websocket, ServoAction, MsgType=ActionType, AttachAngles=SendAngles, WasHandled=ActionHandled)

  # We probably could get around having to pull and save this information by looking at the sockets the server has opened
  # But this is probably the quickest and dirtiest option instead.
  async def __RegisterClient(self, websocket):
    self.__clients.add(websocket)

  async def __UnregisterClient(self, websocket):
    self.__clients.remove(websocket)

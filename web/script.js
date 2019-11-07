var output;
var panAngle;
var tiltAngle;
var TiltAngleOffset=10.0;
var PanAngleOffset=10.0;

function CreateWebsocket()
{
  output = document.getElementById("robotconsole");
  panAngle = document.getElementById("panangle");
  tiltAngle = document.getElementById("tiltangle");
  
  websocket = new WebSocket("ws://192.168.50.169:5867/");
  websocket.onopen = function(evt) { onOpen(evt) };
  websocket.onclose = function(evt) { onClose(evt) };
  websocket.onmessage = function(evt) { onMessage(evt) };
  websocket.onerror = function(evt) { onError(evt) };
  console.log("Ready");
}

function onOpen(evt)
{
  writeToScreen("CONNECTED");
}

function onClose(evt)
{
  writeToScreen("DISCONNECTED");
}

function onMessage(evt)
{
  var responseMessage = JSON.parse(evt.data);  
  writeToScreen('<span style="color: blue;">RESPONSE: ' + evt.data+'</span>');
  panAngle.innerHTML = responseMessage.panCurrentAngle;
  tiltAngle.innerHTML = responseMessage.tiltCurrentAngle;
}

function onError(evt)
{
  writeToScreen('<span style="color: red;">ERROR:</span> ' + evt.data);
}

function writeToScreen(message)
{
  var pre = document.createElement("p");
  pre.style.wordWrap = "break-word";
  pre.innerHTML = message;
  output.appendChild(pre);
}

function moveUp()
{
  websocket.send('{"servo": "tilt", "action": "moverel", "angle": '+TiltAngleOffset+'}');
}

function moveDown()
{
  websocket.send('{"servo": "tilt", "action": "moverel", "angle": -'+TiltAngleOffset+'}');
}

function moveLeft()
{
  websocket.send('{"servo": "pan", "action": "moverel", "angle": -'+PanAngleOffset+'}');
}

function moveRight()
{
  websocket.send('{"servo": "pan", "action": "moverel", "angle": '+PanAngleOffset+'}');
}

function resetPan()
{
  websocket.send('{"servo": "pan", "action": "reset"}');
}

function resetTilt()
{
  websocket.send('{"servo": "tilt", "action": "reset"}');
}

function resetAll()
{
  websocket.send('{"servo": "tilt", "action": "resetall"}');
}

window.addEventListener("load", CreateWebsocket);

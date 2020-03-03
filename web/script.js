var output;
var panAngle;
var tiltAngle;
var aiStatusText;
var websocket;
var aiStatus=false;

/*
A lot of code is shamelessly copied from https://www.websocket.org/echo.html and is pretty awful.
*/

function writeToScreen(message)
{
  if (!output)
  {
   return; 
  }
  
  var pre = document.createElement("p");
  pre.style.wordWrap = "break-word";
  pre.innerHTML = message;
  output.appendChild(pre);
}

function getCurrentAngles()
{
  websocket.send('{"servo": "tilt", "action": "curangles"}');
}

function onOpen()
{
  writeToScreen("CONNECTED");
  setInterval(getCurrentAngles, 15000);
}

function onClose()
{
  writeToScreen("DISCONNECTED");
}

function onMessage(evt)
{
  var responseMessage = JSON.parse(evt.data);  
  writeToScreen('<span style="color: blue;">RESPONSE: ' + evt.data+'</span>');
  panAngle.innerText = responseMessage.panCurrentAngle;
  tiltAngle.innerText = responseMessage.tiltCurrentAngle;
  aiStatusText.innerText = responseMessage.AIDisabled;
  aiStatus = responseMessage.AIDisabled;
}

function onError(evt)
{
  writeToScreen('<span style="color: red;">ERROR:</span> ' + evt.data);
}

function moveUp()
{
  websocket.send('{"action": "up"}');
}

function moveDown()
{
  websocket.send('{"action": "down"}');
}

function moveLeft()
{
  websocket.send('{"action": "left"}');
}

function moveRight()
{
  websocket.send('{"action": "right"}');
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

function toggleAI()
{
  var aiCommand = (aiStatus) ? "enableai" : "disableai";
  websocket.send('{"action": '+aiCommand+'}');
  aiStatus = !aiStatus;
}

function CreateWebsocket()
{
  output = document.getElementById("robotconsole");
  panAngle = document.getElementById("panangle");
  tiltAngle = document.getElementById("tiltangle");
  aiStatusText = document.getElementById("aistatus");
  
  websocket = new WebSocket("ws://"+window.location.hostname+":5867/");
  websocket.onopen = function(evt) { onOpen(); };
  websocket.onclose = function(evt) { onClose(); };
  websocket.onmessage = function(evt) { onMessage(evt); };
  websocket.onerror = function(evt) { onError(evt); };
  console.log("Ready");
}

window.addEventListener("load", CreateWebsocket);

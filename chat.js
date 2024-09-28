const topic = window.location.pathname.split("/").pop();
const ws = new WebSocket("wss://" + window.location.host + "/chat/" + topic);

document.title = document.title + " " + topic;
document.getElementById("title").textContent += " " + topic;

ws.onopen = () => {
    console.log("Connected to the WebSocket server");
};

ws.onmessage = (event) => {
    const chatbox = document.getElementById("chatbox");
    const message = document.createElement("div");
    message.textContent = event.data;
    chatbox.appendChild(message);
};

function sendMessage() {
    const input = document.getElementById("message");
    ws.send(input.value);
    input.value = "";
}
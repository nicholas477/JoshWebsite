const topic = window.location.pathname.split("/").pop()
console.log(topic)
const ws = new WebSocket("wss://" + window.location.host + "/chat/" + topic);

document.title = document.title + " " + topic

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
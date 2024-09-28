from aiohttp import web
from aiohttp.http_websocket import WSCloseCode, WSMessage
from aiohttp.web_request import Request

async def index(request):
    return web.FileResponse('./index.html')

async def chat(request):
    return web.FileResponse('./chat.html')

async def chatjs(request):
    print("someone is going to chat.js")
    return web.FileResponse('./chat.js')

class ChatRoom:
    connected_clients: set[web.WebSocketResponse]
    topic: str

    def __init__(self, topic: str):
        self.connected_clients = set()
        self.topic = topic

    async def wshandle(self, request: Request, ws: web.WebSocketResponse):
        await ws.prepare(request)

        print("New chat user for topic: {topic}!".format(topic=self.topic))
        self.connected_clients.add(ws)

        async for msg in ws:
            if msg.type == web.WSMsgType.close:
                print("{client} left chatroom {topic}".format(client=str(request.remote), topic=self.topic))
                self.connected_clients.remove(ws)
                break

            elif msg.type == web.WSMsgType.text:
                print(str(request.remote) + " said: " + msg.data)
                for client in self.connected_clients:
                    if not client.closed and not client._closing:
                        await client.send_str(msg.data)

        return ws

chatrooms = dict()
def get_chatroom(room: str):
    if not room in chatrooms:
        chatrooms[room] = ChatRoom(room)

    return chatrooms[room]


async def handle_chat(request: Request) -> web.WebSocketResponse:
    ws = web.WebSocketResponse()
    ready = ws.can_prepare(request=request)
    if not ready:
        # not a websocket connection
        print("someone is going to chat.html")
        return web.FileResponse("chat.html")
    
    room = request.match_info.get('topic', 'default')
    chatroom = get_chatroom(room)
    await chatroom.wshandle(request, ws)
    return ws

app = web.Application()
app.add_routes([web.get('/', index),
                web.get('/chat.js', chatjs),
                web.get('/chat/{topic}', handle_chat)])

if __name__ == "__main__":
    print("Running chatroom...")
    web.run_app(app, host='0.0.0.0', port=6789)
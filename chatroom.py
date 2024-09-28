from aiohttp import web
from aiohttp.http_websocket import WSCloseCode, WSMessage
from aiohttp.web_request import Request
from log import print

class ChatUser:
    ws: web.WebSocketResponse
    usernum: int

    def __init__(self, ws: web.WebSocketResponse, usernum: int):
        self.ws = ws
        self.usernum = usernum

    def __hash__(self):
        return hash(self.ws)
    
    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.ws == other.ws
        elif isinstance(other, web.WebSocketResponse):
            return self.ws == other
        else: return NotImplemented

class ChatRoom:
    connected_clients: set[ChatUser]
    topic: str
    numusers: int

    def __init__(self, topic: str):
        self.connected_clients = set()
        self.topic = topic
        self.numusers = 1

    def get_remote(self, request: Request, c: ChatUser) -> str:
        usernum = str(c.usernum)
        return "{ip} (user {usernum})".format(ip=request.headers["Cf-Connecting-Ip"], usernum=usernum)

    async def broadcast_message(self, msg: str):
        for client in self.connected_clients:
            if not client.ws.closed and not client.ws._closing:
                await client.ws.send_str(msg)

    async def remove_client(self, request: Request, c: ChatUser):
        print("{client} left chatroom {topic}".format(client=self.get_remote(request, c), topic=self.topic))
        self.connected_clients.remove(c)
        await self.broadcast_message("User {usernum} left chatroom".format(usernum=str(c.usernum)))

    async def wshandle(self, request: Request, ws: web.WebSocketResponse) -> web.WebSocketResponse:
        await ws.prepare(request)

        user = ChatUser(ws, self.numusers)
        await self.broadcast_message("User {usernum} joined chatroom".format(usernum=str(user.usernum)))
        self.connected_clients.add(user)
        self.numusers = self.numusers + 1

        print("{client} joined chatroom for topic: {topic}!".format(client=self.get_remote(request, user), topic=self.topic))
        await ws.send_str("Welcome to chatroom for topic: {topic}, there are {usernum} users connected".format(topic=self.topic, usernum=len(self.connected_clients)))
        await ws.send_str("You are user number: {usernum}".format(usernum=user.usernum))

        async for msg in ws:
            if msg.type == web.WSMsgType.close:
                break

            elif msg.type == web.WSMsgType.error:
                print('ws connection closed with exception %s' % ws.exception())
                break

            elif msg.type == web.WSMsgType.text:
                print(self.get_remote(request, user) + " said: " + msg.data)
                await self.broadcast_message("User {usernum}: {msg}".format(usernum=str(user.usernum), msg=msg.data))

        await self.remove_client(request, user)
        return ws

chatrooms = dict()
def get_chatroom(room: str):
    roomlower = room.lower()
    if not roomlower in chatrooms:
        chatrooms[roomlower] = ChatRoom(roomlower)

    return chatrooms[roomlower]
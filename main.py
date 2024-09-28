from aiohttp import web
from aiohttp.http_websocket import WSCloseCode, WSMessage
from aiohttp.web_request import Request
from log import print

from chatroom import *

async def index(request):
    return web.FileResponse('./index.html')

async def chat(request):
    return web.FileResponse('./chat.html')

async def style(request):
    return web.FileResponse('./style.css')

async def chatjs(request):
    return web.FileResponse('./chat.js')

async def handle_chat(request: Request) -> web.WebSocketResponse:
    ws = web.WebSocketResponse()
    ready = ws.can_prepare(request=request)
    if not ready:
        # not a websocket connection
        return web.FileResponse("chat.html")
    
    room = request.match_info.get('topic', 'default')
    chatroom = get_chatroom(room)
    await chatroom.wshandle(request, ws)
    return ws

app = web.Application()
app.add_routes([web.get('/', index),
                web.get('/chat.js', chatjs),
                web.get('/style.css', style),
                web.get('/chat/{topic}', handle_chat)])

if __name__ == "__main__":
    print("Running chatroom...")
    web.run_app(app, host='0.0.0.0', port=6789)
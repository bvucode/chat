from fastapi import FastAPI, WebSocket
from typing import List
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()

templates = Jinja2Templates(directory="templates")

# Список подключенных клиентов
connected_clients = []

# Очередь сообщений
message_queue = []

# WebSocket для веб-интерфейса чата
@app.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    await websocket.accept()
    # Добавляем клиента в список подключенных
    connected_clients.append({"websocket": websocket, "username": username})
    # Приветственное сообщение для нового клиента
    welcome_message = f"Привет, {username}! Добро пожаловать в чат!"
    await websocket.send_text(welcome_message)
    
    # Отправляем сообщения из очереди (если они есть)
    for message in message_queue:
        await websocket.send_text(message)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = f"{username}: {data}"
            # Добавляем сообщение в очередь
            message_queue.append(message)
            # Отправляем сообщение всем подключенным клиентам
            for client in connected_clients:
                await client["websocket"].send_text(message)
    except WebSocketDisconnect:
        # Удаляем клиента из списка при отключении
        connected_clients.remove({"websocket": websocket, "username": username})

# Веб-страница для входа в чат
@app.get("/", response_class=HTMLResponse)
async def chat_interface(request):
    return templates.TemplateResponse("chat.html", {"request": request})

# HTML-шаблон для веб-интерфейса чата (templates/chat.html)
# Вам нужно создать директорию "templates" и поместить этот файл туда.
# Здесь мы предоставляем простой интерфейс для ввода имени пользователя и подключения к чату.

# chat.html
"""
<!DOCTYPE html>
<html>
<head>
    <title>Real-time Chat</title>
</head>
<body>
    <h1>Real-time Chat</h1>
    <form>
        <label for="username">Введите ваше имя: </label>
        <input type="text" id="username" required>
        <button type="button" onclick="connectToChat()">Подключиться</button>
    </form>
    <div id="chatbox" style="border: 1px solid #ccc; width: 300px; height: 200px; overflow-y: scroll;"></div>
    <form>
        <input type="text" id="message" required>
        <button type="button" onclick="sendMessage()">Отправить</button>
    </form>

    <script>
        let socket;
        let username;
        const chatbox = document.getElementById("chatbox");

        function connectToChat() {
            username = document.getElementById("username").value;
            if (username) {
                socket = new WebSocket(`ws://localhost:8000/ws/${username}`);
                socket.onmessage = function(event) {
                    chatbox.innerHTML += event.data + "<br>";
                    chatbox.scrollTop = chatbox.scrollHeight;
                };
            }
        }

        function sendMessage() {
            const message = document.getElementById("message").value;
            if (socket && message) {
                socket.send(message);
                document.getElementById("message").value = "";
            }
        }
    </script>
</body>
</html>
"""

# Запустите приложение с помощью uvicorn, например:
# uvicorn filename:app --host 0.0.0.0 --port 8000



# Plugins / Extensions

Você pode adicionar mais funcionalidades aos request, responde e websockets objects, para isso você pode usar `app.register(extension)` para registrar uma extension
Esteja ciente de que usar extension pode ter um pact no desempenho e usá-lo com `request_response_factory_max_items`, `websocket_factory_max_items`
ou equivalente na CLI `--req-res-factory-maxitems`, `--ws-factory-maxitems` reduzirá esse impact no desempenho

As extension devem seguir a assinatura `def extension(request, response, ws)`, request, response e ws request contêm `method` que vincula um method a uma instância, e também um
`property(name: str, default_value: any = None)` que adiciona dinamicamente uma propriedade à instância.

```python
from socketify import App, OpCode

app = App()

def extension(request, response, ws):
    @request.method
    async def get_user(self):
        token = self.get_header("token")
        return { "name": "Test" } if token else { "name", "Anonymous" }
    
    @response.method
    def msgpack(self, value: any):
        self.write_header(b'Content-Type', b'application/msgpack')
        data = msgpack.packb(value, default=encode_datetime, use_bin_type=True)
        return self.end(data)
    
    @ws.method
    def send_pm(self, to_username: str, message: str):
        user_data = self.get_user_data()
        pm_topic = f"pm-{to_username}+{user_data.username}"
        
        # Se o tópico existir, envie a mensagem
        if app.num_subscribers(pm_topic) > 0:
            # Envie mensagem privada
            return self.publish(pm_topic, message, OpCode.TEXT)
        
        # Se o tópico não existir, crie-o e sinalize o usuário
        # Subscribe a conversa
        self.subscribe(pm_topic)
        # Sinalize o usuário que você quer falar e crie uma PM room
        # Todos os usuários devem dar subscribe em signal-{username}
        self.publish(f"signal-{to_username}", { 
            "type": "pm", 
            "username": user_data.username, 
            "message": message 
        }, OpCode.TEXT)
    # Esta property pode ser usada em methods de extension e/ou middlewares
    request.property("cart", [])

# Extension devem serm registradas antes de routes
app.register(extension)
```

### Próximos [SSL](ssl.md)

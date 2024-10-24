## The App.ws route
As "routes" de WebSockets sõ registradas de forma semelhante, mas não idêntica.

Cada route do websockets tem o mesmo padrão e correspondência de padrões que para http, mas em vez de um único callback, você tem um conjunto inteiro deles, aqui está um exemplo:

Detalhes de configuração, notas:
- *idle_timeout*: número de segundos de inatividade antes que o cliente seja desconectado. Se definido como 0, nenhuma política é aplicada (as conexões podem ficar obsoletas) 
- *open*: A função callback para conexão da websocket é aberta.  
    ```python
    def on_open(ws : WebSocket): 
        """
        ws: WebSocket - websocket connection
        """
        ...
    ```
- *close*: A função callback para conexão da websocket é aberta.
    ```python
    def on_close(ws: WebSocket, code: int, msg: Union[bytes, str]): 
        """
        ws: WebSocket 
            websocket connection
        code: int 
            exit code from client
        msg: byte, str
            exit message
        """
        ...
    ```
- *upgrade*: A função callback atualiza detalhes de conexão da socket. 
    ```python
    def on_upgrade(res: Response, req: Request, socket_context):
        """
        res: Response
        req: Request
        """
        ...
    ```
- *message*: A função callback para mensagens recebidas da websocket.
    ```python
    def on_message(ws: WebSocket, msg: Union[bytes, str], opcode: OpCode): 
        """
        ws: WebSocket
        msg: bytes, str
        opcode: OpCode
        """
    ```
- *drain*: Em caso de backpressure, política para drenar o buffer ws.
    ```python
    def on_drain(ws: WebSocket):
        ...
    ```
```python
app = App()
app.ws(
    "/*",
    {
        "compression": CompressOptions.SHARED_COMPRESSOR,
        "max_payload_length": 16 * 1024 * 1024,
        "idle_timeout": 12,
        "open": on_open,
        "message": on_message,
        "close": on_close,
        "upgrade": on_upgrade,
        'drain': on_drain,
        "subscription": lambda ws, topic, subscriptions, subscriptions_before: print(f'subscription/unsubscription on topic {topic} {subscriptions} {subscriptions_before}'),
    },
)
```
## Use o recurso `WebSocket.get_user_data()`

Você deve usar o recurso de dados do usuário fornecido para armazenar e anexar quaisquer dados do usuário por socket. ir de dados do usuário para WebSocked é possível se você fizer seus dados do usuário manterem o WebSocket e conectar as coisas no open handler do WebSocket. Sua memória de dados do usuário é válida enquanto seu WebSocket é.

Se você quiser criar algo mais elaborado, você pode fazer com que os dados do usuário mantenham um ponteiro para algum bloco de memória alocado dinamicamente que mantém um booleano se o WebSocket ainda é válido ou não. O céu é o limite aqui.

Parar fazer isso, use a configuração callback de `upgrade` nas configurações de `app.ws`.

Example:
```python
from socketify import App, WebSocket, OpCode
app = App()

ID = 0

def on_open(ws: WebSocket):
    user_data = ws.get_user_data()
    print('ws %s connected' % user_data['user_id'])
    ws.send('Hello, world!')

def on_upgrade(res, req, socket_context):
    global ID
    ID += 1
    key = req.get_header("sec-websocket-key")
    protocol = req.get_header("sec-websocket-protocol")
    extensions = req.get_header("sec-websocket-extensions")
    user_data=dict(user_id=ID)
    res.upgrade(key, protocol, extensions, socket_context, user_data)

def on_message(ws: WebSocket, msg: str, opcode: OpCode):
    user_data = ws.get_user_data()
    print('ws %s: %s' % (user_data['user_id'], msg))

def on_close(ws, code, msg):
    user_data = ws.get_user_data()
    print('ws %s closed' % user_data['user_id'])

def on_drain(ws: WebSocket):
    user_data = ws.get_user_data()
    print('ws %s backpressure: %s' % (user_data['user_id'], ws.get_buffered_amount()))

app.ws(
    "/*",
    {
        "compression": CompressOptions.SHARED_COMPRESSOR,
        "max_payload_length": 16 * 1024 * 1024,
        "idle_timeout": 12,
        "open": on_open,
        "message": on_message,
        "close": on_close,
        "upgrade": on_upgrade,
        "drain": on_drain,
        "subscription": lambda ws, topic, subscriptions, subscriptions_before: print(f'subscription/unsubscription on topic {topic} {subscriptions} {subscriptions_before}'),
    }
)
```

## WebSockets são válidos de aberto a fechado

Todos os WebSockets fornecidos têm garantia de viver do evento aberto (onde você obteve seu WebSocket) até que o evento fechado seja chamado.
Os eventos de mensagem nunca serão emitidos fora de aberto/fechado. Chamar `ws.close` ou `ws.end` chamará imediatamente o closa handler.

## Backpressure em Websockets

Da mesma forma que para o Http, métodos como `ws.send(...)` podem causar backpressure. Certifique-se de verificar `ws.get_buffered_amount()` antes de enviar e verificar o valor de retorno de `ws.send` antes de enviar mais dados. WebSockets não têm `.onWritable`, mas em vez disso fazem uso do handler de `.drain` do websocket route handler.

Dentro do evento `.drain` você deve verificar `ws.get_buffered_amount()`, ele pode ter drenado ou aaté mesmo aumentado. Provavelmente drenado, mas não presuma que tenha sido, o evento `.drain` é apenas uma dica de que ele mudou.

## Backpressure
O envio em um WebSocket pode gerar backpressure. `ws.send` retorna uma enumeração de BACKPRESSURE, SUCCESS ou DROPPED. Quando send retorna BACKPRESSURE, significa que você deve parar de enviar dados até que o evento drain seja acionado e `ws.get_buffered_amount()` retorna uma quantidade razoável de bytes. Mas cso você tenha especificado um `max_backpressure` ao criar o `WebSocketContext`, esse limite será automaticamente imposto. Isso significa que uma tentativa de enviar uma mensagem que resultaria em muita backpressure será cancelada e o envio retornará DROPPED. Isso significa que a mensagem foi descartada e não será colocada na fila. `max_backpressure` é uma configuração essencial ao usar sub/pub como um receptor lento, caso contrário, pode acumular muita backpressure. Ao definir `max_backpressure`, a biblioteca gerenciará automaticamente e imporá uma backpressure máxima permitida por socket para você.

## Ping/pongs "heartbeats"
A biblioteca enviará pings automaticamente para os clientes de acordo com o `idle_timeout` especificado. Se definir `idle_timeout = 120 seconds`, um ping será emitido alguns segundos antes desse tempo limite, a menos que o cliente não responde a tempo, o socket será fechado à força e o close events será acionado. Ao desconectar, todos os recursos são liberados, incluindo assinaturas de tópicos e qualquer backpressure. Você pode facilmente deixar o navegador se reconectar usando 3 linhas ou mais de JavaScript, se quiser.


## Configurações
A compression (permessage-deflate) tem três modos principais; `CompressOptions.DISABLED`, `CompressOptions.SHARED_COMPRESSOR` e qualquer um dos `CompressOptions.DEDICATED_COMPRESSOR_xKB`. As opções desabilitadas e compartilhadas não requerem memória, enquanto o compressor dedicado requer a quantidade de memória que você selecionou. Por exemplo, `CompressOptions.DEDICATED_COMPRESSOR_4KB` adiciona uma sobrecarga de 4 KB por WebSockets, equanto`uCompressOptions.DEDICATED_COMPRESSOR_256KB` adiciona - você adivinhou - 256 KB!

Compressing usando shared significa que cada mensagem WebSocket é um fluxo de compression isolado, não tem uma janela de compression deslizante, mantida entre várias chamadas de envio como as variantes dedicadas. 

Você provavelmente quer um compression compartilhado se estiver lidando com mensagens JSON maiores, ou um compression dedicado de 4kb se estiver lidando com mensagem binárias, você provavelmente quer desabilitá-lo completamente.

idle_timeout é aproximadamente a qunatidade de segundos que pode passar entre as mensagens. Ficar ocioso por mais do que isso, e a conexão ativa. O servidor enviará pings automaticamente caso seja necessário.

### Próximo [Plugins / Extensions](extensions.md)
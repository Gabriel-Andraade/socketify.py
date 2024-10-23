## Corking

É muito importante entender o mecanismo de corking, pois ele é responsável por formatar, empacotar e enviar dados de forma eficiente. Corking é empacotar muitos envios em um único bloco syscall/SSL, sem corking seu aplicativo ainda funcionará de forma confiável, mas podendo ter um desempenho muito ruim e usar rede excessiva. Em alguns casos, o desempenho pode ser terrível sem o corking adequado.

É por isso que seus sockets serão corked por padrão na maioria dos casos simples, incluindo todos os exemplos fornecidos. No entanto, há casos em que o corking padrão não pode acontecer automaticamente.

Sempre que sua lógica de negócios registrada(seus callbacks) for chamada da biblioteca, como ao receber uma mensagem ou quando um socket for aberto, você verá corked por padrão. O que quer você faça com o socket dentro desse retorno de chamada será eficiente e propriamente corked.

Se você tiver retornos de chamada registrados em alguma outra library, digamos libhiredis, esses callbacks não serão chamados com sockets corked  (como poderíamos saber quando cork o socket se não controlamos a library de terceiros!!?).

Apenas um único socket pode ser corked em qualquer ponto no tempo (isolado por thread, é claro). É eficiente cork-and-uncork. 

Sempre que seu callback for uma corrotina, como async/await, o corking automático só pode acontecer na primeira parte da corrotina (considere await um separador que essencialmente corta a corrotina em segmentos menores). Apenas o primeiro "segmento" da corrotina será chamado de socketify, os seguintes segmentos async serão chamados pelo loop de eventos asyncio em um ponto posterior no tempo e, portanto, não estarão sob nosso controle com o corking padrão habilitado, o Object `HttpRequest` sendo alocado na pilha e válido apenas em uma única invocação de callbacks, portanto, válido apenas no primeiro "segmento" antes do primeiro await.
Se você quiser apenas preservar seu headers, url, method, cookies e query string `req.preserve()` para copiar todos os dados e mantê-los no request object, mas haverá alguma perda de desempenho.
 
O Corking é importante mesmo para chamadas que parecem ser "atomic" e enviam apenas um pedaço. `res.end`, `res.try_end`, `res.write_status`, `res.write_header` provavelmente enviarão vários pedaços de dados e são muitos importantes para o corking corretamente.

Você pode certificar-se de que o corking esteja habilidado, mesmo para casos em que o corking padrão estaria habilitado, envolvendo qualquer chamada de função de envio em um lambda ou função como esta:
```python
async def home(res, req):
    auth = req.get_header("authorization")
    user = await do_auth(auth)
    
    res.cork(lambda res: res.end(f"Hello {user.name}"))
```

```python
async def home(res, req):
    auth = req.get_header("authorization")
    user = await do_auth(auth)

    def on_cork(res):
        res.write_header("session_id", user.session_id)
        res.end(f"Hello {user.name}")
    
    res.cork(on_cork)
```
> Você não pode usar async dentro do cork, mas pode usar o cork somente quando precisar enviar a resposta depois que todo o async acontecer

Para sua conveniência, temos `res.cork_end()`, `ws.cork_send()` que fará o cork e chamará o end para você, e também `res.render()` que responde usando sempre o `res.cork_end()` para enviar seu HTML/data

### Next [Routes](routes.md)
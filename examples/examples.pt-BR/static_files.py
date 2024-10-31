# Temos uma versão disso usando aiofile e aiofiles
# Esta é uma versão de sync sem nehuma dependência, normalmente é muito rápido em CPython e PyPy3
# Em produção, recomendado fortemente usar CDN como CloudFlare ou e/ NGINX ou similar para arquivos estáticos (em qualquer linguagem/framework)

# Alguns dados da minha máquina rodando (Debian 12/testing, i7-7700HQ, 32GB RAM, Samsung 970 PRO NVME)
# Usando oha -c 400 -z 5s http://localhost:3000/

# nginx     - try_files                 -  77630.15 req/s
# pypy3     - socketify static          -  16797.30 req/s
# python3   - socketify static          -  10140.19 req/s
# node.js   - @fastify/static           -   5437.16 req/s
# node.js   - express.static            -   4077.49 req/s
# python3   - socketify static_aiofile  -   2390.96 req/s
# python3   - socketify static_aiofiles -   1615.12 req/s
# python3   - scarlette static uvicorn  -   1335.56 req/s
# python3   - fastapi static gunicorn   -   1296.14 req/s
# pypy3     - socketify static_aiofile  -    639.70 req/s
# pypy3     - socketify static_aiofiles -    637.55 req/s
# pypy3     - fastapi static gunicorn   -    253.31 req/s
# pypy3     - scarlette static uvicorn  -    279.45 req/s

# Conclusão:
# Com PyPy3 somente estático é realmente utilizável gunicorn/uvicorn, aiofiles e aiofile são realmente lentos no PyPy3 talvez isso mude com HPy
# Python3 com qualquer opção será mais rápido que gunicorn/uvicorn mas com PyPy3 com estático obtivemos 4x (ou quase isso no caso de fastify) desempenho do node.js
# Mas mesmo PyPy3 + socketify estático é 5x mais lento que NGINX

# De qualquer forma, realmente recomendamos usar NGINX ou similar + CDN para produção como todo mundo
# Recomendações de produto Gunicorn: https://docs.gunicorn.org/en/latest/deploy.html#deploying-gunicorn
# Recomendações de produto Express: https://expressjs.com/en/advanced/best-practice-performance.html
# Recomendações de produto Fastify: https://www.fastify.io/docs/latest/Guides/Recommendations/

from socketify import App, sendfile


app = App()


# Enviar home
async def home(res, req):
    # Envia o arquivo inteiro com 304 e suporte a intervalo de bytes
    await sendfile(res, req, "./public/index.html")


app.get("/", home)

# Serve todos os arquivos na pasta pública sob /*rota (você pode usar qualquer rota como/assets)
app.static("/", "./public")

app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % config.port),
)
app.run()

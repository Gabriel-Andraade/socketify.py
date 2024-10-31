from socketify import App
import redis
import aiohttp
import asyncio
from helpers.twolevel_cache import TwoLevelCache # Importe dois níveis de caches

# Criar enquete redis + conexões
redis_pool = redis.ConnectionPool(host="localhost", port=6379, db=0)
redis_connection = redis.Redis(connection_pool=redis_pool)
# CACHE DE 2 NÍVEIS (Redis para compartilhar entre os trabalhadores, Memória para ser muito mais rápida)
# Cache na memória é de 30s, cache no redis é de 60s de duração
cache = TwoLevelCache(redis_connection, 30, 60)

###
# Model
###

    # Função async para buscar dados de um Pokémon específico usando PokeAPI
async def get_pokemon(number):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://pokeapi.co/api/v2/pokemon/{number}"
        ) as response:
            pokemon = await response.text() # Resposta com texto
            # Cache só funciona com strings/bytes
            # Não mudaremos nada aqui, então não precisa analisar o json
            return pokemon.encode("utf-8")

    # Função async para buscar uma lista de 151 Pokémon originais
async def get_original_pokemons():
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://pokeapi.co/api/v2/pokemon?limit=151"
        ) as response:
            # Cache só funciona com string/bytes 
            # Aqui não muda nada, não precisa analisar
            pokemons = await response.text()
            return pokemons.encode("utf-8") # Convert text in bytes for cache 


###
# Routes
###

    # função para listar Pokémon originais com cache
def list_original_pokemons(res, req):

    # Verifique o cache para a resposta mais rápida
    value = cache.get("original_pokemons") # Verificar cache para todos
    if value != None:
        return res.end(value) # Responder com cache disponível

    # Aqui obtém async do modelo
    async def get_originals():
        value = await cache.run_once("original_pokemons", 5, get_original_pokemons)
        res.cork_end(value) # Enviar resposta com dados

    res.run_async(get_originals())  # Função de execução async

    # Função de buscar e listar Pokémon específico por números com cache
def list_pokemon(res, req):

    # Obter parâmetros necessários
    try:
        number = int(req.get_parameter(0))
    except:
        # Número inválido
        return req.set_yield(1)

    # Verifica o cache para desempenhar uma resposta rápida
    cache_key = f"pokemon-{number}" # Crie uma chave de cache específica para um Pokémon 
    value = cache.get(cache_key) # Verifica um cache
    if value != None:
        return res.end(value) # Responde com cache se estiver disponível

    # Função async para dados de pesquisa de un Pokémon se não tiver no cache
    async def find_pokemon(number, res):
        # Sincronize(sync) com o bloqueio do redis para executar apenas uma vez
        # Se mais de 1 worker/request tentar fazer esta solicitação, apenas um chamará o modelo e os outros obterão do cache
        value = await cache.run_once(cache_key, 5, get_pokemon, number)
        res.cork_end(value) # Envia uma resposta com dados

    res.run_async(find_pokemon(number, res)) # execute a função async


###
# Aqui eu decidi usar sync primeiro e async somente se for necessário, mas você pode usar async diretamente veja ./aync.py
###
app = App()
app.get("/", list_original_pokemons) # Rota para uma lista de 151 pokémon original 
app.get("/:number", list_pokemon) # Rota dinâmica para pesquisar Pokémon específico
app.any("/*", lambda res, _: res.write_status(404).end("Not Found"))
app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % config.port),
)
app.run()

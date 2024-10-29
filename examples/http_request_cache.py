from socketify import App
import redis
import aiohttp
import asyncio
from helpers.twolevel_cache import TwoLevelCache # Import two level of caches

# create redis poll + connections
redis_pool = redis.ConnectionPool(host="localhost", port=6379, db=0)
redis_connection = redis.Redis(connection_pool=redis_pool)
# 2 LEVEL CACHE (Redis to share among workers, Memory to be much faster)
# cache in memory is 30s, cache in redis is 60s duration
cache = TwoLevelCache(redis_connection, 30, 60)

###
# Model
###

    # Function async to fetch data from a specific Pokémon using PokeAPI
async def get_pokemon(number):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://pokeapi.co/api/v2/pokemon/{number}"
        ) as response:
            pokemon = await response.text() # Response with text 
            # cache only works with strings/bytes
            # we will not change nothing here so no needs to parse json
            return pokemon.encode("utf-8")

    # Function async for fetch one list for 151 pokémon originals
async def get_original_pokemons():
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://pokeapi.co/api/v2/pokemon?limit=151"
        ) as response:
            # cache only works with strings/bytes
            # we will not change nothing here so no needs to parse json
            pokemons = await response.text()
            return pokemons.encode("utf-8") # Convert text in bytes for cache 


###
# Routes
###

    # function for list original pokemon with cache
def list_original_pokemons(res, req):

    # check cache for faster response
    value = cache.get("original_pokemons") # Verify cache for datas 
    if value != None:
        return res.end(value) # Respond with available cache

    # get asynchronous from Model
    async def get_originals():
        value = await cache.run_once("original_pokemons", 5, get_original_pokemons)
        res.cork_end(value) # Send answer with datas

    res.run_async(get_originals())  # execution function async

    # Function search and list specific pokemon by number with cache
def list_pokemon(res, req):

    # get needed parameters
    try:
        number = int(req.get_parameter(0))
    except:
        # invalid number
        return req.set_yield(1)

    # check cache for faster response
    cache_key = f"pokemon-{number}" # create a key of specific cache for a pokemon 
    value = cache.get(cache_key) # Verify a cache
    if value != None:
        return res.end(value) # respond with cache if available

    # Function async for search datas of a pokemon if not have in cache
    async def find_pokemon(number, res):
        # sync with redis lock to run only once
        # if more than 1 worker/request try to do this request, only one will call the Model and the others will get from cache
        value = await cache.run_once(cache_key, 5, get_pokemon, number)
        res.cork_end(value) # send a response with datas

    res.run_async(find_pokemon(number, res)) # execute function async


###
# Here i decided to use an sync first and async only if needs, but you can use async directly see ./async.py
###
app = App()
app.get("/", list_original_pokemons) # Route for a list of 151 pokemon original 
app.get("/:number", list_pokemon)
app.any("/*", lambda res, _: res.write_status(404).end("Not Found"))
app.listen(
    3000,
    lambda config: print("Listening on port http://localhost:%d now\n" % config.port),
)
app.run()

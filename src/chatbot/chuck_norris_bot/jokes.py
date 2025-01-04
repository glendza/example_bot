import aiohttp


async def get_chuck_norris_joke() -> str:
    """
    Get a Chuck Norris joke from the API.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.chucknorris.io/jokes/random") as response:
            data = await response.json()
            return data["value"]

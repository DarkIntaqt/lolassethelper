import os
import time
import aiohttp

import asyncio
from .challengesPerRegion import getChallengePerRegion
from ..helper.createFolder import createFolder

regions = [
    "br1",
    "euw1",
    "eun1",
    "jp1",
    "kr",
    "la1",
    "la2",
    "na1",
    "oc1",
    "ru",
    "tr1",
    "ph2",
    "sg2",
    "th2",
    "tw2",
    "vn2",
]


async def main():
    # Check if the output folder exists
    createFolder("output/challenges")

    tasks = []
    data = {}
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/challenges.json"
        ) as response:

            if response.status != 200:
                return 404

            data = await response.json()

        for region in regions:
            tasks.append(
                asyncio.create_task(getChallengePerRegion(region, data, session))
            )

        result = await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())

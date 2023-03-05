import os
import asyncio
import json
from ..helper.createFolder import createFolder
from .getChallenge import getChallenge


try:
    from .. import config
except ImportError:
    # Check if the config exists
    print(
        "ERROR: lolassethelper/config.py doesn't exist or is missing the variable apiKey"
    )
    print(
        "How to fix this issue: https://github.com/DarkIntaqt/lolassethelper/blob/master/SETUP.md"
    )
    exit()


async def getChallengePerRegion(region, data, session):

    challenges = {}
    titles = []

    # Parse Titles
    for id, title in data["titles"].items():
        id = str(title["itemId"])
        challengeId = 0
        challengeTier = 0

        # Check for apprentice title
        if len(id) > 3:
            challengeId = int(id[0 : (len(id) - 2)])
            challengeTier = int(id[(len(id) - 2) : len(id)])

        titles.append(
            {
                "title": title["name"],
                "titleId": int(id),
                "challengeId": challengeId,
                "challengeTier": challengeTier,
            }
        )

    # A list of challenges provided by the Riot API
    challengeList = []
    challengePercentiles = []

    async with session.get(
        f"https://{region}.api.riotgames.com/lol/challenges/v1/challenges/config?api_key={config.apiKey}"
    ) as response:
        if response.status == 200:
            challengeList = await response.json()
        else:
            print(
                f"WARN: Riot API challenge returned an error {response.status}; The script will continue but the data could be falsified"
            )

    async with session.get(
        f"https://{region}.api.riotgames.com/lol/challenges/v1/challenges/percentiles?api_key={config.apiKey}"
    ) as response:
        if response.status == 200:
            challengePercentiles = await response.json()
        else:
            print(
                f"WARN: Riot API challenge percentiles returned an error {response.status}; The script will continue but the data could be falsified"
            )

    # Parse Challenges
    for challengeId, challenge in data["challenges"].items():
        challenges[challengeId] = await getChallenge(
            challengeId=int(challengeId),
            challenge=challenge,
            session=session,
            region=region,
            challengeList=challengeList,
            challengePercentiles=challengePercentiles,
        )

    createFolder(f"output/{region}")
    with open(f"output/{region}/challenges.json", "w+") as file:
        file.write(json.dumps({"challenges": challenges, "titles": titles}))

    print(f"Challenges: {region} finished. ")

    return True

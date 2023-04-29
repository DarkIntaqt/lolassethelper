import os
import asyncio
import json
from ..helper.createFolder import createFolder
from ..helper.rateLimitRequest import rateLimitRequest
from .getChallenge import getChallenge
from .getTitles import getTitles


try:
    from ..config import (
        apiKey,
        translateChallenges,
        dynamicThresholds,
        rateLimitThreshold,
    )
except ImportError:
    # Check if the config exists
    print("ERROR: lolassethelper/config.py doesn't exist")
    print(
        "How to fix this issue: https://github.com/DarkIntaqt/lolassethelper/blob/master/SETUP.md"
    )
    exit()


async def getChallengesPerRegion(region, data, session):
    challenges = {}
    titles = await getTitles(data["titles"])

    # A list of challenges provided by the Riot API
    challengeList = []
    challengePercentiles = []

    # Fetch the list of challenges
    challengeListResponse = await rateLimitRequest(
        url=f"https://{region}.api.riotgames.com/lol/challenges/v1/challenges/config?api_key={apiKey}",
        region=region,
        session=session,
        sleepThreshold=rateLimitThreshold,
    )
    if challengeListResponse != None:
        challengeList = challengeListResponse

    # Fetch the list of percentiles
    challengePercentilesResponse = await rateLimitRequest(
        url=f"https://{region}.api.riotgames.com/lol/challenges/v1/challenges/config?api_key={apiKey}",
        region=region,
        session=session,
        sleepThreshold=0.8,
    )
    if challengePercentilesResponse != None:
        challengePercentiles = challengePercentilesResponse

    # Parse Challenges
    for challengeId, challenge in data["challenges"].items():
        challenges[challengeId] = await getChallenge(
            challengeId=int(challengeId),
            challenge=challenge,
            session=session,
            region=region,
            challengeList=challengeList,
            challengePercentiles=challengePercentiles,
            dynamicThresholds=dynamicThresholds,
            apiKey=apiKey,
            requestThreshold=rateLimitThreshold,
        )

    createFolder(f"output/challenges/{region}")
    with open(f"output/challenges/{region}/raw.json", "w+") as file:
        file.write(json.dumps({"challenges": challenges, "titles": titles}))

    if translateChallenges == False:
        print(f"Challenges: {region} finished without translation. ")
        return True

    # Translate challenges
    if len(challengeList) > 0:
        for lang, value in challengeList[0]["localizedNames"].items():
            translation = data

            # en_US is loaded by default
            if "en_US" != lang:
                async with session.get(
                    f"https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/{lang.lower()}/v1/challenges.json"
                ) as response:
                    if response.status == 200:
                        translation = await response.json()
                    else:
                        print(
                            f"WARN: CDragon challenge translation returned an error {response.status} for {lang}; The script will continue but the data could be falsified"
                        )
            translatedChallenge = challenges

            # Loop through the challenge list and change the translatable parts
            for challenge in challengeList:
                translatedChallenge[str(challenge["id"])]["name"] = translation[
                    "challenges"
                ][str(challenge["id"])]["name"]
                translatedChallenge[str(challenge["id"])]["description"] = translation[
                    "challenges"
                ][str(challenge["id"])]["description"]
                translatedChallenge[str(challenge["id"])][
                    "descriptionShort"
                ] = translation["challenges"][str(challenge["id"])]["descriptionShort"]

            # Translate the titles
            translatedTitles = await getTitles(translation["titles"])

            with open(f"output/challenges/{region}/{lang}.json", "w+") as file:
                file.write(
                    json.dumps(
                        {"challenges": translatedChallenge, "titles": translatedTitles}
                    )
                )

    print(f"Challenges: {region} finished. ")

    return True

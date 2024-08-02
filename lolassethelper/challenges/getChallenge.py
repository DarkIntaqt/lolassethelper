import re
from .retiredChallenges import retiredChallenges
from ..helper.rateLimitRequest import rateLimitRequest


def removeTags(raw):
    return re.compile(r"<[^>]+>").sub("", raw)


async def getChallenge(
    challengeId,
    challenge,
    session,
    region,
    challengeList,
    challengePercentiles,
    apiKey,
    dynamicThresholds=False,
    requestThreshold=0.8,
):
    # Check if the current challenge exists in the live api
    riotProvidedChallengeData = {}
    riotProvidedChallengePercentiles = {}
    for tempChallenge in challengeList:
        if tempChallenge["id"] == challengeId:
            riotProvidedChallengeData = tempChallenge
            break

    # Check the tags if the challenge is a capstone
    isCapstone = False
    if "isCapstone" in challenge["tags"] and challenge["tags"]["isCapstone"] == "Y":
        isCapstone = True

    # Check the tags if the challenge has a parent
    parent = 0
    if "parent" in challenge["tags"]:
        parent = int(challenge["tags"]["parent"])

    # If the challenge does not exist, set state to disabled
    state = "DISABLED"
    percentiles = {}
    thresholds = {}

    # This code blocks only executes if the challenge is ENABLED
    if len(riotProvidedChallengeData.items()) > 0:
        state = riotProvidedChallengeData["state"]
        if str(challengeId) in challengePercentiles:
            riotProvidedChallengePercentiles = challengePercentiles[str(challengeId)]

        # Set thresholds to the ones given by the Riot Games API
        thresholds = riotProvidedChallengeData["thresholds"]

    # Set percentiles to the ones given by the Riot Games API
    percentiles = riotProvidedChallengePercentiles

    isReversed = challenge["reverseDirection"]
    hasLeaderboard = challenge["leaderboard"]
    # If the state is disabled, force hasLeaderboard to False
    if state == "DISABLED":
        hasLeaderboard = False

    # Set queueId
    queueIds = challenge["queueIds"]

    # Set imageId
    imageId = challengeId
    if len(challenge["levelToIconPath"]) > 0:
        link = challenge["levelToIconPath"][
            list(challenge["levelToIconPath"].keys())[0]
        ]

        s = link.split("/")
        if len(s) == 9:
            if s[6].isnumeric() and int(s[6]) != challengeId:
                imageId = int(s[6])

    # set state to RETIRED if challenge is withing "reitred_challenges"
    if challengeId in retiredChallenges:
        state = "RETIRED"

    # Dynamic Thresholds
    if dynamicThresholds == True and challenge["leaderboard"] == True:
        challengeGrandmasterThreshold = await rateLimitRequest(
            url=f"https://{region}.api.riotgames.com/lol/challenges/v1/challenges/{challengeId}/leaderboards/by-level/MASTER?limit=1&api_key={apiKey}",
            region=region,
            session=session,
            sleepThreshold=requestThreshold,
        )
        challengeChallengerThreshold = await rateLimitRequest(
            url=f"https://{region}.api.riotgames.com/lol/challenges/v1/challenges/{challengeId}/leaderboards/by-level/GRANDMASTER?limit=1&api_key={apiKey}",
            region=region,
            session=session,
            sleepThreshold=requestThreshold,
        )

        if (
            challengeGrandmasterThreshold != None
            and len(challengeGrandmasterThreshold) > 0
        ):
            thresholds["GRANDMASTER"] = challengeGrandmasterThreshold[0]["value"]

        if (
            challengeChallengerThreshold != None
            and len(challengeChallengerThreshold) > 0
        ):
            thresholds["CHALLENGER"] = challengeChallengerThreshold[0]["value"]

        print(f"Thresholds loaded for {challengeId}#{region}")

    return {
        "id": challengeId,
        "imageId": imageId,
        "state": state,
        "name": removeTags(challenge["name"]),
        "description": removeTags(challenge["description"]),
        "descriptionShort": removeTags(challenge["descriptionShort"]),
        "source": challenge["source"],
        "queueIds": queueIds,
        "parent": parent,
        "capstone": isCapstone,
        "reversed": isReversed,
        "leaderboard": hasLeaderboard,
        "thresholds": thresholds,
        "percentiles": percentiles,
    }

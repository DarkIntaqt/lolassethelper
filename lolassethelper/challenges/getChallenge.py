import re
from .retiredChallenges import retiredChallenges


def removeTags(raw):
    return re.compile(r"<[^>]+>").sub("", raw)


async def getChallenge(
    challengeId, challenge, session, region, challengeList, challengePercentiles
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

    # set state to RETIRED if challenge is withing "reitred_challenges"
    if challengeId in retiredChallenges:
        state = "RETIRED"

    return {
        "id": challengeId,
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

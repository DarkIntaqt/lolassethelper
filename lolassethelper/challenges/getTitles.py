async def getTitles(titles):
    response = []

    # Parse Titles
    for id, title in titles.items():
        id = str(title["itemId"])
        challengeId = 0
        challengeTier = 0

        # Check for Apprentice title
        if len(id) > 3:
            challengeId = int(id[0 : (len(id) - 2)])
            challengeTier = int(id[(len(id) - 2) : len(id)])

        response.append(
            {
                "title": title["name"],
                "titleId": int(id),
                "challengeId": challengeId,
                "challengeTier": challengeTier,
            }
        )

    return response

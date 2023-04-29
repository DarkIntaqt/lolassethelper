import asyncio

ratelimits = {}


async def rateLimitRequest(url, region, session, sleepThreshold=0.8, retry=True):
    # Empower the request first

    if region not in ratelimits:
        ratelimits[region] = [[0, 20, 1], [0, 100, 120]]

    await rateLimitRegion(region, sleepThreshold)

    async with session.get(url) as response:
        if response.status == 200:
            setRateLimitHeader(headers=response.headers, region=region)
            return await response.json()
        # Return None if the request was not successful
        print(
            f"WARN: Riot API challenge returned an error {response.status}; The script will continue but the data could be falsified"
        )

        if response.status == 429:
            await asyncio.sleep(int(response.headers["Retry-After"]))
            if retry == True:
                print("Retry")
                return await rateLimitRequest(
                    url=url,
                    region=region,
                    session=session,
                    sleepThreshold=sleepThreshold,
                    retry=False,
                )

        return None


async def rateLimitRegion(region, sleepThreshold):
    limits = ratelimits[region]

    quickRate = limits[0][0] / limits[0][1]
    longRate = limits[1][0] / limits[1][1]

    if quickRate > sleepThreshold:
        await asyncio.sleep(limits[0][2] * (1 - quickRate))

    if longRate > sleepThreshold:
        await asyncio.sleep(limits[1][2] * (1 - longRate))


def setRateLimitHeader(headers, region):
    riotRateLimitsCount = headers["X-App-Rate-Limit-Count"].split(",")
    riotRateLimitsLimit = headers["X-App-Rate-Limit"].split(",")

    ratelimits[region] = [
        [
            int(riotRateLimitsCount[0].split(":")[0]),
            int(riotRateLimitsLimit[0].split(":")[0]),
            int(riotRateLimitsCount[0].split(":")[1]),
        ],
        [
            int(riotRateLimitsCount[1].split(":")[0]),
            int(riotRateLimitsLimit[1].split(":")[0]),
            int(riotRateLimitsCount[1].split(":")[1]),
        ],
    ]

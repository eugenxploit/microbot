# SPDX-License-Identifier: GPL-2.0-or-later

from random import choice

from aiohttp import ClientSession

from ubot.micro_bot import micro_bot

ldr = micro_bot.loader

GEL_URL = "https://gelbooru.com/index.php"


@ldr.add(pattern="gel(s|x|q|)(f|)")
async def gelbooru(event):
    await event.edit(f"`Processing…`")

    if "x" in event.pattern_match.group(0):
        rating = "Rating:explicit"
    elif "s" in event.pattern_match.group(0):
        rating = "Rating:safe"
    elif "q" in event.pattern_match.group(0):
        rating = "Rating:questionable"
    else:
        rating = ""

    if event.pattern_match.group(2):
        as_file = True
    else:
        as_file = False

    search_query = event.pattern_match.group(3)

    params = {"page": "dapi",
              "s": "post",
              "q": "index",
              "json": 1,
              "tags": f"{rating} {search_query}".strip()}

    session = ClientSession()

    async with session.get(GEL_URL, params=params) as response:
        if response.status == 200:
            response = await response.json()
        else:
            await event.edit(f"`An error occurred, response code: `**{response.status}**")
            return

    await session.close()

    if not response:
        await event.edit(f"`No results for query: `**{search_query}**")
        return

    response = choice(response)

    valid_urls = []

    for url in ['file_url', 'large_file_url', 'source']:
        if url in response.keys():
            valid_urls.append(response[url])

    if not valid_urls:
        await event.edit(f"`Failed to find URLs for query: `**{search_query}**")
        return

    for image_url in valid_urls:
        try:
            await event.client.send_file(event.chat_id, file=image_url, force_document=as_file)
            await event.delete()
            return
        except:
            pass

    await event.edit(f"`Failed to fetch media for query: `**{search_query}**")

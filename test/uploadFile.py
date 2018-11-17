import aiohttp
import asyncio
url = 'http://ddayzzz.wang:9998'

async def uploadFile():

        files = {
            'image1.jpg': open('test/image1.jpg', 'rb'),
            'image2.jpg': open('test/image2.jpg', 'rb'),
            'large.jpg': open('test/large.jpg', 'rb')
        }
        async with session.post(url + '/api/v1/upload', data=files) as resp:
            print(resp.status)
            print(await resp.text())

async def test_create_post():
    async with aiohttp.ClientSession() as session:
        async with session.post(url + '/api/v1/upload', data={'imageId': '1541057264966ac8fb873465848f1b90ea9afec874d85000.jpg',
                                                              }) as resp:
            print(resp.status)
            print(await resp.text())
loop = asyncio.get_event_loop()
loop.run_until_complete(uploadFile())
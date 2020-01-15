import aiohttp
import asyncio
import pandas
import time
import json
from flask import Flask, request
from bs4 import BeautifulSoup

headers = {
    'user-agent':
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
}
url = "https://feebee.com.tw/channel/home"


class makeProp():
    def __init__(self, name, img, minPrice, maxPrice):
        self.name = name
        self.img = img
        self.minPrice = minPrice
        self.maxPrice = maxPrice


class Utility():
    def __init__(self, item):
        self.item = item

    def selNameImg(item):
        sel = "div#home_" + item + " > ul > li > a.link_ghost > img"
        return sel

    def selPrice(item):
        sel = "div#home_" + item + " > ul > li > span > meta"
        return sel


app = Flask(__name__)


def _parse_results(url, html):
    # print(url)

    try:
        soup = BeautifulSoup(html, 'html.parser')
        selNameImgStr1 = soup.select(Utility.selNameImg("視聽家電"))
        selNameImgStr2 = soup.select(Utility.selNameImg("生活家電"))
        selNameImgStr3 = soup.select(Utility.selNameImg("廚房家電"))
        selNameImgStr4 = soup.select(Utility.selNameImg("健康-美容家電"))
        selNameImgStr5 = soup.select(Utility.selNameImg("按摩家電"))

        selPriceStr1 = soup.select(Utility.selPrice("視聽家電"))
        selPriceStr2 = soup.select(Utility.selPrice("生活家電"))
        selPriceStr3 = soup.select(Utility.selPrice("廚房家電"))
        selPriceStr4 = soup.select(Utility.selPrice("健康-美容家電"))
        selPriceStr5 = soup.select(Utility.selPrice("按摩家電"))

        video = makeProp(list(), list(), list(), list())
        life = makeProp(list(), list(), list(), list())
        kitchen = makeProp(list(), list(), list(), list())
        health = makeProp(list(), list(), list(), list())
        massage = makeProp(list(), list(), list(), list())

        # print(selNameImgStr4)
        # print(len(selName))
        for i in range(len(selNameImgStr1)):
            # video
            video.name.append(selNameImgStr1[i].get('alt'))
            video.img.append(selNameImgStr1[i].get('src'))
            # life
            life.name.append(selNameImgStr2[i].get('alt'))
            life.img.append(selNameImgStr2[i].get('src'))
            # kitchen
            kitchen.name.append(selNameImgStr3[i].get('alt'))
            kitchen.img.append(selNameImgStr3[i].get('src'))
            # health
            health.name.append(selNameImgStr4[i].get('alt'))
            health.img.append(selNameImgStr4[i].get('src'))
            # massage
            massage.name.append(selNameImgStr5[i].get('alt'))
            massage.img.append(selNameImgStr5[i].get('src'))

        for i in range(len(selPriceStr1)):
            # minprice
            if(i % 3 == 1):
                video.minPrice.append(selPriceStr1[i].get('content'))
                life.minPrice.append(selPriceStr2[i].get('content'))
                kitchen.minPrice.append(selPriceStr3[i].get('content'))
                health.minPrice.append(selPriceStr4[i].get('content'))
                massage.minPrice.append(selPriceStr5[i].get('content'))
            # maxprice
            if(i % 3 == 2):
                video.maxPrice.append(selPriceStr1[i].get('content'))
                life.maxPrice.append(selPriceStr2[i].get('content'))
                kitchen.maxPrice.append(selPriceStr3[i].get('content'))
                health.maxPrice.append(selPriceStr4[i].get('content'))
                massage.maxPrice.append(selPriceStr5[i].get('content'))

        videoTable = pandas.DataFrame(
            {"Name": video.name, "Img": video.img, "Min": video.minPrice, "Max": video.maxPrice})
        lifeTable = pandas.DataFrame(
            {"Name":  life.name, "Img":  life.img, "Min":  life.minPrice, "Max":  life.maxPrice})
        kitchenTable = pandas.DataFrame(
            {"Name": kitchen.name, "Img": kitchen.img, "Min": kitchen.minPrice, "Max": kitchen.maxPrice})
        healthTable = pandas.DataFrame(
            {"Name": health.name, "Img": health.img, "Min": health.minPrice, "Max": health.maxPrice})
        massageTable = pandas.DataFrame(
            {"Name": massage.name, "Img": massage.img, "Min": massage.minPrice, "Max": massage.maxPrice})

        videoOutput = json.loads(videoTable.to_json(
            orient='records', force_ascii=False))
        lifeOutput = json.loads(lifeTable.to_json(
            orient='records', force_ascii=False))
        kitchenOutput = json.loads(kitchenTable.to_json(
            orient='records', force_ascii=False))
        healthOutput = json.loads(healthTable.to_json(
            orient='records', force_ascii=False))
        massageOutput = json.loads(massageTable.to_json(
            orient='records', force_ascii=False))
        output = {'video': videoOutput, 'life': lifeOutput,
                  'kitchen': kitchenOutput, 'health': healthOutput, 'message': massageOutput}
        return output
    except Exception as e:
        raise e


async def fetch(session, url, headers):
    # url = url + ss
    async with session.get(url, headers=headers, timeout=10) as response:
        return await response.text()


async def main():
    async with aiohttp.ClientSession() as client:
        html = await fetch(client, url, headers=headers)
        try:
            output = _parse_results(url, html)
            return output
        except Exception as e:
            raise e

loop = asyncio.get_event_loop()


@app.route('/', methods=['POST'])
def gogo():
    # request.get_json()
    output = loop.run_until_complete(main())
    return output


@app.route('/', methods=['GET'])
def getDisplay():
    return "Please use post method to get home items"


if __name__ == '__main__':
    app.run()

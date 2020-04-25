from functools import lru_cache

import requests
import aiohttp
import asyncio
from async_lru import alru_cache
from injector import inject

from backend.utils.http import fetch_async, fetch

GOOGLE_API_KEY = "AIzaSyAPGGYxsJfpi3DY0o11lAR4-Gccfpf3juw"
YANDEX_API_KEY = "9dc2f628-77ef-4202-ad14-913e947114f4"


class GeocoderService:

    @inject
    def __init__(self):
        pass

    @lru_cache(maxsize=32)
    def from_google_sync(self, locality):
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={locality}&key={GOOGLE_API_KEY}"
        json = fetch(url)
        lon, lat = None, None
        country = ""
        try:
            country = \
            list(filter(lambda d: "country" in d.get("types", ""), json["results"][0]["address_components"]))[0][
                "long_name"]
            location = json["results"][0]["geometry"]["location"]
            lon, lat = float(location["lng"]), float(location["lat"])
        except:
            pass
        return dict(lon=lon, lat=lat, country=country)

    @alru_cache(maxsize=32)
    async def from_google(self, locality):
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={locality}&key={GOOGLE_API_KEY}"
        async with aiohttp.ClientSession() as session:
            json = await fetch_async(session, url)
            lon, lat = None, None
            country = ""
            try:
                country = \
                    list(filter(lambda d: "country" in d.get("types", ""), json["results"][0]["address_components"]))[
                        0][
                        "long_name"]
                location = json["results"][0]["geometry"]["location"]
                lon, lat = float(location["lng"]), float(location["lat"])
            except:
                pass
            return dict(lon=lon, lat=lat, country=country)

    @alru_cache(maxsize=32)
    async def from_yandex(self, locality, results=1):
        url = f"https://geocode-maps.yandex.ru/1.x/?apikey={YANDEX_API_KEY}&format=json&geocode={locality}&results={results}"
        async with aiohttp.ClientSession() as session:
            json = await fetch_async(session, url)
            lon, lat = None, None
            try:
                response = json["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"]
                response = response.split()
                lon, lat = float(response[0]), float(response[1])
            except:
                pass
            return lon, lat

import json
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


NULL_DATETIME = datetime.fromtimestamp(0)


class ApiError(Exception):
    pass


class GW2API:
    URL_BASE = "https://api.guildwars2.com/v2/"
    DISK_CACHE_PATH = Path("~/.cache/gw2_api/").expanduser()
    CACHE: Dict[str, Tuple[Any, datetime]] = {}

    def __init__(self, api_key: Optional[str] = None):
        self.api_headers = {}
        self.api_key = api_key
        self.DISK_CACHE_PATH.mkdir(parents=True, exist_ok=True)

    @property
    def api_key(self) -> Optional[str]:
        return self._api_key

    @api_key.setter
    def api_key(self, value: Optional[str]):
        self._api_key = value
        if value is not None:
            self.api_headers["Authorization"] = "Bearer " + value

    def disk_cache_lookup(self, endpoint: str) -> Tuple[Any, datetime]:
        disk_path = self.DISK_CACHE_PATH / endpoint.replace('/', '.')
        try:
            result, expiration = json.loads(disk_path.read_text())
            expiration = datetime.fromtimestamp(expiration)
            return result, expiration
        except:
            return {}, NULL_DATETIME

    def disk_cache_store(self, endpoint: str, result: Any, expiration: datetime) -> None:
        disk_path = self.DISK_CACHE_PATH / endpoint.replace('/', '.')
        try:
            disk_path.write_text(json.dumps([result, expiration.timestamp()]))
        except:
            pass

    def get(self, endpoint: str, cache_seconds: int = 60*60*24, *, auth_required=False) -> Any:
        if auth_required and self.api_key is None:
            raise ApiError("an api key is required for this function")

        now = datetime.now()

        # Try to get the result from the RAM cache
        if endpoint in self.CACHE:
            result, expiration = self.CACHE[endpoint]
        # Try to get the result from the disk cache
        else:
            result, expiration = self.disk_cache_lookup(endpoint)
            self.CACHE[endpoint] = result, expiration

        # If the acquired result is still valid, return it
        if now < expiration:
            return result

        # Get a new result from the api and set the expiration
        result = requests.get(self.URL_BASE + endpoint, headers=self.api_headers).json()
        expiration = now + timedelta(seconds=cache_seconds)
        self.CACHE[endpoint] = (result, expiration)
        self.disk_cache_store(endpoint, result, expiration)
        return result

    def colors(self):
        return self.get("colors")

    def color(self, color_id: int):
        return self.get("colors/{}".format(color_id))

    def continents(self):
        return self.get("continents")

    def continent(self, continent_id: int):
        return self.get("continents/{}".format(continent_id))

    def floors(self, continent_id: int):
        return self.get("continents/{}/floors".format(continent_id))

    def floor(self, continent_id: int, floor_id: int):
        return self.get("continents/{}/floors/{}".format(continent_id, floor_id))

    def regions(self, continent_id: int, floor_id: int):
        return self.get("continents/{}/floors/{}/regions".format(continent_id, floor_id))

    def region(self, continent_id: int, floor_id: int, region_id: int):
        return self.get("continents/{}/floors/{}/regions/{}".format(continent_id, floor_id, region_id))

    def region_maps(self, continent_id: int, floor_id: int, region_id: int):
        return self.get("continents/{}/floors/{}/regions/{}/maps".format(continent_id, floor_id, region_id))

    def maps(self):
        return self.get("maps")

    def map(self, map_id: int):
        return self.get("maps/{}".format(map_id))

    def map_verbose(self, map_id: int, floor_id: Optional[int] = None):
        map_data = self.map(map_id)
        continent_id = map_data['continent_id']
        if floor_id is None:
            floor_id = map_data['default_floor']
        region_id = map_data['region_id']

        map_data.update(self.get("continents/{}/floors/{}/regions/{}/maps/{}".format(continent_id, floor_id, region_id, map_id)))
        return map_data

    def map_sectors(self, map_id: int, floor_id: Optional[int] = None):
        map_data = self.map(map_id)
        continent_id = map_data['continent_id']
        if floor_id is None:
            floor_id = map_data['default_floor']
        region_id = map_data['region_id']

        return self.get("continents/{}/floors/{}/regions/{}/maps/{}/sectors".format(continent_id, floor_id, region_id, map_id))

    def map_sector(self, map_id: int, sector_id: int, floor_id: Optional[int] = None):
        map_data = self.map(map_id)
        continent_id = map_data['continent_id']
        if floor_id is None:
            floor_id = map_data['default_floor']
        region_id = map_data['region_id']

        return self.get("continents/{}/floors/{}/regions/{}/maps/{}/sectors/{}".format(continent_id, floor_id, region_id, map_id, sector_id))

    def map_pois(self, map_id: int, floor_id: Optional[int] = None):
        map_data = self.map(map_id)
        continent_id = map_data['continent_id']
        if floor_id is None:
            floor_id = map_data['default_floor']
        region_id = map_data['region_id']

        return self.get("continents/{}/floors/{}/regions/{}/maps/{}/pois".format(continent_id, floor_id, region_id, map_id))

    def map_poi(self, map_id: int, poi_id: int, floor_id: Optional[int] = None):
        map_data = self.map(map_id)
        continent_id = map_data['continent_id']
        if floor_id is None:
            floor_id = map_data['default_floor']
        region_id = map_data['region_id']

        return self.get("continents/{}/floors/{}/regions/{}/maps/{}/pois/{}".format(continent_id, floor_id, region_id, map_id, poi_id))

    def map_tasks(self, map_id: int, floor_id: Optional[int] = None):
        map_data = self.map(map_id)
        continent_id = map_data['continent_id']
        if floor_id is None:
            floor_id = map_data['default_floor']
        region_id = map_data['region_id']

        return self.get("continents/{}/floors/{}/regions/{}/maps/{}/tasks".format(continent_id, floor_id, region_id, map_id))

    def map_task(self, map_id: int, task_id: int, floor_id: Optional[int] = None):
        map_data = self.map(map_id)
        continent_id = map_data['continent_id']
        if floor_id is None:
            floor_id = map_data['default_floor']
        region_id = map_data['region_id']

        return self.get("continents/{}/floors/{}/regions/{}/maps/{}/tasks/{}".format(continent_id, floor_id, region_id, map_id, task_id))

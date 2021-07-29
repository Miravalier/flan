import json
import os
import struct
import numpy as np
from enum import Enum, Flag
from dataclasses import dataclass

MUMBLE_LINK_FILE = "/tmp/gw2_mumble_link"


class Mount(Enum):
    NONE = 0
    JACKAL = 1
    GRIFFON = 2
    SPRINGER = 3
    SKIMMER = 4
    RAPTOR = 5
    ROLLER_BEETLE = 6
    WARCLAW = 7
    SKYSCALE = 8


class Profession(Enum):
    UNKNOWN = 0
    GUARDIAN = 1
    WARRIOR = 2
    ENGINEER = 3
    RANGER = 4
    THIEF = 5
    ELEMENTALIST = 6
    MESMER = 7
    NECROMANCER = 8
    REVENANT = 9


class Race(Enum):
    ASURA = 0
    CHARR = 1
    HUMAN = 2
    NORN = 3
    SYLVARI = 4


class UISize(Enum):
    SMALL = 0
    NORMAL = 1
    LARGE = 2
    LARGER = 3


class UIState(Flag):
    MAP_OPEN = 1
    COMPASS_TOP_RIGHT = 2
    COMPASS_ROTATION_ENABLED = 4
    GAME_FOCUS = 8
    COMPETITIVE_MODE = 16
    TEXTBOX_FOCUS = 32
    IN_COMBAT = 64


@dataclass
class Identity:
    name: str
    profession: Profession
    specialization: int
    race: Race
    map_id: int
    world_id: int
    team_color_id: int
    commander: bool
    fov: float
    ui_size: UISize


class MumbleLink:
    PROPERTIES = (
        'ui_version', 'ui_tick', 'avatar_position', 'avatar_front',
        'avatar_top', 'name', 'camera_position', 'camera_front',
        'camera_top', 'identity', 'map_id', 'map_type',
        'shard_id', 'instance', 'build_id', 'ui_state',
        'compass_width', 'compass_height', 'compass_rotation', 'player_x',
        'player_y', 'map_center_x', 'map_center_y', 'map_scale',
        'process_id', 'mount'
    )

    def __init__(self):
        self.fd = os.open(MUMBLE_LINK_FILE, os.O_RDONLY)
        self.buffer = bytearray(4096)
        self.update()

    def close(self):
        os.close(self.fd)

    def update(self):
        os.lseek(self.fd, 0, os.SEEK_SET)
        os.readv(self.fd, [self.buffer])

    def parse(self, fmt: str, offset: int):
        return struct.unpack_from(fmt, self.buffer, offset)[0]

    def unpack(self, fmt: str, offset: int):
        return struct.unpack_from(fmt, self.buffer, offset)

    def __str__(self):
        return "MumbleLink{{{}}}".format(", ".join(
            "{}: {}".format(k, repr(getattr(self, k))) for k in MumbleLink.PROPERTIES
        ))

    @property
    def ui_version(self):
        return self.parse("I", 0)

    @property
    def ui_tick(self):
        return self.parse("I", 4)

    @property
    def avatar_position(self):
        return np.array(self.unpack("3f", 8))

    @property
    def avatar_front(self):
        return np.array(self.unpack("3f", 20))

    @property
    def avatar_top(self):
        return np.array(self.unpack("3f", 32))

    @property
    def name(self):
        return self.parse("512s", 44).decode('utf-16').split('\0')[0]

    @property
    def camera_position(self):
        return np.array(self.unpack("3f", 556))

    @property
    def camera_front(self):
        return np.array(self.unpack("3f", 568))

    @property
    def camera_top(self):
        return np.array(self.unpack("3f", 580))

    @property
    def identity_raw(self):
        json_string = self.parse("512s", 592).decode('utf-16').split('\0')[0]
        if json_string:
            try:
                return json.loads(json_string)
            except json.JSONDecodeError:
                return {}
        else:
            return {}

    @property
    def identity(self):
        r = self.identity_raw
        return Identity(
            r.get("name", ""),
            Profession(r.get("profession", 0)),
            r.get("spec", 0),
            Race(r.get("race", 0)),
            r.get("map_id", 0),
            r.get("world_id", 0),
            r.get("team_color_id", 0),
            r.get("commander", False),
            r.get("fov", 0.0),
            UISize(r.get("uisz", 0))
        )

    @property
    def map_id(self):
        return self.parse("I", 1136)

    @property
    def map_type(self):
        return self.parse("I", 1140)

    @property
    def shard_id(self):
        return self.parse("I", 1144)

    @property
    def instance(self):
        return self.parse("I", 1148)

    @property
    def build_id(self):
        return self.parse("I", 1152)

    @property
    def ui_state(self):
        return UIState(self.parse("I", 1156))

    @property
    def compass_width(self):
        """
        @return Compass width in pixels
        """
        return self.parse("H", 1160)

    @property
    def compass_height(self):
        """
        @return Compass height in pixels
        """
        return self.parse("H", 1162)

    @property
    def compass_rotation(self):
        """
        @return Compass rotation in radians
        """
        return self.parse("f", 1164)

    @property
    def player_x(self):
        """
        @return Player x coordinate in continentCoords
        """
        return self.parse("f", 1168)

    @property
    def player_y(self):
        """
        @return Player y coordinate in continentCoords
        """
        return self.parse("f", 1172)

    @property
    def map_center_x(self):
        """
        @return Map center x coordinate in continentCoords
        """
        return self.parse("f", 1176)

    @property
    def map_center_y(self):
        """
        @return Map center x coordinate in continentCoords
        """
        return self.parse("f", 1180)

    @property
    def map_scale(self):
        return self.parse("f", 1184)

    @property
    def process_id(self):
        return self.parse("I", 1188)

    @property
    def mount_index(self):
        return self.parse("B", 1192)

    @property
    def mount(self):
        return Mount(self.mount_index)

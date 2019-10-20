"""小米空气净化器组件"""
import logging

from homeassistant.helpers.entity import Entity
from ..mi_air_purifier import DOMAIN

_LOGGER = logging.getLogger(__name__)


def setup_platform(hass, config, add_devices, discovery_info=None):
    """初始化小米空气净化器"""
    if discovery_info is None:
        logging.info("没有空气净化器需要发现")
        return
    devices = []
    logging.debug("准备添加设备")
    for host, device in hass.data[DOMAIN].items():
        logging.info("添加设备[%s]", device)
        devices.append(MiAirPurifierEntity(device, DOMAIN, DOMAIN))
    add_devices(devices)


class MiAirPurifierEntity(Entity):
    """小米空气净化器实体"""

    def __init__(self, air_purifier, name, unique_id):
        """初始化小米空气净化器"""
        self._air_purifier = air_purifier
        self._name = name
        self._unique_id = unique_id

    @property
    def name(self):
        """Return the default name of the binary sensor."""
        return self._name

    @property
    def unique_id(self):
        """Return an unique identifier for this entity."""
        return self._unique_id

    @property
    def state(self) -> str:
        return self._air_purifier.status().power

    @property
    def should_poll(self):
        """Return False because entity pushes its state to HA."""
        return False

"""小米净水器组件传感器，净水器无法控制所以只有传感器"""
import logging

from homeassistant.helpers.entity import Entity
from ..mi_water_purifier import SENSOR_TYPES

_LOGGER = logging.getLogger(__name__)

COOKER_DOMAIN = 'mi_water_purifier'

def setup_platform(hass, config, add_devices, discovery_info=None):
    """初始化小米厨下净水器传感器"""

    if discovery_info is None:
        return

    sensors = []

    for host, device in hass.data[COOKER_DOMAIN].items():
        for sensor_type in SENSOR_TYPES.values():
            sensors.append(MiWaterPurifierSensor(device, sensor_type))

    add_devices(sensors)


class MiWaterPurifierSensor(Entity):
    """小米厨下净水器传感器类"""

    def __init__(self, device, config):
        """初始化传感器"""
        self._state = None
        self._data = None
        self._water_purifier = device
        self._name = config[1]
        self._data_key = config[2]
        self._icon = config[3]
        self._unit = config[4]
        self.parse_data()

    @property
    def name(self):
        """返回传感器名称"""
        return self._water_purifier.name + '_' + self._name

    @property
    def icon(self):
        """返回传感器对应图标"""
        return 'mdi:' + self._icon

    @property
    def state(self):
        """返回传感器状态"""
        return self._state

    @property
    def unit_of_measurement(self):
        """返回传感器测量单位"""
        return self._unit

    @property
    def device_state_attributes(self):
        """返回传感器属性"""
        attrs = {}
        return attrs

    def parse_data(self):
        if self._water_purifier._data:
            self._data = self._water_purifier._data
            self._state = self._data[self._data_key]

    def update(self):
        """更新数据"""
        self.parse_data()

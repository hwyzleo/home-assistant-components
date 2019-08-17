"""小米扫地机器人组件传感器"""
import logging

from homeassistant.helpers.entity import Entity
from ..mi_vacuum_cleaner import DOMAIN

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES = {
    'battery': ['status().battery', 'battery', '%', None],
    'count': ['clean_history().count', 'robot-vacuum', None, None],
    'total_duration': ['clean_history().total_duration', 'clock-outline', 'H', 'hours'],
    'total_area': ['clean_history().total_area', 'floor-plan', 'M²', 'meter'],
    'main_brush': ['consumable_status().main_brush', 'clock-outline', 'H', 'hours'],
    'main_brush_left': ['consumable_status().main_brush_left', 'clock-outline', 'H', 'hours'],
    'side_brush': ['consumable_status().side_brush', 'clock-outline', 'H', 'hours'],
    'side_brush_left': ['consumable_status().side_brush_left', 'clock-outline', 'H', 'hours'],
    'filter': ['consumable_status().filter', 'clock-outline', 'H', 'hours'],
    'filter_left': ['consumable_status().filter_left', 'clock-outline', 'H', 'hours'],
    'sensor_dirty': ['consumable_status().sensor_dirty', 'clock-outline', 'H', 'hours'],
    'sensor_dirty_left': ['consumable_status().sensor_dirty_left', 'clock-outline', 'H', 'hours'],
}


def setup_platform(hass, config, add_devices, discovery_info=None):
    """初始化小米扫地机器人传感器"""

    if discovery_info is None:
        _LOGGER.info("没有传感器需要被发现")
        return

    sensors = []
    _LOGGER.info("准备添加传感器")
    for host, device in hass.data[DOMAIN].items():
        for key in SENSOR_TYPES.keys():
            _LOGGER.debug("添加传感器[%s]", key)
            sensors.append(MiVacuumCleanerSensor(device, SENSOR_TYPES[key]))

    add_devices(sensors)


class MiVacuumCleanerSensor(Entity):
    """小米扫地机器人传感器类"""

    def __init__(self, device, config):
        """初始化传感器"""
        self._state = None
        self._data = None
        self._device = device
        self._name = config[0]
        self._icon = config[1]
        self._unit = config[2]
        self._handle = config[3]
        self.parse_data()

    @property
    def name(self):
        """返回传感器名称"""
        return 'mi_vacuum_cleaner_' + self._name

    @property
    def icon(self):
        """返回传感器对应图标"""
        if self._icon is None:
            return None
        else:
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
        try:
            self._state = eval("self._device." + self._name)
            if self._handle is not None:
                if self._handle == 'hours':
                    self._state = self._state.days * 24 + int(self._state.seconds / 3600)
                if self._handle == 'meter':
                    self._state = int(self._state)
        except Exception as e:
            _LOGGER.warning("获取扫地机传感器[%s]异常[%s]", self._name, e)

    def update(self):
        """更新数据"""
        self.parse_data()

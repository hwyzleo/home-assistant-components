"""小米厨下净水器组件，净水器无法控制所以只有传感器"""
import math
import logging

from homeassistant.const import (CONF_NAME, CONF_HOST, CONF_TOKEN, )
from homeassistant.helpers.entity import Entity
from homeassistant.exceptions import PlatformNotReady
from miio import Device, DeviceException

_LOGGER = logging.getLogger(__name__)

REQUIREMENTS = ['python-miio>=0.3.1']

"""自来水水质"""
TAP_WATER_QUALITY = {'name': 'tap_water_quality', 'key': 'ttds'}
"""过滤后水质"""
FILTERED_WATER_QUALITY = {'name': 'filtered_water_quality', 'key': 'ftds'}
"""PP棉滤芯已净水量"""
PP_COTTON_FILTER_PURIFIED_LITERS = {'name': 'pp_cotton_filter_purified_liters', 'key': 'pfpl'}
"""PP棉滤芯已净水小时数"""
PP_COTTON_FILTER_PURIFIED_HOURS = {'name': 'pp_cotton_filter_purified_hours', 'key': 'pfph'}
"""前置活性炭滤芯已净水量"""
FRONT_ACTIVE_CARBON_FILTER_PURIFIED_LITERS = {'name': 'front_active_carbon_filter_purified_liters', 'key': 'fcfpl'}
"""前置活性炭滤芯已净水小时数"""
FRONT_ACTIVE_CARBON_FILTER_PURIFIED_HOURS = {'name': 'front_active_carbon_filter_purified_hours', 'key': 'fcfph'}
"""RO反渗透滤芯已净水量"""
RO_FILTER_PURIFIED_LITERS = {'name': 'ro_filter_purified_liters', 'key': 'rofpl'}
"""RO反渗透滤芯已净水小时数"""
RO_FILTER_PURIFIED_HOURS = {'name': 'ro_filter_purified_hours', 'key': 'rofph'}
"""后置活性炭滤芯已净水量"""
REAR_ACTIVE_CARBON_FILTER_PURIFIED_LITERS = {'name': 'rear_active_carbon_filter_purified_liters', 'key': 'rcfpl'}
"""后置活性炭滤芯已净水小时数"""
REAR_ACTIVE_CARBON_FILTER_PURIFIED_HOURS = {'name': 'rear_active_carbon_filter_purified_hours', 'key': 'rcfph'}
"""PP棉滤芯总净水量"""
PP_COTTON_FILTER_TOTAL_LITERS = {'name': 'pp_cotton_filter_total_liters', 'key': 'pftl'}
"""PP棉滤芯总小时数"""
PP_COTTON_FILTER_TOTAL_HOURS = {'name': 'pp_cotton_filter_total_hours', 'key': 'pfth'}
"""前置活性炭滤芯总净水量"""
FRONT_ACTIVE_CARBON_FILTER_TOTAL_LITERS = {'name': 'front_active_carbon_filter_total_liters', 'key': 'fcftl'}
"""前置活性炭滤芯总小时数"""
FRONT_ACTIVE_CARBON_FILTER_TOTAL_HOURS = {'name': 'front_active_carbon_filter_total_hours', 'key': 'fcfth'}
"""RO反渗透滤芯总净水量"""
RO_FILTER_TOTAL_LITERS = {'name': 'ro_filter_total_liters', 'key': 'roftl'}
"""RO反渗透滤芯总小时数"""
RO_FILTER_TOTAL_HOURS = {'name': 'ro_filter_total_hours', 'key': 'rofth'}
"""后置活性炭滤芯总净水量"""
REAR_ACTIVE_CARBON_FILTER_TOTAL_LITERS = {'name': 'rear_active_carbon_filter_total_liters', 'key': 'rcftl'}
"""后置活性炭滤芯总小时数"""
REAR_ACTIVE_CARBON_FILTER_TOTAL_HOURS = {'name': 'rear_active_carbon_filter_total_hours', 'key': 'rcfth'}
"""PP棉滤芯剩余天数"""
PP_COTTON_FILTER_REMAINING_DAYS = {'name': 'pp_cotton_filter_remaining_days', 'key': 'pfrd'}
"""PP棉滤芯剩余百分比"""
PP_COTTON_FILTER_REMAINING_PERCENT = {'name': 'pp_cotton_filter_remaining_percent', 'key': 'pfrp'}
"""前置活性炭滤芯剩余天数"""
FRONT_ACTIVE_CARBON_FILTER_REMAINING_DAYS = {'name': 'front_active_carbon_filter_remaining_days', 'key': 'fcfrd'}
"""前置活性炭滤芯剩余百分比"""
FRONT_ACTIVE_CARBON_FILTER_REMAINING_PERCENT = {'name': 'front_active_carbon_filter_remaining_percent', 'key': 'fcfrp'}
"""RO反渗透滤芯剩余天数"""
RO_FILTER_REMAINING_DAYS = {'name': 'ro_filter_remaining_days', 'key': 'rofrd'}
"""RO反渗透滤芯剩余百分比"""
RO_FILTER_REMAINING_PERCENT = {'name': 'ro_filter_remaining_percent', 'key': 'rofrp'}
"""后置活性炭滤芯剩余天数"""
REAR_ACTIVE_CARBON_FILTER_REMAINING_DAYS = {'name': 'rear_active_carbon_filter_remaining_days', 'key': 'rcfrd'}
"""后置活性炭滤芯剩余百分比"""
REAR_ACTIVE_CARBON_FILTER_REMAINING_PERCENT = {'name': 'rear_active_carbon_filter_remaining_percent', 'key': 'rcfrp'}

def setup_platform(hass, config, add_devices, discovery_info=None):
    """初始化小米厨下净水器组件"""

    host = config.get(CONF_HOST)
    name = config.get(CONF_NAME)
    token = config.get(CONF_TOKEN)

    _LOGGER.info("初始化小米厨下净水器组件，净水器IP[%s]Token[%s...]", host, token[:5])

    devices = []
    try:
        device = Device(host, token)
        waterPurifier = MiKitchenWaterPurifier(device, name)
        devices.append(MiKitchenWaterPurifierSensor(waterPurifier, TAP_WATER_QUALITY))
        devices.append(MiKitchenWaterPurifierSensor(waterPurifier, FILTERED_WATER_QUALITY))
        devices.append(MiKitchenWaterPurifierSensor(waterPurifier, PP_COTTON_FILTER_PURIFIED_LITERS))
        devices.append(MiKitchenWaterPurifierSensor(waterPurifier, PP_COTTON_FILTER_PURIFIED_HOURS))
        devices.append(MiKitchenWaterPurifierSensor(waterPurifier, PP_COTTON_FILTER_REMAINING_DAYS))
        devices.append(MiKitchenWaterPurifierSensor(waterPurifier, PP_COTTON_FILTER_REMAINING_PERCENT))
        devices.append(MiKitchenWaterPurifierSensor(waterPurifier, PP_COTTON_FILTER_TOTAL_LITERS))
        devices.append(MiKitchenWaterPurifierSensor(waterPurifier, PP_COTTON_FILTER_TOTAL_HOURS))
        devices.append(MiKitchenWaterPurifierSensor(waterPurifier, FRONT_ACTIVE_CARBON_FILTER_PURIFIED_LITERS))
        devices.append(MiKitchenWaterPurifierSensor(waterPurifier, FRONT_ACTIVE_CARBON_FILTER_PURIFIED_HOURS))
        devices.append(MiKitchenWaterPurifierSensor(waterPurifier, FRONT_ACTIVE_CARBON_FILTER_REMAINING_DAYS))
        devices.append(MiKitchenWaterPurifierSensor(waterPurifier, FRONT_ACTIVE_CARBON_FILTER_REMAINING_PERCENT))
        devices.append(MiKitchenWaterPurifierSensor(waterPurifier, FRONT_ACTIVE_CARBON_FILTER_TOTAL_LITERS))
        devices.append(MiKitchenWaterPurifierSensor(waterPurifier, FRONT_ACTIVE_CARBON_FILTER_TOTAL_HOURS))
        devices.append(MiKitchenWaterPurifierSensor(waterPurifier, RO_FILTER_PURIFIED_LITERS))
        devices.append(MiKitchenWaterPurifierSensor(waterPurifier, RO_FILTER_PURIFIED_HOURS))
        devices.append(MiKitchenWaterPurifierSensor(waterPurifier, RO_FILTER_REMAINING_DAYS))
        devices.append(MiKitchenWaterPurifierSensor(waterPurifier, RO_FILTER_REMAINING_PERCENT))
        devices.append(MiKitchenWaterPurifierSensor(waterPurifier, RO_FILTER_TOTAL_LITERS))
        devices.append(MiKitchenWaterPurifierSensor(waterPurifier, RO_FILTER_TOTAL_HOURS))
        devices.append(MiKitchenWaterPurifierSensor(waterPurifier, REAR_ACTIVE_CARBON_FILTER_PURIFIED_LITERS))
        devices.append(MiKitchenWaterPurifierSensor(waterPurifier, REAR_ACTIVE_CARBON_FILTER_PURIFIED_HOURS))
        devices.append(MiKitchenWaterPurifierSensor(waterPurifier, REAR_ACTIVE_CARBON_FILTER_REMAINING_DAYS))
        devices.append(MiKitchenWaterPurifierSensor(waterPurifier, REAR_ACTIVE_CARBON_FILTER_REMAINING_PERCENT))
        devices.append(MiKitchenWaterPurifierSensor(waterPurifier, REAR_ACTIVE_CARBON_FILTER_TOTAL_LITERS))
        devices.append(MiKitchenWaterPurifierSensor(waterPurifier, REAR_ACTIVE_CARBON_FILTER_TOTAL_HOURS))
    except DeviceException:
        _LOGGER.exception('初始化小米厨下净水器组件失败')
        raise PlatformNotReady

    add_devices(devices)

class MiKitchenWaterPurifierSensor(Entity):
    """小米厨下净水器传感器类"""

    def __init__(self, waterPurifier, data_key):
        """初始化传感器"""
        self._state = None
        self._data = None
        self._waterPurifier = waterPurifier
        self._data_key = data_key
        self.parse_data()

    @property
    def name(self):
        """返回传感器名称"""
        return self._waterPurifier.name + '_' + self._data_key['name']

    @property
    def icon(self):
        """返回传感器对应图标"""
        if self._data_key['key'] is TAP_WATER_QUALITY['key'] or \
            self._data_key['key'] is FILTERED_WATER_QUALITY['key']:
            return 'mdi:water'
        else:
            return 'mdi:filter-outline'

    @property
    def state(self):
        """返回传感器状态"""
        return self._state

    @property
    def unit_of_measurement(self):
        """返回传感器测量单位"""
        if self._data_key['key'] is TAP_WATER_QUALITY['key'] or \
            self._data_key['key'] is FILTERED_WATER_QUALITY['key']:
            return 'TDS'
        if self._data_key['key'] is PP_COTTON_FILTER_REMAINING_DAYS['key'] or \
            self._data_key['key'] is FRONT_ACTIVE_CARBON_FILTER_REMAINING_DAYS['key'] or \
            self._data_key['key'] is RO_FILTER_REMAINING_DAYS['key'] or \
            self._data_key['key'] is REAR_ACTIVE_CARBON_FILTER_REMAINING_DAYS['key']:
            return '天'
        if self._data_key['key'] is PP_COTTON_FILTER_TOTAL_LITERS['key'] or \
            self._data_key['key'] is FRONT_ACTIVE_CARBON_FILTER_TOTAL_LITERS['key'] or \
            self._data_key['key'] is RO_FILTER_TOTAL_LITERS['key'] or \
            self._data_key['key'] is REAR_ACTIVE_CARBON_FILTER_TOTAL_LITERS['key'] or \
            self._data_key['key'] is PP_COTTON_FILTER_PURIFIED_LITERS['key'] or \
            self._data_key['key'] is FRONT_ACTIVE_CARBON_FILTER_PURIFIED_LITERS['key'] or \
            self._data_key['key'] is RO_FILTER_PURIFIED_LITERS['key'] or \
            self._data_key['key'] is REAR_ACTIVE_CARBON_FILTER_PURIFIED_LITERS['key']:
            return '升'
        if self._data_key['key'] is PP_COTTON_FILTER_TOTAL_HOURS['key'] or \
            self._data_key['key'] is FRONT_ACTIVE_CARBON_FILTER_TOTAL_HOURS['key'] or \
            self._data_key['key'] is RO_FILTER_TOTAL_HOURS['key'] or \
            self._data_key['key'] is REAR_ACTIVE_CARBON_FILTER_TOTAL_HOURS['key'] or \
            self._data_key['key'] is PP_COTTON_FILTER_PURIFIED_HOURS['key'] or \
            self._data_key['key'] is FRONT_ACTIVE_CARBON_FILTER_PURIFIED_HOURS['key'] or \
            self._data_key['key'] is RO_FILTER_PURIFIED_HOURS['key'] or \
            self._data_key['key'] is REAR_ACTIVE_CARBON_FILTER_PURIFIED_HOURS['key']:
            return '小时'
        return '%'

    @property
    def device_state_attributes(self):
        """返回传感器属性"""
        attrs = {}
        return attrs

    def parse_data(self):
        if self._waterPurifier._data:
            self._data = self._waterPurifier._data
            self._state = self._data[self._data_key['key']]

    def update(self):
        """更新数据"""
        self.parse_data()

class MiKitchenWaterPurifier(Entity):
    """小米厨下净水器类"""

    def __init__(self, device, name):
        """初始化小米厨下净水器"""
        self._state = None
        self._device = device
        self._name = name
        self.parse_data()

    @property
    def name(self):
        """返回名称"""
        return self._name

    @property
    def icon(self):
        """返回图标"""
        return 'mdi:water'

    @property
    def unit_of_measurement(self):
        """返回测量单位"""
        return 'TDS'

    @property
    def state(self):
        """返回状态"""
        return self._state

    @property
    def hidden(self) -> bool:
        """如果需要隐藏实体则返回 True"""
        return True

    @property
    def device_state_attributes(self):
        """返回属性"""
        attrs = {}
        return attrs

    def parse_data(self):
        """解析数据"""
        try:
            data = {}
            status = self._device.send('get_prop', [])
            data[TAP_WATER_QUALITY['key']] = status[0]
            data[FILTERED_WATER_QUALITY['key']] = status[1]
            data[PP_COTTON_FILTER_PURIFIED_LITERS['key']] = status[2]
            data[PP_COTTON_FILTER_PURIFIED_HOURS['key']] = status[3]
            data[FRONT_ACTIVE_CARBON_FILTER_PURIFIED_LITERS['key']] = status[4]
            data[FRONT_ACTIVE_CARBON_FILTER_PURIFIED_HOURS['key']] = status[5]
            data[RO_FILTER_PURIFIED_LITERS['key']] = status[6]
            data[RO_FILTER_PURIFIED_HOURS['key']] = status[7]
            data[REAR_ACTIVE_CARBON_FILTER_PURIFIED_LITERS['key']] = status[8]
            data[REAR_ACTIVE_CARBON_FILTER_PURIFIED_HOURS['key']] = status[9]
            data[PP_COTTON_FILTER_TOTAL_LITERS['key']] = status[10]
            data[PP_COTTON_FILTER_TOTAL_HOURS['key']] = status[11]
            data[FRONT_ACTIVE_CARBON_FILTER_TOTAL_LITERS['key']] = status[12]
            data[FRONT_ACTIVE_CARBON_FILTER_TOTAL_HOURS['key']] = status[13]
            data[RO_FILTER_TOTAL_LITERS['key']] = status[14]
            data[RO_FILTER_TOTAL_HOURS['key']] = status[15]
            data[REAR_ACTIVE_CARBON_FILTER_TOTAL_LITERS['key']] = status[16]
            data[REAR_ACTIVE_CARBON_FILTER_TOTAL_HOURS['key']] = status[17]
            data[PP_COTTON_FILTER_REMAINING_DAYS['key']] = int((data[PP_COTTON_FILTER_TOTAL_HOURS['key']] - data[PP_COTTON_FILTER_PURIFIED_HOURS['key']]) / 24)
            data[PP_COTTON_FILTER_REMAINING_PERCENT['key']] = math.floor(data[PP_COTTON_FILTER_REMAINING_DAYS['key']] * 24 * 100 / data[PP_COTTON_FILTER_TOTAL_HOURS['key']])
            data[FRONT_ACTIVE_CARBON_FILTER_REMAINING_DAYS['key']] = int((data[FRONT_ACTIVE_CARBON_FILTER_TOTAL_HOURS['key']] - data[FRONT_ACTIVE_CARBON_FILTER_PURIFIED_HOURS['key']]) / 24)
            data[FRONT_ACTIVE_CARBON_FILTER_REMAINING_PERCENT['key']] = math.floor(data[FRONT_ACTIVE_CARBON_FILTER_REMAINING_DAYS['key']] * 24 * 100 / data[FRONT_ACTIVE_CARBON_FILTER_TOTAL_HOURS['key']])
            data[RO_FILTER_REMAINING_DAYS['key']] = int((data[RO_FILTER_TOTAL_HOURS['key']] - data[RO_FILTER_PURIFIED_HOURS['key']]) / 24)
            data[RO_FILTER_REMAINING_PERCENT['key']] = math.floor(data[RO_FILTER_REMAINING_DAYS['key']] * 24 * 100 / data[RO_FILTER_TOTAL_HOURS['key']])
            data[REAR_ACTIVE_CARBON_FILTER_REMAINING_DAYS['key']] = rcfd = int((data[REAR_ACTIVE_CARBON_FILTER_TOTAL_HOURS['key']] - data[REAR_ACTIVE_CARBON_FILTER_PURIFIED_HOURS['key']]) / 24)
            data[REAR_ACTIVE_CARBON_FILTER_REMAINING_PERCENT['key']] = math.floor(data[REAR_ACTIVE_CARBON_FILTER_REMAINING_DAYS['key']] * 24 * 100 / data[REAR_ACTIVE_CARBON_FILTER_TOTAL_HOURS['key']])

            self._data = data
            self._state = self._data[FILTERED_WATER_QUALITY['key']]
        except DeviceException:
            _LOGGER.exception('获取小米厨下净水器属性失败')
            self._data = None
            self._state = None
            raise PlatformNotReady

    def update(self):
        """更新数据"""
        self.parse_data()
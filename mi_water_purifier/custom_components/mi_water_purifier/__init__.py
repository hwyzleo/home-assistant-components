"""小米净水器组件初始化"""
from datetime import timedelta
import math
import logging
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from homeassistant.const import (CONF_NAME, CONF_HOST, CONF_TOKEN, CONF_SCAN_INTERVAL)
from homeassistant.exceptions import PlatformNotReady
from homeassistant.helpers.entity import Entity
from homeassistant.helpers import discovery
from homeassistant.helpers.event import track_time_interval
from homeassistant.helpers.dispatcher import dispatcher_send
from homeassistant.util.dt import utcnow
from miio import Device, DeviceException

_LOGGER = logging.getLogger(__name__)

REQUIREMENTS = ['python-miio>=0.3.1']

DEFAULT_NAME = 'mi_water_purifier'
DEFAULT_SCAN_INTERVAL = timedelta(seconds=30)

DOMAIN = 'mi_water_purifier'
CONF_MODEL = 'model'
DATA_KEY = 'mi_water_purifier_data'
DATA_STATE = 'state'

MODEL_LX2 = 'yunmi.waterpuri.lx2'
MODEL_LX3 = 'yunmi.waterpuri.lx3'  # 小米厨下净水器
MODEL_LX4 = 'yunmi.waterpuri.lx4'
MODEL_V2 = 'yunmi.waterpurifier.v2'
MODEL_V3 = 'yunmi.waterpurifier.v3'
SUPPORTED_MODELS = [
    MODEL_LX2,
    MODEL_LX3,
    MODEL_LX4,
    MODEL_V2,
    MODEL_V3,
]

TAP_WATER_QUALITY = 'ttds'  # 自来水水质
FILTERED_WATER_QUALITY = 'ftds'  # 过滤后水质
PP_CTN_FL_PURIFY_LITERS = 'pcfpl'  # PP棉滤芯已净水量
PP_CTN_FL_PURIFY_HOURS = 'pcfph'  # PP棉滤芯已净水小时数
FRONT_ACTIVE_C_FL_PURIFY_LITERS = 'fcfpl'  # 前置活性炭滤芯已净水量
FRONT_ACTIVE_C_FL_PURIFY_HOURS = 'fcfph'  # 前置活性炭滤芯已净水小时数
RO_FL_PURIFY_LITERS = 'rofpl'  # RO反渗透滤芯已净水量
RO_FL_PURIFY_HOURS = 'rofph'  # RO反渗透滤芯已净水小时数
REAR_ACTIVE_C_FL_PURIFY_LITERS = 'rcfpl'  # 后置活性炭滤芯已净水量
REAR_ACTIVE_C_FL_PURIFY_HOURS = 'rcfph'  # 后置活性炭滤芯已净水小时数
PP_CTN_FL_TTL_LITERS = 'pcftl'  # PP棉滤芯总净水量
PP_CTN_FL_TTL_HOURS = 'pcfth'  # PP棉滤芯总小时数
FRONT_ACTIVE_C_FL_TTL_LITERS = 'fcftl'  # 前置活性炭滤芯总净水量
FRONT_ACTIVE_C_FL_TTL_HOURS = 'fcfth'  # 前置活性炭滤芯总小时数
RO_FL_TTL_LITERS = 'roftl'  # RO反渗透滤芯总净水量
RO_FL_TTL_HOURS = 'rofth'  # RO反渗透滤芯总小时数
REAR_ACTIVE_C_FL_TTL_LITERS = 'rcftl'  # 后置活性炭滤芯总净水量
REAR_ACTIVE_C_FL_TTL_HOURS = 'rcfth'  # 后置活性炭滤芯总小时数
PP_CTN_FL_REMAINING_DAYS = 'pcfrd'  # PP棉滤芯剩余天数
PP_CTN_FL_REMAINING_PCT = 'pcfrp'  # PP棉滤芯剩余百分比
FRONT_ACTIVE_C_FL_REMAINING_DAYS = 'fcfrd'  # 前置活性炭滤芯剩余天数
FRONT_ACTIVE_C_FL_REMAINING_PCT = 'fcfrp'  # 前置活性炭滤芯剩余百分比
RO_FL_REMAINING_DAYS = 'rofrd'  # RO反渗透滤芯剩余天数
RO_FL_REMAINING_PCT = 'rofrp'  # RO反渗透滤芯剩余百分比
REAR_ACTIVE_C_FL_REMAINING_DAYS = 'rcfrd'  # 后置活性炭滤芯剩余天数
REAR_ACTIVE_C_FL_REMAINING_PCT = 'rcfrp'  # 后置活性炭滤芯剩余百分比

SENSOR_TYPES = {
    'tap_water_quality': [0, 'tap_water_quality', TAP_WATER_QUALITY, 'water', 'TDS'],
    'filtered_water_quality': [1, 'filtered_water_quality', FILTERED_WATER_QUALITY, 'water', 'TDS'],
    'pp_ctn_fl_purify_liters': [2, 'pp_ctn_fl_purify_liters', PP_CTN_FL_PURIFY_LITERS, 'water', 'L'],
    'pp_ctn_fl_purify_hours': [3, 'pp_ctn_fl_purify_hours', PP_CTN_FL_PURIFY_HOURS, 'clock-outline', 'H'],
    'pp_ctn_fl_remaining_days': [None, 'pp_ctn_fl_remaining_days', PP_CTN_FL_REMAINING_DAYS, 'calendar-range', 'D'],
    'pp_ctn_fl_remaining_pct': [None, 'pp_ctn_fl_remaining_pct', PP_CTN_FL_REMAINING_PCT, 'percent', '%'],
    'pp_ctn_fl_ttl_liters': [10, 'pp_ctn_fl_ttl_liters', PP_CTN_FL_TTL_LITERS, 'water', 'L'],
    'pp_ctn_fl_ttl_hours': [11, 'pp_ctn_fl_ttl_hours', PP_CTN_FL_TTL_HOURS, 'clock-outline', 'H'],
    'front_active_c_fl_purify_liters': [4, 'front_active_c_fl_purify_liters', FRONT_ACTIVE_C_FL_PURIFY_LITERS, 'water',
                                        'L'],
    'front_active_c_fl_purify_hours': [5, 'front_active_c_fl_purify_hours', FRONT_ACTIVE_C_FL_PURIFY_HOURS,
                                       'clock-outline', 'H'],
    'front_active_c_fl_remaining_days': [None, 'front_active_c_fl_remaining_days', FRONT_ACTIVE_C_FL_REMAINING_DAYS,
                                         'calendar-range', 'D'],
    'front_active_c_fl_remaining_pct': [None, 'front_active_c_fl_remaining_pct', FRONT_ACTIVE_C_FL_REMAINING_PCT,
                                        'percent', '%'],
    'front_active_c_fl_ttl_liters': [12, 'front_active_c_fl_ttl_liters', FRONT_ACTIVE_C_FL_TTL_LITERS, 'water', 'L'],
    'front_active_c_fl_ttl_hours': [13, 'front_active_c_fl_ttl_hours', FRONT_ACTIVE_C_FL_TTL_HOURS, 'clock-outline',
                                    'H'],
    'ro_fl_purify_liters': [6, 'ro_fl_purify_liters', RO_FL_PURIFY_LITERS, 'water', 'L'],
    'ro_fl_purify_hours': [7, 'ro_fl_purify_hours', RO_FL_PURIFY_HOURS, 'clock-outline', 'H'],
    'ro_fl_remaining_days': [None, 'ro_fl_remaining_days', RO_FL_REMAINING_DAYS, 'calendar-range', 'D'],
    'ro_fl_remaining_pct': [None, 'ro_fl_remaining_pct', RO_FL_REMAINING_PCT, 'percent', '%'],
    'ro_fl_ttl_liters': [14, 'ro_fl_ttl_liters', RO_FL_TTL_LITERS, 'water', 'L'],
    'ro_fl_ttl_hours': [15, 'ro_fl_ttl_hours', RO_FL_TTL_HOURS, 'clock-outline', 'H'],
    'rear_active_c_fl_purify_liters': [8, 'rear_active_c_fl_purify_liters', REAR_ACTIVE_C_FL_PURIFY_LITERS, 'water',
                                       'L'],
    'rear_active_c_fl_purify_hours': [9, 'rear_active_c_fl_purify_hours', REAR_ACTIVE_C_FL_PURIFY_HOURS,
                                      'clock-outline', 'H'],
    'rear_active_c_fl_remaining_days': [None, 'rear_active_c_fl_remaining_days', REAR_ACTIVE_C_FL_REMAINING_DAYS,
                                        'calendar-range', 'D'],
    'rear_active_c_fl_remaining_pct': [None, 'rear_active_c_fl_remaining_pct', REAR_ACTIVE_C_FL_REMAINING_PCT,
                                       'percent', '%'],
    'rear_active_c_fl_ttl_liters': [16, 'rear_active_c_fl_ttl_liters', REAR_ACTIVE_C_FL_TTL_LITERS, 'water', 'L'],
    'rear_active_c_fl_ttl_hours': [17, 'rear_active_c_fl_ttl_hours', REAR_ACTIVE_C_FL_TTL_HOURS, 'clock-outline', 'H'],
}

"""验证配置参数"""
CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_TOKEN): vol.All(cv.string, vol.Length(min=32, max=32)),
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_MODEL): vol.In(SUPPORTED_MODELS),
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): cv.time_period,
    })
}, extra=vol.ALLOW_EXTRA)


def setup(hass, config):
    """初始化小米净水器组件"""

    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    host = config[DOMAIN][CONF_HOST]
    token = config[DOMAIN][CONF_TOKEN]
    name = config[DOMAIN][CONF_NAME]
    model = config[DOMAIN].get(CONF_MODEL)
    scan_interval = config[DOMAIN][CONF_SCAN_INTERVAL]

    if DATA_KEY not in hass.data:
        hass.data[DATA_KEY] = {}
        hass.data[DATA_KEY][host] = {}

    try:
        miio_device = Device(host, token)
        device_info = miio_device.info()
        model = device_info.model
        _LOGGER.info("发现净水器设备，型号[%s]，软件版本[%s]，硬件版本[%s]",
                     model,
                     device_info.firmware_version,
                     device_info.hardware_version)
    except DeviceException:
        raise PlatformNotReady

    if model in SUPPORTED_MODELS:
        water_purifier = MiWaterPurifier(miio_device, name)
        _LOGGER.info("实例化小米净水器[%s]", name)
        hass.data[DOMAIN][host] = water_purifier
        for component in ['sensor']:
            discovery.load_platform(hass, component, DOMAIN, {}, config)
    else:
        _LOGGER.error("未支持设备型号[%s]", model)
        return False

    def update(event_time):
        """更新设备状态"""
        try:
            water_purifier.update()
            state = water_purifier.state
            hass.data[DATA_KEY][host][DATA_STATE] = state
            dispatcher_send(hass, '{}_updated'.format(DOMAIN), host)
        except DeviceException as ex:
            dispatcher_send(hass, '{}_unavailable'.format(DOMAIN), host)
            _LOGGER.error("获取净化器状态时异常[%s]", ex)

    update(utcnow())
    track_time_interval(hass, update, scan_interval)

    return True


class MiWaterPurifier(Entity):
    """小米净水器类"""

    def __init__(self, device, name):
        """初始化小米净水器"""
        self._data = None
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
            for sensor_type in SENSOR_TYPES.values():
                if sensor_type[0] is not None:
                    data[sensor_type[2]] = status[int(sensor_type[0])]

            if data[PP_CTN_FL_TTL_HOURS] - data[PP_CTN_FL_PURIFY_HOURS] <= 0:
                data[PP_CTN_FL_REMAINING_DAYS] = 0
                data[PP_CTN_FL_REMAINING_PCT] = 0
            else:
                data[PP_CTN_FL_REMAINING_DAYS] = int((data[PP_CTN_FL_TTL_HOURS] - data[PP_CTN_FL_PURIFY_HOURS]) / 24)
                data[PP_CTN_FL_REMAINING_PCT] = math.floor(
                data[PP_CTN_FL_REMAINING_DAYS] * 24 * 100 / data[PP_CTN_FL_TTL_HOURS])
            if data[FRONT_ACTIVE_C_FL_TTL_HOURS] - data[FRONT_ACTIVE_C_FL_PURIFY_HOURS] <= 0:
                data[FRONT_ACTIVE_C_FL_REMAINING_DAYS] = 0
                data[FRONT_ACTIVE_C_FL_REMAINING_PCT] = 0
            else:
                data[FRONT_ACTIVE_C_FL_REMAINING_DAYS] = int(
                (data[FRONT_ACTIVE_C_FL_TTL_HOURS] - data[FRONT_ACTIVE_C_FL_PURIFY_HOURS]) / 24)
                data[FRONT_ACTIVE_C_FL_REMAINING_PCT] = math.floor(
                data[FRONT_ACTIVE_C_FL_REMAINING_DAYS] * 24 * 100 / data[FRONT_ACTIVE_C_FL_TTL_HOURS])
            if data[RO_FL_TTL_HOURS] - data[RO_FL_PURIFY_HOURS] <= 0:
                data[RO_FL_REMAINING_DAYS] = 0
                data[RO_FL_REMAINING_PCT] = 0
            else:
                data[RO_FL_REMAINING_DAYS] = int((data[RO_FL_TTL_HOURS] - data[RO_FL_PURIFY_HOURS]) / 24)
                data[RO_FL_REMAINING_PCT] = math.floor(data[RO_FL_REMAINING_DAYS] * 24 * 100 / data[RO_FL_TTL_HOURS])
            if data[REAR_ACTIVE_C_FL_TTL_HOURS] - data[REAR_ACTIVE_C_FL_PURIFY_HOURS] <= 0:
                data[REAR_ACTIVE_C_FL_REMAINING_DAYS] = 0
                data[REAR_ACTIVE_C_FL_REMAINING_PCT] = 0
            else:
                data[REAR_ACTIVE_C_FL_REMAINING_DAYS] = int(
                (data[REAR_ACTIVE_C_FL_TTL_HOURS] - data[REAR_ACTIVE_C_FL_PURIFY_HOURS]) / 24)
                data[REAR_ACTIVE_C_FL_REMAINING_PCT] = math.floor(
                data[REAR_ACTIVE_C_FL_REMAINING_DAYS] * 24 * 100 / data[REAR_ACTIVE_C_FL_TTL_HOURS])

            self._data = data
            self._state = self._data[FILTERED_WATER_QUALITY]
        except DeviceException:
            _LOGGER.exception('获取小米厨下净水器属性失败')
            self._data = None
            self._state = None
            raise PlatformNotReady

    def update(self):
        """更新数据"""
        self.parse_data()

"""小米空气净化器组件初始化"""
from datetime import timedelta
import logging
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from homeassistant.const import (CONF_NAME, CONF_HOST, CONF_TOKEN, CONF_SCAN_INTERVAL)
from homeassistant.exceptions import PlatformNotReady
from homeassistant.helpers import discovery
from homeassistant.helpers.event import track_time_interval
from homeassistant.helpers.dispatcher import dispatcher_send
from homeassistant.helpers.entity import Entity
from homeassistant.util.dt import utcnow
from miio import Device, DeviceException, AirPurifier, VacuumException
from miio.airpurifier import OperationMode

_LOGGER = logging.getLogger(__name__)

REQUIREMENTS = ['python-miio>=0.3.1']

DEFAULT_NAME = 'mi_air_purifier'
DEFAULT_SCAN_INTERVAL = timedelta(seconds=30)

DOMAIN = 'mi_air_purifier'
CONF_MODEL = 'model'
DATA_KEY = 'mi_air_purifier_data'
DATA_STATE = 'state'

MODEL_AIR_PURIFIER_SUPER_2 = 'zhimi.airpurifier.sa2'

SUPPORTED_MODELS = [
    MODEL_AIR_PURIFIER_SUPER_2
]

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
    """初始化小米空气净化器组件"""

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

    if model is None:
        try:
            miio_device = Device(host, token)
            device_info = miio_device.info()
            model = device_info.model
            _LOGGER.info("发现空气净化器设备，型号[%s]，软件版本[%s]，硬件版本[%s]",
                         model,
                         device_info.firmware_version,
                         device_info.hardware_version)
        except DeviceException:
            raise PlatformNotReady
    if model in SUPPORTED_MODELS:
        try:
            air_purifier = AirPurifier(host, token)
            _LOGGER.info("实例化空气净化器[%s]成功", model)
            hass.data[DOMAIN][host] = air_purifier

            for component in ['fan', 'sensor']:
                _LOGGER.debug("加载组件[%s]", component)
                discovery.load_platform(hass, component, DOMAIN, {}, config)
        except VacuumException:
            _LOGGER.error("实例化空气净化器[%s]异常", model)
            raise PlatformNotReady
    else:
        _LOGGER.error("未支持设备型号[%s]", model)
        return False

    def update(event_time):
        """更新设备状态"""
        try:
            air_purifier.status()
            hass.data[DATA_KEY][host] = air_purifier
            dispatcher_send(hass, '{}_updated'.format(DOMAIN), host)
        except DeviceException as ex:
            dispatcher_send(hass, '{}_unavailable'.format(DOMAIN), host)
            _LOGGER.error("获取空气净化器状态时异常[%s]", ex)

    update(utcnow())
    track_time_interval(hass, update, scan_interval)

    def on_service(call):
        """打开空气净化器"""
        air_purifier.on()

    def off_service(call):
        """关闭空气净化器"""
        air_purifier.off()

    def set_mode_service(call):
        """设置模式"""
        mode = call.data.get("mode", "auto")
        air_purifier.set_mode(OperationMode(mode))

    def set_led_service(call):
        """设置LED"""
        led = call.data.get("led", True)
        air_purifier.set_led(led)

    """注册服务"""
    hass.services.register(DOMAIN, 'on', on_service)
    hass.services.register(DOMAIN, 'off', off_service)
    hass.services.register(DOMAIN, 'set_mode', set_mode_service)
    hass.services.register(DOMAIN, 'set_led', set_led_service)

    return True

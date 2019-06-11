# Home Assistant 小米厨下净水器组件

![Screenshot1](./images/screenshot1.png)

## 安装

1. 将本目录 [mi_kitchen_water_purifier] 所有文件复制到 [custom_components] 下
2. 获取小米厨下净水器 IP 及 Token

## 配置

```yaml
sensor:
  - platform: mi_kitchen_water_purifier
    host: 你获取的IP
    token: 你获取的Token
    name: 你自定义的名称
```

## 参考

基于看到现在使用量最大的小米净水器组件 [https://github.com/bit3725/homeassistant-mi-water-purifier](https://github.com/bit3725/homeassistant-mi-water-purifier) 修改，调整如下

- 去除了 Group，因为都是 Sensor，感觉额外封一个 Group 作为对象意义不大
- 将滤芯剩余天数与剩余百分比拆分为2个 Sensor
- 每种滤芯增加了新的属性：已净水量、已净水小时数、总净水量、总净水小时数
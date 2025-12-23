from datetime import timedelta

DOMAIN = "yainternetometr"

SENSOR_PING = "ping"
SENSOR_DOWNLOAD = "download"
SENSOR_UPLOAD = "upload"
CONF_UPDATE_INTERVAL = "update_interval"

DEVICE_MANUFACTURER = "Yandex"
DEVICE_MODEL = "Internetometr"
DEVICE_NAME = "YaInternetometr"
DEVICE_IDENTIFIER = "internet_test"

DEFAULT_SCAN_INTERVAL = timedelta(seconds=1800) # 30 minutes
MIN_SCAN_INTERVAL = 60 # 1 minute
MAX_SCAN_INTERVAL = 3600 # 1 hour
STEP_SCAN_INTERVAL = 30 # 30 seconds
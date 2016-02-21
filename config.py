general = dict(
    disableLogging = False,
    actionDataSource = 'actionData.csv',
    mediaRendererModelName = 'gmediarender',
    deviceSearchTimeout = 20,
    rfidLockIntervall = 6,
    logging_formatter = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

app = dict(
    host = '0.0.0.0',
    port = 80,
    debug = False,
)

wifi = dict(
    wpa_conf_file = '/etc/wpa_supplicant/wpa_supplicant.conf',
    interface_file = '/etc/network/interfaces',
)

rfid = dict(
    sleepTime = 1,
)

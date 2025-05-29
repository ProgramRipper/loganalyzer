import re

from i18n import _

from .vars import *
from .utils.utils import *


def checkDrop(lines):
    drops = searchExclude('insufficient bandwidth', lines, ['test_stream'])
    val = 0
    severity = 9000
    for drop in drops:
        try:
            v = float(drop[drop.find("(") + 1: drop.find(")")
                           ].strip('%').replace(",", "."))
        except (ValueError, OverflowError):
            v = 0
        if (v > val):
            val = v
    if (val != 0):
        if (val >= 15):
            severity = LEVEL_CRITICAL
        elif (15 > val and val >= 5):
            severity = LEVEL_WARNING
        else:
            severity = LEVEL_INFO
    return [
        severity,
        _("{}% Dropped Frames").format(val),
        _(
            "Your log contains streaming sessions with dropped frames. This can only be caused by a failure in your internet connection or your networking hardware. It is not caused by OBS. Follow the troubleshooting steps at: {}Dropped Frames and General Connection Issues{}."
        ).format(
            '<a href="https://obsproject.com/wiki/Dropped-Frames-and-General-Connection-Issues">',
            "</a>",
        ),
    ]


def checkKiller(lines):
    if (len(search('Interface: Killer', lines)) > 0):
        return [
            LEVEL_INFO,
            _("Killer NIC"),
            _(
                "Killer's Software Suite is known for its poor performance and issues when trying to stream. Please download the package from {}the vendor's page{} , completely uninstall all Killer NIC items and run the installer, choosing to only install the Hardware Drivers."
            ).format(
                '<a href="https://www.intel.com/content/www/us/en/download/19779/intel-killer-performance-suite.html">',
                "</a>",
            ),
        ]


def checkVantage(lines):
    if (len(search('Lenovo Vantage / Legion Edge is installed.', lines)) > 0):
        return [
            LEVEL_WARNING,
            _("Lenovo Vantage"),
            _(
                'Lenovo Vantage / Legion Edge is installed and is known to cause connection issues while streaming. Open Lenovo Vantage and set the "Network Boost" feature to disabled when streaming with OBS.'
            ),
        ]


def checkWifi(lines):
    if (len(search('802.11', lines)) > 0):
        return [
            LEVEL_WARNING,
            _("Wi-Fi Streaming"),
            _(
                "In many cases, wireless connections can cause issues because of their unstable nature. Streaming really requires a stable connection. Often wireless connections are fine, but if you have problems, the first troubleshooting step would be to switch to wired. We highly recommend streaming on wired connections."
            ),
        ]


def checkBind(lines):
    if (len(search('Binding to ', lines)) > 0):
        return [
            LEVEL_WARNING,
            _("Binding to IP"),
            _(
                'Binding to a manually chosen IP address is rarely needed. Go to Settings -> Advanced -> Network and set "Bind to IP" back to "Default".'
            ),
        ]


nicspeed_re = re.compile(r"(?i)Interface: (?P<nicname>.+) \(ethernet, ((?P<speed>\d+)|((?P<downspeed>\d+)↓/(?P<upspeed>\d+)↑)) mbps\)")


def checkNICSpeed(lines):
    nicLines = search('Interface: ', lines)
    if (len(nicLines) > 0):
        for i in nicLines:
            m = nicspeed_re.search(i)
            if m:
                nic = m.group("nicname")
                try:
                    if m.group("speed"):
                        speed = int(m.group("speed"))
                    elif m.group("upspeed"):
                        speed = int(m.group("upspeed"))
                except (ValueError, OverflowError):
                    speed = 1000
                if speed < 1000:
                    if 'GbE' in nic or 'Gigabit' in nic:
                        return [
                            LEVEL_WARNING,
                            _("Slow Network Connection"),
                            _(
                                "Your gigabit-capable network card is only connecting at 100mbps. This may indicate a bad network cable or outdated router / switch which could be impacting network performance."
                            ),
                        ]
    return None


def checkDynamicBitrate(lines):
    dynBrLines = search('Dynamic bitrate enabled', lines)
    if (len(dynBrLines) > 0):
        return [
            LEVEL_INFO,
            _("Dynamic Bitrate"),
            _(
                "Dynamic Bitrate is enabled. Instead of dropping frames when network issues are detected, OBS will automatically reduce the stream quality to compensate. The bitrate will adjust back to normal once the connection becomes stable. In some (very specific) situations, Dynamic Bitrate can get stuck at a low bitrate. If this happens frequently, it is recommended to turn off Dynamic Bitrate in Settings -> Advanced -> Network."
            ),
        ]
    return None


def checkNetworkOptimizations(lines):
    networkOptimizationLines = search('New socket loop enabled by user', lines)
    if (len(networkOptimizationLines) > 0):
        return [
            LEVEL_INFO,
            _("Network Optimizations"),
            _(
                "Network Optimizations are enabled. This option is disabled by default. It is only suggested to enable Network Optimizations if you are having issues streaming. The setting can be toggled in Settings -> Advanced -> Network."
            ),
        ]
    return None


def checkTCPPacing(lines):
    TCPPacingLines = search('Low latency mode enabled by user', lines)
    if (len(TCPPacingLines) > 0):
        return [
            LEVEL_INFO,
            _("TCP Pacing"),
            _(
                "TCP Pacing (Low Latency mode) is enabled. This option is disabled by default. It is only suggested to enable TCP Pacing if you are having issues streaming. The setting can be toggled in Settings -> Advanced -> Network."
            ),
        ]
    return None


def checkStreamDelay(lines):
    delayLines = search('second delay active', lines)
    if (len(delayLines) > 0):
        return [
            LEVEL_INFO,
            _("Stream Delay"),
            _(
                "Stream Delay may currently be active. This means that your stream is being delayed by a certain number of seconds. If this is not what you intended, please disable it in Settings -> Advanced -> Stream Delay."
            ),
        ]
    return None

from i18n import _

from .vars import *
from .utils.utils import *


def checkInit(lines):
    if search('Failed to initialize video', lines):
        return [
            LEVEL_CRITICAL,
            _("Initialize Failed"),
            _(
                "Failed to initialize video. Your GPU may not be supported, or your graphics drivers may need to be updated."
            ),
        ]


def getRenderLag(lines):
    drops = search('rendering lag', lines)
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

    return val


def checkRenderLag(lines):
    val = getRenderLag(lines)

    if (val != 0):
        if (val >= 10):
            severity = LEVEL_CRITICAL
        elif (10 > val and val >= 3):
            severity = LEVEL_WARNING
        else:
            severity = LEVEL_INFO

        return [
            severity,
            _("{}% Rendering Lag").format(val),
            _(
                "Your GPU is maxed out and OBS can't render scenes fast enough. Running a game without vertical sync or a frame rate limiter will frequently cause performance issues with OBS because your GPU will be maxed out. OBS requires a little GPU to render your scene."
            )
            + "<br><br>"
            + _(
                "Enable Vsync or set a reasonable frame rate limit that your GPU can handle without hitting 100% usage."
            )
            + "<br><br>"
            + _(
                "If that's not enough you may also need to turn down some of the video quality options in the game. If you are experiencing issues in general while using OBS, your GPU may be overloaded for the settings you are trying to use."
            )
            + "<br><br>"
            + _(
                "Please check our guide for ideas why this may be happening, and steps you can take to correct it: {}GPU Overload Issues{}."
            ).format(
                '<a href="https://obsproject.com/kb/encoding-performance-troubleshooting">',
                "</a>",
            ),
        ]


def checkAMDdrivers(lines):
    if search('The AMF Runtime is very old and unsupported', lines):
        return [
            LEVEL_WARNING,
            _("AMD Drivers"),
            _(
                "The AMF Runtime is very old and unsupported. The AMF Encoder will not work properly or not show up at all. Consider updating your drivers by downloading the newest installer from {}AMD's website{}."
            ).format('<a href="https://support.amd.com/en-us/download">', "</a>"),
        ]


def checkNVIDIAdrivers(lines):
    if (search('[jim-nvenc] Current driver version does not support this NVENC version, please upgrade your driver', lines) or search('[NVENC] Test process failed: outdated_driver', lines)):
        return [
            LEVEL_WARNING,
            _("Old NVIDIA Drivers"),
            _(
                "The installed NVIDIA driver does not support NVENC features needed for optimized encoders. Consider updating your drivers by downloading the newest installer from {}NVIDIA's website{}."
            ).format('<a href="https://www.nvidia.com/Download/index.aspx">', "</a>"),
        ]


def checkNVIDIAdriversEGL(lines):
    if not search('Using EGL/X11', lines):
        return
    if search('OpenGL loaded successfully, version 3.3.0 NVIDIA 390', lines):
        return [
            LEVEL_WARNING,
            _("Old NVIDIA Drivers"),
            _("Legacy NVIDIA 390 drivers do not support window capture on EGL."),
        ]


def checkVideoSettings(lines):
    videoSettings = []
    res = []
    for i, s in enumerate(lines):
        if "video settings reset:" in s:
            videoSettings.append(i)
    if (len(videoSettings) > 0):
        fmt = lines[videoSettings[-1] + 5].split()[-1]
        colorRange = lines[videoSettings[-1] + 6].split()[-1]
        if 'Full' in colorRange:
            res.append(
                [
                    LEVEL_WARNING,
                    _("Wrong Color Range"),
                    _(
                        'Having the Color Range set to "Full" will cause playback issues in certain browsers and on various video platforms. Shadows, highlights and color will look off. In OBS, go to "Settings -> Advanced" and set "Color Range" back to "Limited".'
                    ),
                ]
            )
        if (fmt != 'NV12' and fmt != 'P010'):
            res.append(
                [
                    LEVEL_CRITICAL,
                    _("Wrong Color Format"),
                    _(
                        "Color Formats other than NV12 and P010 are primarily intended for recording, and are not recommended when streaming. Streaming may incur increased CPU usage due to color format conversion. You can change your Color Format in Settings -> Advanced."
                    ),
                ]
            )

        basex, basey = lines[videoSettings[-1] + 1].split()[-1].split('x')
        outx, outy = lines[videoSettings[-1] + 2].split()[-1].split('x')
        fps_num, fps_den = lines[videoSettings[-1] + 4].split()[-1].split('/')
        try:
            baseAspect = float(basex) / float(basey)
            outAspect = float(outx) / float(outy)
            fps = float(fps_num) / float(fps_den)
        except (ValueError, OverflowError):
            return res                          # If fetching the resolution/fps fails, skip those checks

        if ((not ((1.77 < baseAspect) and (baseAspect < 1.7787))) or (not ((1.77 < outAspect) and (outAspect < 1.7787)))):
            res.append(
                [
                    LEVEL_WARNING,
                    _("Non-Standard Aspect Ratio"),
                    _(
                        "Almost all modern streaming services and video platforms expect video in 16:9 aspect ratio. OBS is currently configured to record in an aspect ratio that differs from that. You (or your viewers) will see black bars during playback. Go to Settings -> Video and change your Canvas Resolution to one that is 16:9."
                    ),
                ]
            )
        if (not ((fps == 60) or (fps == 30))):
            res.append(
                [
                    LEVEL_WARNING,
                    _("Non-Standard Framerate"),
                    _(
                        "Framerates other than 30fps or 60fps may lead to playback issues like stuttering or screen tearing. Stick to either of these for better compatibility with video players. You can change your OBS frame rate in Settings -> Video."
                    ),
                ]
            )
        if (fps >= 144):
            res.append(
                [
                    LEVEL_WARNING,
                    _("Excessively High Framerate"),
                    _(
                        "Recording at a tremendously high framerate will not give you higher quality recordings. Usually quite the opposite. Most computers cannot handle encoding at high framerates. You can change your OBS frame rate in Settings -> Video."
                    ),
                ]
            )
    return res

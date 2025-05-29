from i18n import _

from .vars import *
from .utils.utils import *


def getSessionTypeLine(lines):
    sessionType = search('Session Type:', lines)
    if len(sessionType) > 0:
        return sessionType[0]


def getWindowSystemLine(lines):
    windowSystem = search('Window System:', lines)
    if len(windowSystem) > 0:
        return windowSystem[0]


def checkDistro(lines):
    isDistroNix = search('Distribution:', lines)

    if len(isDistroNix) <= 0:
        return

    distro = isDistroNix[0].split()
    distro = distro[2:]
    distro = ' '.join(distro)

    return [LEVEL_INFO, distro, ""]


def checkFlatpak(lines):
    isFlatpak = search('Flatpak Runtime:', lines)

    if len(isFlatpak) > 0:
        return [
            LEVEL_INFO,
            _("Flatpak"),
            _(
                "You are using the Flatpak. Plugins are available as Flatpak extensions, which you can find in your Distribution's Software Center or via {}flatpak search com.obsproject.Studio{}. Installation of external plugins is not supported."
            ).format("<code>", "</code>"),
        ]


def checkSnapPackage(lines):
    isDistroNix = search('Distribution:', lines)

    if len(isDistroNix) <= 0:
        return

    if '"Ubuntu Core"' in isDistroNix[0]:
        return [
            LEVEL_WARNING,
            _("Snap Package"),
            _(
                "You are using the Snap Package. This is a community-supported modified build of OBS Studio; please file issues on the {}Snapcrafters GitHub{}."
            ).format(
                '<a href="https://github.com/snapcrafters/obs-studio/issues">', "</a>"
            )
            + "<br><br>"
            + _(
                "OBS may be unable to assist with issues arising out of the usage of this package. We recommend following our {}Install Instructions{} instead."
            ).format('<a href="https://obsproject.com/download#linux">', "</a>"),
        ]


def checkWayland(lines):
    isDistroNix = search('Distribution:', lines)
    isFlatpak = search('Flatpak Runtime:', lines)

    if (len(isDistroNix) <= 0) and (len(isFlatpak) <= 0):
        return

    sessionTypeLine = getSessionTypeLine(lines)
    if not sessionTypeLine:
        return

    if 'wayland' not in sessionTypeLine:
        return

    if len(isDistroNix) > 0:
        if '"Ubuntu" "20.04"' in isDistroNix[0]:
            return [
                LEVEL_CRITICAL,
                _("Ubuntu 20.04 under Wayland"),
                _(
                    "Ubuntu 20.04 does not provide the needed dependencies for OBS to capture under Wayland."
                )
                + "<br>"
                + _("Capture will only function under X11/Xorg."),
            ]

    windowSystemLine = getWindowSystemLine(lines)
    # If there is no Window System, OBS is running under Wayland
    if windowSystemLine:
        # If there is, OBS is running under XWayland
        return [
            LEVEL_CRITICAL,
            _("Running under XWayland"),
            _(
                "OBS is running under XWayland, which prevents OBS from being able to capture."
            )
            + "<br>"
            + _(
                "To fix that, you will need to run OBS with the following command in a terminal:{}obs -platform wayland{}"
            ).format("<p><code>", "</code></p>"),
        ]

    hasNoPipewireCapture = search('[pipewire] No capture', lines)
    if len(hasNoPipewireCapture) > 0:
        return [
            LEVEL_CRITICAL,
            _("No PipeWire capture on Wayland"),
            _(
                "In order to capture displays or windows under Wayland, OBS requires the appropriate PipeWire capture portal for your Desktop Environment."
            )
            + "<br><br>"
            + _(
                "An overview of available capture portals can be found on the Arch Linux Wiki:"
            )
            + "<br>"
            + _("{}XDG Desktop Portal{}").format(
                '<a href="https://wiki.archlinux.org/title/XDG_Desktop_Portal">',
                "</a>",
            )
            + "<br>"
            + _(
                "Note that the availability of Window and/or Display capture depends on your Desktop Environment's implementation of these portals."
            ),
        ]

    return [LEVEL_INFO, "Wayland", ""]


def checkX11Captures(lines):
    isDistroNix = search('Distribution:', lines)
    isFlatpak = search('Flatpak Runtime:', lines)

    if (len(isDistroNix) <= 0) and (len(isFlatpak) <= 0):
        return

    sessionTypeLine = getSessionTypeLine(lines)
    if not sessionTypeLine:
        return

    if 'x11' not in sessionTypeLine:
        return

    # obsolete PW sources
    hasPipewireCaptureDesktop = search('pipewire-desktop-capture-source', lines)
    hasPipewireCaptureWindow = search('pipewire-window-capture-source', lines)
    # unified PW source
    hasPipewireCaptureScreen = search('pipewire-screen-capture-source', lines)

    if (len(hasPipewireCaptureDesktop) > 0) or (len(hasPipewireCaptureWindow) > 0) or (len(hasPipewireCaptureScreen) > 0):
        return [
            LEVEL_WARNING,
            _("PipeWire capture on X11"),
            _(
                "Most Desktop Environments do not implement the PipeWire capture portals on X11. This can result in being unable to pick a window or display, or the selected source will stay empty."
            )
            + "<br><br>"
            + _(
                'We generally recommend using "Window Capture (Xcomposite)" on X11, as "Display Capture (XSHM)" can introduce bottlenecks depending on your setup.'
            ),
        ]

    return [LEVEL_INFO, "X11", ""]


def checkDesktopEnvironment(lines):
    isDistroNix = search('Distribution:', lines)
    isFlatpak = search('Flatpak Runtime:', lines)

    if (len(isDistroNix) <= 0) and (len(isFlatpak) <= 0):
        return

    desktopEnvironmentLine = search('Desktop Environment:', lines)
    desktopEnvironment = desktopEnvironmentLine[0].split()

    if (len(desktopEnvironment) > 3):
        desktopEnvironment = desktopEnvironment[3:]
        desktopEnvironment = ' '.join(desktopEnvironment)
    else:
        desktopEnvironment = ''

    if (len(desktopEnvironment) > 0):
        return [LEVEL_INFO, desktopEnvironment, '']


def checkMissingModules(lines):
    isDistroNix = search('Distribution:', lines)

    if (len(isDistroNix) <= 0):
        return

    modulesMissingList = []
    modulesCheckList = ('obs-browser.so', 'obs-websocket.so', 'vlc-video.so')

    for module in modulesCheckList:
        if not search(module, lines):
            modulesMissingList.append(module)

    if len(modulesMissingList):
        modulesMissingString = str(modulesMissingList)
        modulesMissingString = modulesMissingString.replace("['", "<ul><li>")
        modulesMissingString = modulesMissingString.replace("', '", "</li><li>")
        modulesMissingString = modulesMissingString.replace("']", "</li></ul>")

        return [
            LEVEL_INFO,
            _("Missing Modules ({})").format(len(modulesMissingList)),
            _("You are missing the following default modules:")
            + "<br>"
            + modulesMissingString,
        ]


def checkLinuxVCam(lines):
    isDistroNix = search('Distribution:', lines)
    isFlatpak = search('Flatpak Runtime:', lines)

    if (len(isDistroNix) <= 0) and (len(isFlatpak) <= 0):
        return

    hasV4L2Module = search('v4l2loopback not installed', lines)

    if len(hasV4L2Module) > 0:
        return [
            LEVEL_INFO,
            _("Virtual Camera not available"),
            _(
                "Using the Virtual Camera requires the {}v4l2loopback{} kernel module to be installed."
            ).format("<code>", "</code>")
            + "<br>"
            + _(
                "If required, please refer to our {}Install Instructions{} on how to install this on your distribution."
            ).format(
                '<a href="https://github.com/obsproject/obs-studio/wiki/install-instructions#prerequisites-for-all-versions">',
                "</a>",
            ),
        ]

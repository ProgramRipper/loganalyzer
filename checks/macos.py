from checks.vars import *
import html

from i18n import _

from .utils.utils import *
from .utils.macosversions import *


def getMacVersionLine(lines):
    isMac = search('OS Name: Mac OS X', lines) + search('OS Name: macOS', lines)
    macVersion = search('OS Version:', lines)
    if (len(isMac) > 0 and len(macVersion) > 0):
        return macVersion[0]


def getMacVersion(lines):
    versionLine = getMacVersionLine(lines)

    if not versionLine:
        return

    m = macver_re.search(versionLine)
    if not m:
        return

    ver = {
        "major": m.group("major"),
        "minor": m.group("minor"),
        "full": m.group("major") + "." + m.group("minor")
    }

    if ver["full"] in macversions:
        v = macversions[ver["full"]]
        ver.update(v)
        return ver

    if ver["major"] in macversions:
        v = macversions[ver["major"]]
        ver.update(v)
        return ver

    return


def checkMacVer(lines):
    verinfo = getMacVersion(lines)
    if not verinfo:
        return

    mv = "macOS %s.%s" % (html.escape(verinfo["major"]), html.escape(verinfo["minor"]))
    try:
        if (int(verinfo["major"]) <= 10 and "max" in verinfo):
            msg = _(
                "You are running {} {}, which is multiple versions out of date and no longer supported by Apple or recent OBS versions. We recommend updating to the latest macOS release to ensure continued security, functionality and compatibility."
            ).format(mv, html.escape(verinfo["name"]))
            mv += " (EOL)"
            return [LEVEL_WARNING, mv, msg]
    except (ValueError, OverflowError):
        pass

    if "latest" in verinfo:
        msg = _(
            "You are running {} {}, which is currently supported by Apple and the most recent version of OBS."
        ).format(mv, html.escape(verinfo["name"]))
        mv += " (OK)"
        return [LEVEL_INFO, mv, msg]

    msg = _(
        "You are running {} {}, which is not officially supported by Apple but is compatible with the most recent version of OBS. Updating to a more recent version of macOS is recommended to ensure that you are able to install future versions of OBS."
    ).format(mv, html.escape(verinfo["name"]))
    mv += " (OK)"
    return [LEVEL_INFO, mv, msg]


def checkRosettaTranslationStatus(lines):
    if (len(search('Rosetta translation used: true', lines)) > 0):
        return [
            LEVEL_WARNING,
            _("Intel OBS on Apple Silicon Mac"),
            _(
                "You are running the Intel version of OBS on an Apple Silicon Mac. You may get improved performance using the Apple Silicon version of OBS."
            ),
        ]


def checkMacPermissions(lines):
    macPerms = search('[macOS] Permission for', lines)
    deniedPermissions = set()

    for line in macPerms:
        if 'denied' in line:
            found = re.search(r'Permission for (.+) denied', line)
            if found:
                permissionName = found.group(1).title()
                permissionDescription = {
                    "Audio Device Access": _(
                        "{}Microphone{}: OBS requires this permission if you want to capture your microphone."
                    ).format("<b>", "</b>"),
                    "Video Device Access": _(
                        "{}Camera{}: This permission is needed in order to capture content from a webcam or capture card."
                    ).format("<b>", "</b>"),
                    "Accessibility": _(
                        "{}Accessibility{}: For keyboard shortcuts (hotkeys) to work while other apps are focused this permission is needed."
                    ).format("<b>", "</b>"),
                    "Screen Capture": _(
                        "{}Screen Recording{}: OBS requires this permission to be able to capture your screen."
                    ).format("<b>", "</b>"),
                }.get(permissionName)

                if permissionDescription:
                    deniedPermissions.add(permissionDescription)

    if deniedPermissions:
        deniedPermissionsString = "<br>\n<ul>\n<li>" + "</li>\n<li>".join(deniedPermissions) + "</li>\n</ul>"
        return [
            LEVEL_WARNING,
            _("Permissions Not Granted ({})").format(len(deniedPermissions)),
            _(
                "The following permissions have not been granted:{}If you would like to grant permissions for the above, follow the instructions in the {}macOS Permissions Guide{}."
            ).format(
                deniedPermissionsString,
                '<a href="https://obsproject.com/kb/macos-permissions-guide">',
                "</a>",
            ),
        ]

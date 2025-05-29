import html
import re
from pkg_resources import parse_version

from i18n import _

from .vars import *
from .utils.utils import *


def checkClassic(lines):
    if (len(search(': Open Broadcaster Software v0.', lines)) > 0):
        return True, [
            LEVEL_CRITICAL,
            _("OBS Classic"),
            _(
                "You are still using OBS Classic. This version is no longer supported. While we cannot and will not do anything to prevent you from using it, we cannot help with any issues that may come up."
            )
            + "<br>"
            + _("It is recommended that you update to OBS Studio.")
            + "<br><br>"
            + _(
                "Further information on why you should update (and how): {}OBS Classic to OBS Studio{}."
            ).format(
                '<a href="https://obsproject.com/forum/threads/how-to-easily-switch-to-obs-studio.55820/">',
                "</a>",
            ),
        ]
    else:
        return False, [LEVEL_NONE, _("OBS Studio"), _("Nothing to say")]


def checkCrash(lines):
    if (len(search('Unhandled exception:', lines)) > 0):
        return True, [
            LEVEL_CRITICAL,
            _("Crash Log"),
            _(
                "You have uploaded a crash log. The Log Analyzer does not yet process crash logs."
            ),
        ]
    else:
        return False, [LEVEL_NONE, _("OBS Studio Log"), _("Nothing to say")]


def checkDual(lines):
    if (len(search('Warning: OBS is already running!', lines)) > 0):
        return [
            LEVEL_CRITICAL,
            _("Two Instances"),
            _(
                "Two instances of OBS are running. If you are not intentionally running two instances, they will likely interfere with each other and consume excessive resources. Stop one of them. Check Task Manager for stray OBS processes if you can't find the other one."
            ),
        ]


def checkAutoconfig(lines):
    if (len(search('Auto-config wizard', lines)) > 0):
        return [
            LEVEL_CRITICAL,
            _("Auto-Config Wizard"),
            _(
                "The log contains an Auto-Config Wizard run. Results of this analysis are therefore inaccurate. Please post a link to a clean log file."
            )
            + cleanLog,
        ]


def checkCPU(lines):
    cpu = search('CPU Name', lines)
    if (len(cpu) > 0):
        if (('APU' in cpu[0]) or ('Pentium' in cpu[0]) or ('Celeron' in cpu[0])):
            return [
                LEVEL_CRITICAL,
                _("Insufficient Hardware"),
                _(
                    "Your system is below minimum specs for OBS to run and may be too underpowered to livestream. There are no recommended settings we can suggest, but try the Auto-Config Wizard in the Tools menu. You may need to upgrade or replace your computer for a better experience."
                ),
            ]
        elif ('i3' in cpu[0]):
            return [
                LEVEL_INFO,
                _("Insufficient Hardware"),
                _(
                    "Your system is below minimum specs for OBS to run and is too underpowered to livestream using software encoding. Livestreams and recordings may run more smoothly if you are using a hardware encoder like QuickSync, NVENC or AMF (via Settings -> Output)."
                ),
            ]


def getOBSVersionLine(lines):
    versionPattern = re.compile(r': OBS \d+\.\d+\.\d+')
    versionLines = search('OBS', lines)
    for line in versionLines:
        if versionPattern.search(line):
            return line
    return versionLines[-1]


def getOBSVersionString(lines):
    versionLine = getOBSVersionLine(lines)
    versionString = versionLine[versionLine.find("OBS"):]
    return versionString.split()[1]


obsver_re = re.compile(r"""
    (?i)
    (?P<ver_major>[0-9]+)
    \.
    (?P<ver_minor>[0-9]+)
    \.
    (?P<ver_micro>[0-9]+)
    (
        -
        (?P<special> (?P<special_type> rc|beta) \d*)
    )?
    $
    """, re.VERBOSE)


def checkObsVersion(lines):
    versionString = getOBSVersionString(lines)

    if parse_version(versionString) == parse_version('21.1.0'):
        return [
            LEVEL_WARNING,
            _("Broken Auto-Update"),
            _(
                "You are not running the latest version of OBS Studio. Automatic updates in version 21.1.0 are broken due to a bug."
            )
            + "<br>"
            + _(
                "Please update by downloading the latest installer from the {}downloads page{} and running it."
            ).format('<a href="https://obsproject.com/download">', "</a>"),
        ]

    m = obsver_re.search(versionString.replace('-modified', ''))

    if m is None and re.match(r"(?:\d)+\.(?:\d)+\.(?:\d)+\+(?:[\d\w\-\.~\+])+", versionString):
        return [
            LEVEL_INFO,
            _("Unofficial OBS Build ({})").format(html.escape(versionString)),
            _(
                "Your OBS version identifies itself as '{}', which is not an official build."
            ).format(html.escape(versionString))
            + "<br>"
            + _(
                "If you are on Linux, ensure you're using the PPA. If you cannot switch to the PPA, contact the maintainer of the package for any support issues."
            ),
        ]
    if m is None and re.match(r"(?:\d)+\.(?:\d)+\.(?:\d\w)+(?:-caffeine)", versionString):
        return [
            LEVEL_INFO,
            _("Third party OBS Version ({})").format(html.escape(versionString)),
            _(
                "Your OBS version identifies itself as '{}', which is made by a third party. Contact them for any support issues."
            ).format(html.escape(versionString)),
        ]
    if m is None and re.match(r"(?:\d)+\.(?:\d)+\.(?:\d)+-(?:[\d-])*([a-z0-9]+)(?:-modified){0,1}", versionString):
        return [
            LEVEL_INFO,
            _("Custom OBS Build ({})").format(html.escape(versionString)),
            _(
                "Your OBS version identifies itself as '{}', which is not a released OBS version."
            ).format(html.escape(versionString)),
        ]
    if m is None:
        return [
            LEVEL_INFO,
            _("Unparseable OBS Version ({})").format(html.escape(versionString)),
            _(
                "Your OBS version identifies itself as '{}', which cannot be parsed as a valid OBS version number."
            ).format(html.escape(versionString)),
        ]

    # Do we want these to check the version number and tell the user that a
    # release version is actually available, if one is actually available?
    # We can consider adding something like that later.
    if m.group("special") is not None:
        if m.group("special_type") == "beta":
            return [
                LEVEL_INFO,
                _("Beta OBS Version ({})").format(html.escape(versionString)),
                _(
                    "You are running a beta version of OBS. There is nothing wrong with this, but you may experience problems that you may not experience with fully released OBS versions. You are encouraged to upgrade to a released version of OBS as soon as one is available."
                ),
            ]

        if m.group("special_type") == "rc":
            return [
                LEVEL_INFO,
                _("Release Candidate OBS Version ({})").format(
                    html.escape(versionString)
                ),
                _(
                    "You are running a release candidate version of OBS. There is nothing wrong with this, but you may experience problems that you may not experience with fully released OBS versions. You are encouraged to upgrade to a released version of OBS as soon as one is available."
                ),
            ]

    if parse_version(versionString.replace('-modified', '')) < parse_version(CURRENT_VERSION):
        return [
            LEVEL_WARNING,
            _("Old Version ({})").format(html.escape(versionString)),
            _(
                "You are running an old version of OBS Studio ({}) Please update to version {} by going to Help -> Check for updates in OBS or by downloading the latest installer from the {}downloads page{} and running it."
            ).format(
                html.escape(versionString),
                html.escape(CURRENT_VERSION),
                '<a href="https://obsproject.com/download">',
                "</a>",
            ),
        ]


def checkOperatingSystem(lines):
    firstSection = lines[:getSubSections(lines)[0]]
    for s in firstSection:
        if 'mac' in s:
            return "mac"
        elif 'windows' in s:
            return "windows"
        elif 'linux' in s:
            return "linux"


def checkPortableMode(lines):
    if search('Portable mode: true', lines):
        return [
            LEVEL_INFO,
            _("Portable Mode"),
            _(
                "You are running OBS in Portable Mode. This means that OBS will store its settings with the executable. This is useful if you want to run OBS from a flash drive or other removable media."
            ),
        ]


def checkSafeMode(lines):
    if search('Safe Mode enabled.', lines):
        modulesNotLoaded = search('not on safe list', lines)
        moduleNames = []

        for line in modulesNotLoaded:
            found = re.search(r"'([^']+)'", line)
            if found:
                moduleNames.append(found.group(1))

        if moduleNames:
            modulesNotLoadedString = "<br>\n<ul>\n<li>" + "</li>\n<li>".join(moduleNames) + "</li>\n</ul>"
            return [
                LEVEL_WARNING,
                _("Safe Mode Enabled ({})").format(len(moduleNames)),
                _(
                    "You are running OBS in Safe Mode. Safe Mode disables third-party plugins and prevents scripts from running. The following modules were not loaded:"
                )
                + modulesNotLoadedString,
            ]
        else:
            return [
                LEVEL_WARNING,
                _("Safe Mode Enabled"),
                _(
                    "You are running OBS in Safe Mode. Safe Mode disables third-party plugins and prevents scripts from running."
                ),
            ]

from __future__ import print_function
from __future__ import unicode_literals

import logging
import time
import subprocess
import re
import glob
import os
import sys
import locale


logger = logging.getLogger(__name__)
encoding = locale.getdefaultlocale()[1]


def clean_unmount(cmd, mountpoint, tries=5, rmdir=True):
    cmd.append(mountpoint)

    # AVFS mounts are not actually unmountable, but are symlinked.
    if os.path.exists(os.path.join(mountpoint, 'avfs')):
        os.remove(os.path.join(mountpoint, 'avfs'))
        # noinspection PyProtectedMember
        logger.debug("Removed {}".format(os.path.join(mountpoint, 'avfs')))
    elif os.path.islink(mountpoint):
        pass  # if it is a symlink, we can simply skip to removing it
    else:
        # Perform unmount
        # noinspection PyBroadException
        try:
            check_call_(cmd)
        except:
            return False

    # Remove mountpoint only if needed
    if not rmdir:
        return True

    for _ in range(tries):
        if not os.path.ismount(mountpoint):
            # Unmount was successful, remove mountpoint
            if os.path.islink(mountpoint):
                os.unlink(mountpoint)
            else:
                os.rmdir(mountpoint)
            break
        else:
            time.sleep(1)

    if os.path.isdir(mountpoint):
        return False
    else:
        return True


def is_encase(path):
    return re.match(r'^.*\.E\w\w$', path)


def is_compressed(path):
    return re.match(r'^.*\.((zip)|(rar)|((t(ar\.)?)?gz))$', path)


def is_vmware(path):
    return re.match(r'^.*\.vmdk', path)


def expand_path(path):
    """
    Expand the given path to either an Encase image or a dd image
    i.e. if path is '/path/to/image.E01' then the result of this method will be
    /path/to/image.E*'
    and if path is '/path/to/image.001' then the result of this method will be
    '/path/to/image.[0-9][0-9]?'
    """
    if is_encase(path):
        return glob.glob(path[:-2] + '??')
    elif re.match(r'^.*\.\d{2,3}$', path):
        return glob.glob(path[:path.rfind('.')] + '.[0-9][0-9]?')
    else:
        return [path]


def command_exists(cmd):
    fpath, fname = os.path.split(cmd)
    if fpath:
        return os.path.isfile(cmd) and os.access(cmd, os.X_OK)
    else:
        for p in os.environ['PATH'].split(os.pathsep):
            p = p.strip('"')
            fp = os.path.join(p, cmd)
            if os.path.isfile(fp) and os.access(fp, os.X_OK):
                return True

    return False


def module_exists(mod):
    import importlib
    try:
        importlib.import_module(mod)
        return True
    except ImportError:
        return False


def check_call_(cmd, *args, **kwargs):
    logger.debug('$ {0}'.format(' '.join(cmd)))
    return subprocess.check_call(cmd, *args, **kwargs)


def check_output_(cmd, *args, **kwargs):
    logger.debug('$ {0}'.format(' '.join(cmd)))
    result = subprocess.check_output(cmd, *args, **kwargs)
    if result:
        result = result.decode(encoding)
    return result


# noinspection PyBroadException
def force_clean(execute=True, pattern=r".*/im_[0-9.]+_.+", glob_pattern="/tmp/im_*"):
    """Cleans previous mount points without knowing which is mounted. It assumes proper naming of mountpoints.

    1. Unmounts all bind mounted folders in folders with a name of the form *pattern*
    2. Unmounts all folders with a name of the form *pattern* or originating from */image_mounter_*
    3. Deactivates volume groups which originate from a loopback device, which originates from */image_mounter_*
    4. ... and unmounts their related loopback devices
    5. Unmounts all /image_mounter_ folders
    6. Removes all folders matching both *glob_pattern* and *pattern*
    6. Removes all /tmp/image_mounter_* folders

    Performs only a dry run when execute==False
    """

    os.environ['LVM_SUPPRESS_FD_WARNINGS'] = '1'
    commands = []

    # find all mountponits
    mountpoints = {}
    # noinspection PyBroadException
    try:
        result = check_output_(['mount'])
        for line in result.splitlines():
            m = re.match(r'(.+) on (.+) type (.+) \((.+)\)', line)
            if m:
                mountpoints[m.group(2)] = (m.group(1), m.group(3), m.group(4))
    except Exception:
        pass

    # start by unmounting all bind mounts
    for mountpoint, (orig, fs, opts) in mountpoints.items():
        if 'bind' in opts and re.match(pattern, mountpoint):
            commands.append('umount {0}'.format(mountpoint))
            if execute:
                clean_unmount(['umount'], mountpoint, rmdir=False)
    # now unmount all mounts originating from an image_mounter
    for mountpoint, (orig, fs, opts) in mountpoints.items():
        if 'bind' not in opts and ('/image_mounter_' in orig or re.match(pattern, mountpoint)):
            commands.append('umount {0}'.format(mountpoint))
            commands.append('rm -Rf {0}'.format(mountpoint))
            if execute:
                clean_unmount(['umount'], mountpoint)

    # find all loopback devices
    loopbacks = {}
    try:
        result = check_output_(['losetup', '-a'])
        for line in result.splitlines():
            m = re.match(r'(.+): (.+) \((.+)\).*', line)
            if m:
                loopbacks[m.group(1)] = m.group(3)
    except Exception:
        pass

    # find volume groups
    try:
        result = check_output_(['pvdisplay'])
        pvname = vgname = None
        for line in result.splitlines():
            if '--- Physical volume ---' in line:
                pvname = vgname = None
            elif "PV Name" in line:
                pvname = line.replace("PV Name", "").strip()
            elif "VG Name" in line:
                vgname = line.replace("VG Name", "").strip()

            if pvname and vgname:
                try:
                    # unmount volume groups with a physical volume originating from a disk image
                    if '/image_mounter_' in loopbacks[pvname]:
                        commands.append('lvchange -a n {0}'.format(vgname))
                        commands.append('losetup -d {0}'.format(pvname))
                        if execute:
                            check_output_(['lvchange', '-a', 'n', vgname])
                            check_output_(['losetup', '-d', pvname])
                except Exception:
                    pass
                pvname = vgname = None

    except Exception:
        pass

    # unmount base image
    for mountpoint, _ in mountpoints.items():
        if '/image_mounter_' in mountpoint:
            commands.append('fusermount -u {0}'.format(mountpoint))
            commands.append('rm -Rf {0}'.format(mountpoint))
            if execute:
                clean_unmount(['fusermount', '-u'], mountpoint)

    # finalize by cleaning /tmp
    for folder in glob.glob(glob_pattern):
        if re.match(pattern, folder):
            cmd = 'rm -Rf {0}'.format(folder)
            if cmd not in commands:
                commands.append(cmd)
            if execute:
                try:
                    os.rmdir(folder)
                except Exception:
                    pass
    for folder in glob.glob("/tmp/image_mounter_*"):
        cmd = 'rm -Rf {0}'.format(folder)
        if cmd not in commands:
            commands.append(cmd)
        if execute:
            try:
                os.rmdir(folder)
            except Exception:
                pass

    return commands


def determine_slot(table, slot):
    if int(table) >= 0:
        return int(table) * 4 + int(slot) + 1
    else:
        return int(slot) + 1


def terminal_supports_color():
    return (sys.platform != 'Pocket PC' and (sys.platform != 'win32' or 'ANSICON' in os.environ)
            and hasattr(sys.stdout, 'isatty') and sys.stdout.isatty())
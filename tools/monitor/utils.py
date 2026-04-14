import platform


def is_linux():
    return 'Linux' in platform.system()


def is_fedora():
    release = platform.freedesktop_os_release()
    return 'Fedora' in release['NAME']

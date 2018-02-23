import sys

def is_windows_os():
    return sys.platform.startswith('win') or sys.platform.startswith('cygwin')

def is_mac_os():
    return sys.platform.startswith('darwin')

def is_linux_os():
    return sys.platform.startswith('linux')


# Other available values from sys.platform:
'''
OS Name  || sys.platform's value
================================
OS/2	 || 'os2'
OS/2 EMX || 'os2emx'
RiscOS	 || 'riscos'
AtheOS	 || 'atheos'
'''

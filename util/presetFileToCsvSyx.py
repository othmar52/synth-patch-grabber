#!/usr/bin/python3

'''
    thanks to a4syxlist.py
        https://www.elektronauts.com/t/help-identifying-installed-sound-packs/119745/2

    this is a hacky script to extract preset names from SysEx files which get loaded on the synthesizer
    result is a csv file

'''
import sys

configs = [
    {
        'vendor': 'elektron',
        'model': 'analog 4 mkII',
        'sysExStartsWith': b'\xf0\x00\x20\x3c',
        'titleStart': 24,
        'titleEnd': 42,
        'msbPos': -1, # will be defined by the user on importing
        'pcPos':-1 # will be defined by the user on importing
    },
    {
        'vendor': 'dsi',
        'model': 'prophet08',
        'sysExStartsWith': b'\xf0\x01\x23\x02',
        'titleStart': 217,
        'titleEnd': 235,
        'msbPos': 4,
        'pcPos': 5
    },
    {
        'vendor': 'behringer',
        'model': 'deepmind',
        'sysExStartsWith': b'\xf0\x00\x20\x32',
        'titleStart': 265,
        'titleEnd': 282,
        'msbPos': 8,
        'pcPos': 9
    },
    # TODO: patchset has only a single sysex message. how to split this into single patches?
    {
        'vendor': 'korg',
        'model': 'mikrokorg',
        'sysExStartsWith': b'\xf0\x42\x30\x58',
        'titleStart': 265,
        'titleEnd': 282,
        'msbPos': 8,
        'pcPos': 9
    }
    
    #'korg-microkorg': b'\xf0\x42\x30\x58'
]

vendorConf = {}

chunkSize = 512
sysExStartByte = b'\xF0'
sysExEndByte = b'\xF7'

def read_sysex_msg(f):
    """Generator for reading sysex messages from a file."""
    buf = f.read(chunkSize)
    while buf.startswith(sysExStartByte):
        if sysExEndByte in buf:
            msg, buf = buf.split(sysExEndByte, 1)
            msg += sysExEndByte
            yield msg
            if not buf:
                buf += f.read(chunkSize)
        else:
            b = f.read(chunkSize)
            if not b: # eof
                break
            buf += b
    if buf:
        if buf.startswith(sysExStartByte):
            raise ValueError('Incomplete sysex message')
        else:
            raise ValueError('Not a sysex message')

def searchVendorConfig(m):
    for config in configs:
        if m.startswith(bytes(config['sysExStartsWith'])):
            return config
    return None

def read_sysex_messages(filename, func = None):
    global vendorConf
    count = 0
    with open(filename, 'rb') as f:
        for msg in read_sysex_msg(f):
            if len(msg) <= 2:
                continue # ignore empty messages
            try:
                vendorConf = searchVendorConfig(msg)
                #print(vendorConf)
            except KeyError:
                vendorConf = None
            if not vendorConf:
                raise ValueError('sysEx of unknown vendor. configure byte positions')
            count += 1
            if func:
                func(msg)
    return count

def extract(m, subject):
    data = {}
    if subject == "all" or subject == "title":
        data["title"] = m[vendorConf["titleStart"]:vendorConf["titleEnd"]].replace(b'\0', b'').decode("utf-8")

    if subject == "all" or subject == "msb":
        data["msb"] = m[vendorConf["msbPos"]]

    if subject == "all" or subject == "pc":
        data["pc"] = m[vendorConf["pcPos"]]

    return data


def debugSysEx(m):
    #print(len(m))
    print("-------------------------")
    for idx, xx in enumerate(m):
        if isinstance(xx, int):
            if xx > 0:
                print( xx, idx)



def main():
    func = None
    count = False
    argc = 1
    while len(sys.argv) > argc and sys.argv[argc].startswith('--'):
        arg = sys.argv[argc]
        argc += 1
        if arg == '--help':
            print("""Usage: {} [OPTION]... [FILE]...
Extract sysex messages from .syx files and print names of the sounds.

  --help   display this help and exit
  --names  print the name of each sound
  --count  print the number of sysex messages in each file
""".format(sys.argv[0]))
            return
        elif arg == '--names':
            func = lambda m : print(extract(m, "title"))
        elif arg == '--msb':
            func = lambda m : print(extract(m, "msb"))
        elif arg == '--pc':
            func = lambda m : print(extract(m, "pc"))
        elif arg == '--all':
            func = lambda m : print(extract(m, "all"))
        elif arg == '--count':
            count = True
        elif arg == '--':
            break
        else:
            raise ValueError("{}: invalid argment: {}".format(sys.argv[0], arg))

    for arg in sys.argv[argc:]:
        n = read_sysex_messages(arg, func)
        if count:
            print("Read {} non-empty sysex messages from {}".format(n, arg))

if __name__ == "__main__":
    main()




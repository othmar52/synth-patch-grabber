
def getDeviceConfigs(deviceIdentifier=''):
    # TODO read from separate yaml file
    # TODO validate configuration for missing/invalid values and for uniqueness property 'uniquePrefix'
    deviceConfigs = [
        {
            'patchConfType': 'csv',
            'uniquePrefix': 'wb12',
            'vendor': 'Waldorf',
            'model': 'Blofeld',
            'yearOfConstruction': 2007,
            'patchSetName': 'Factory 2012',
            'midiPort': 3,
            'midiChannel': 11,
            'color': 'darkgoldenrod',
            'csvPath': 'csv/patchlist/Waldorf - Blofeld (Factory Presets 2012).csv'
        },
        {
            'uniquePrefix': 'rpx',
            'vendor': 'GEM',
            'model': 'rp-x',
            'yearOfConstruction': 2006,
            'patchConfType': 'csv',
            'patchSetName': 'Factory',
            'midiPort': 2,
            'midiChannel': 4,
            'color': 'grey',
            'csvPath': 'csv/patchlist/GEM - rp-x.csv'
        },
        {
            'uniquePrefix': 'mkc',
            'vendor': 'KORG',
            'model': 'MicroKORG',
            'yearOfConstruction': 2000,
            'patchConfType': 'video-csv',
            'patchSetName': 'Cuckoo',
            'midiPort': 3,
            'midiChannel': 6,
            'color': 'teal',
            'csvPath': 'csv/patchlist/KORG - MicroKORG (Cuckoo Patches).csv',
            'video': {
                'path': 'util/MicroKORG-Cuckoo-Patches/128 NEW microKorg patches-UeiKJdvcync.webm',
                'col-start': 'yt-startsecond',
                'col-end': 'yt-endsecond',
                'delta-start': 0.2
            }
        },
        {
            'uniquePrefix': 's1f',
            'vendor': 'Roland',
            'model': 'System-1m',
            'yearOfConstruction': 2014,
            'patchConfType': 'csv',
            'patchSetName': 'Factory',
            'midiPort': 3,
            'midiChannel': 5,
            'color': 'lawngreen',
            'csvPath': 'csv/patchlist/Roland - System1.csv'
        },
        {
            'uniquePrefix': 's1p',
            'vendor': 'Roland',
            'model': 'System-1m',
            'yearOfConstruction': 2014,
            'patchConfType': 'csv',
            'patchSetName': 'Promars',
            'midiPort': 3,
            'midiChannel': 5,
            'color': 'lawngreen',
            'csvPath': 'csv/patchlist/Roland - System1 - Promars.csv'
        },
        {
            'uniquePrefix': 'vir',
            'vendor': 'Access',
            'model': 'Virus A',
            'yearOfConstruction': 1997,
            'patchConfType': 'csv',
            'patchSetName': 'Factory',
            'midiPort': 3,
            'midiChannel': 7,
            'color': 'firebrick',
            'csvPath': 'csv/patchlist/Access - VirusA.csv'
        },
        {
            'uniquePrefix': 'xid',
            'vendor': 'Roland',
            'model': 'JD-Xi',
            'yearOfConstruction': 2015,
            'patchConfType': 'csv',
            'patchSetName': 'Factory Digital',
            'midiPort': 3,
            'midiChannel': 1,
            'color': 'darkorange',
            'csvPath': 'csv/patchlist/Roland - JD-Xi dig.csv'
        },
        {
            'uniquePrefix': 'xia',
            'vendor': 'Roland',
            'model': 'JD-Xi',
            'yearOfConstruction': 2015,
            'patchConfType': 'csv',
            'patchSetName': 'Factory Analog',
            'midiPort': 3,
            'midiChannel': 3,
            'color': 'darkblue',
            'csvPath': 'csv/patchlist/Roland - JD-Xi ana.csv'
        },
        {
            'uniquePrefix': 'tb3',
            'vendor': 'Roland',
            'model': 'TB-3',
            'yearOfConstruction': 2014,
            'patchConfType': 'csv',
            'patchSetName': 'Factory',
            'midiPort': 3,
            'midiChannel': 9,
            'color': 'lawngreen',
            'csvPath': 'csv/patchlist/Roland - TB-3.csv'
        },
        {
            'uniquePrefix': 'ms2',
            'vendor': 'MFB',
            'model': 'Synth II',
            'yearOfConstruction': 2004,
            'patchConfType': 'csv',
            'patchSetName': 'Factory',
            'midiPort': 3,
            'midiChannel': 8,
            'color': 'dodgerblue',
            'csvPath': 'csv/patchlist/MFB - Synth2.csv'
        }
        #,
        #{
        #    'uniquePrefix': 'mkf',
        #    'vendor': 'KORG',
        #    'model': 'MicroKORG',
        #    'yearOfConstruction': 2000,
        #    'patchConfType': 'csv',
        #    'patchSetName': 'Factory',
        #    'midiPort': 3,
        #    'midiChannel': 6,
        #    'color': 'limegreen',
        #    'csvPath': 'csv/patchlist/KORG - MicroKORG.csv'
        #}
        #,
        #{
        #    'patchConfType': 'csv',
        #    'patchSetName': 'KORG - MS2000',
        #    'midiPort': 3,
        #    'midiChannel': 15,
        #    'color': 'seagreen',
        #    'csvPath': 'csv/patchlist/KORG - MS2000.csv'
        #},
        #{
        #    'patchConfType': 'generic',
        #    'patchSetName': 'Example of generic device withou csv sounds list',
        #    'msb': [0],
        #    'lsb': [],
        #    'patchRange': range(0,127), # will create [0,1,2,...,125,126]
        #    'midiPort': 3,
        #    'midiChannel': 7
        #}
    ]

    if deviceIdentifier == '':
        return deviceConfigs

    foundIdentifiers = []
    for deviceConfig in deviceConfigs:
        if deviceConfig['uniquePrefix'] == deviceIdentifier:
            return [deviceConfig]
        foundIdentifiers.append(deviceConfig['uniquePrefix'])

    raise ValueError(
        'configuration for \'%s\' not found.\n valid identifiers are %s' % (
            deviceIdentifier,
            ', '.join(foundIdentifiers)
        )
    )

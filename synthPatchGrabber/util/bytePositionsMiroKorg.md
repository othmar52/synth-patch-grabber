

TODO: split the single SysEx message with all 128 MicroKorg presets into 128 preset parts  
those nombers found `f0f7.net` should be helpful....

```js
angular.module("f0f7.devices").factory("KorgMicrokorg", ["$log", "$timeout", "Sysex", "WebMIDI", function(e, a, i, s) {
    return {
        id: "KorgMicrokorg",
        manuf: "Korg",
        model: "microKORG / MS2000",
        params: {
            deviceId: 48,
            banks: {
                bank1: {
                    label: "Internal",
                    address: 0
                }
            },
            patchesPerBank: 128,
            transferPause: 600,
            parserConfig: {
                name: {
                    from: 0,
                    to: 11
                },
                dna: {
                    from: 0,
                    to: 254
                }
            }
        },
        sendToBuffer: function(e) {
            var a = i.objectToArray(e.data)
              , r = [240, 66, this.params.deviceId, 88, 64];
            a = i.packDSISysex(a),
            a = r.concat(a, [247]),
            i.sendSysex(a, s.midiOut)
        },
        sendProgramToBank: function(e, a, r) {
            var t = this.reorderProgram(e, a, r);
            i.sendSysex(t, s.midiOut)
        },
        reorderProgram: function(e, a, r) {
            var t = i.objectToArray(e.data)
              , s = [240, 66, this.params.deviceId, 88, 76];
            t = i.packDSISysex(t),
            t = s.concat(t, [247]);
            var n = [240, 66, this.params.deviceId, 88, 17, 0, r, 247];
            return t = t.concat(n)
        },
        retrieveBank: function() {
            var e = [240, 66, this.params.deviceId, 88, 28, 247];
            i.sendSysex(e, s.midiOut)
        },
        extractPatchNames: function(e) {
            var a = [];
            switch ((e = i.objectToArray(e))[4]) {
            case 64:
                a = this.extractSinglePatch(e);
                break;
            case 76:
            case 80:
                a = this.extractMultiDump(e)
            }
            return a
        },
        extractMultiDump: function(e) {
            var a, r, t, s = e.slice(5, 37391), n = i.unpackDSISysex(s), o = [];
            for (a = 0,
            r = n.length; a < r; a += 254)
                254 == (t = n.slice(a, a + 254)).length && o.push(i.extractPatchName(t, this.params.parserConfig));
            return o
        },
        extractSinglePatch: function(e) {
            var a = e.slice(5, 296)
              , r = i.unpackDSISysex(a);
            return [i.extractPatchName(r, this.params.parserConfig)]
        },
        getMaxNameLength: function() {
            return this.params.parserConfig.name.to - this.params.parserConfig.name.from + 1
        },
        renameProgram: function(e, a) {
            var r = this.getMaxNameLength();
            return i.renameProgram(e, r, a.data, this.params.parserConfig)
        }
    }
}
])



unpackDSISysex: function(e) {
    e = e.concat([]);
    for (var a, r, t, s, n = []; 0 < e.length; )
        for (r = e.splice(0, 1),
        t = e.splice(0, 7),
        s = 0; s < t.length; s++)
            a = 1 & r,
            n.push(t[s] | a << 7),
            r >>= 1;
    return n
}
```
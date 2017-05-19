#
# All machines which can be used to do network test
#

NETWORK_SYS = {
    "dell-per515-01.lab.eng.pek2.redhat.com": {
        "ip": "10.73.75.170",
        "password": "redhat",
        "primary_nic": "em2",
        "bond": {"slaves": ["em2", "em1"],
                 "em1": "08:9e:01:63:2c:b2",
                 "em2": "08:9e:01:63:2c:b3"},

        "vlan": {"id": "50",
                 "nics": ["p2p1", "p2p2", "p3p1"],
                 "p2p1": "00:1b:21:a6:64:6c",
                 "p2p2": "00:1b:21:a6:64:6d",
                 "p3p1": "00:1b:21:a6:3d:7a"},
    },

    "ibm-x3650m5-04.lab.eng.pek2.redhat.com": {
        "ip": "10.73.130.225",
        "password": "redhat",
        "primary_nic": "eno1",
        "bond": {"slaves": ["eno1", "eno2"],
                 "eno1": "08:94:ef:21:c0:4d",
                 "eno2": "08:94:ef:21:c0:4e"},
        "vlan": {"id": "50",
                 "nics": ["eno3", "eno4"],
                 "eno3": "08:94:ef:21:c0:4f",
                 "eno4": "08:94:ef:21:c0:50"},
    },

    "dell-per730-35.lab.eng.pek2.redhat.com": {
        "ip": "",
        "password": "redhat",
        "primary_nic": "em1",
        "bond": {"slaves": ["em1", "em2"],
                 "em1": "24:6e:96:19:b9:a4",
                 "em2": "24:6e:96:19:b9:a5"},
        "vlan": {"id": "50",
                 "nics": ["p7p1", "p7p2"],
                 "p7p1": "a0:36:9f:9d:3b:fe",
                 "p7p2": "a0:36:9f:9d:3b:ff"},
    },

    "dell-per730-34.lab.eng.pek2.redhat.com": {
        "ip": "",
        "password": "redhat",
        "primary_nic": "em1",
        "bond": {"slaves": ["em1", "em2"],
                 "em1": "24:6e:96:19:bb:70",
                 "em2": "24:6e:96:19:bb:71"},
        "vlan": {"id": "50",
                 "nics": ["em3", "em4"],
                 "em3": "24:6e:96:19:bb:72",
                 "em4": "24:6e:96:19:bb:73"},
    },

    "dell-op790-01.qe.lab.eng.nay.redhat.com": {
        "ip": "10.66.148.7",
        "password": "redhat",
        "primary_nic": "em1",
        "bond": {"slaves": ["em1", "p4p2"],
                 "em1": "d4:be:d9:95:61:ca",
                 "p4p2": "00:10:18:81:a4:a2"},

        "vlan": {"id": "20",
                 "nics": ["p3p1", "p4p1"],
                 "p3p1": "00:1b:21:27:47:0b",
                 "p4p1": "00:10:18:81:a4:a0"},
    },
}

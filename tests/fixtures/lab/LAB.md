# Test Lab

## Rancid

### Configuration

- All devices have permanent hostname and ipv4 OAM address
- RANCID has 4 groups:
  - group_01_3rows: valid group with all devices, router.db has 3 columns
  - group_02_4rows: valid group with all devices, router.db has 4 columns
  - group_03_router_db_errors: invalid group, has errors in router.db
  - group_04_no_router_db: invalid group, router.db is absent
- Separately there's special folder with rancid-specific files, but without valid groups

### Commands

Backup all configs:

```
sudo -u rancid /usr/lib/rancid/bin/rancid-run
```

Copy configs from vm fo fixtures:

```
scp -r rancid@rancid:/var/lib/rancid ~/projects/faddr/tests/fixtures/
rm -rf ~/projects/faddr/tests/fixtures/rancid/bin
rm -rf ~/projects/faddr/tests/fixtures/rancid/logs
rm -rf ~/projects/faddr/tests/fixtures/rancid/.ssh
rm -rf ~/projects/faddr/tests/fixtures/rancid/.gnupg
rm -rf ~/projects/faddr/tests/fixtures/rancid/.bash_history
rm -rf ~/projects/faddr/tests/fixtures/rancid/.cloginrc
```

## Configuration rules

### Credentials

| Entry      | Value      |
| ---        | ---        |
| `login`    | `faddr`    |
| `password` | `faddr123` |
| `enable`   | `faddr123` |

### Interfaces

- port 0: OAM

- port 1:
  - vlan 100: ipv4 address 10.100.100.1/24
  - vlan 101: native, ipv4 address 10.101.101.1/24
  - vlan 102: qinq s-vlan 102, c-vlan 999, ipv4 address 10.102.102.1/24
  - vlan 110: vrf Test001, ipv4 address 10.110.110.1/24
  - vlan 121: acl input ACLin01 and output ACLout01, ipv4 address 10.121.121.121/24
  - vlan 122: acl input ACLin02, ipv4 address 10.122.122.122/24
  - vlan 123: acl output ACLout02, ipv4 address 10.123.123.123/24
  - vlan 131: rate-limit numerical, ipv4 address 10.131.131.131/24
  - vlan 132: rate-limit via service-policy-like object, ipv4 address 10.132.132.132/24
  - vlan 14x: reserved for QoS/CoS
  - vlan 16x: reserved for ipv6
  - vlan 201: xconnect to 2.2.2.1 with vcid 2001
  - vlan 202: xconnect to 2.2.2.2 with vcid 2002 and backup to 2.2.2.3 with vcid 2003
  - vlan 300: bridge group 300
  - vlan 401: VPLS ldp, neighbours 4.4.4.1, 4.4.4.2 and 4.4.4.3 with backup 4.4.4.4 vpls-id 4001
  - vlan 402: VPLS ldp, neighbours 4.4.4.5, 4.4.4.6, mesh group 1: neighbours 4.4.4.11 mesh group 2: 4.4.4.12
  - vlan 502: VPLS bgp, RD 64502:5002
  - vlan 503: VPLS bgp, RD 1.1.1.1:5003
  - vlan 600: MPLS, LDP, ipv4 address 10.60.0.1/30
  - vlan 601: ISIS, ipv4 address 10.60.1.1/30
  - vlan 602: OSPF, ipv4 address 10.60.2.1/30

- port 2: phy port for LAG

- virtual/logical interfaces:
  - Loopback0: mpls, ldp, address 1.1.1.1/32
  - Loopback10: OaM, vrf OAM, ipv4 address 10.10.10.1/32
  - Loopback100: bgp source for "router bgp" configuration, ipv4 address 100.100.100.1/32
  - irb/BVI/BDI interfaces:
    - vlan 100: ipv4 in GRT, ipv4 address 200.200.100.1/30
    - vlan 101: ipv4 in VRF, ipv4 address 200.200.101.1/30
    - vlan 102: ipv4 in bridge, ipv4 address 200.200.102.1/30
    - vlan 103: ipv4 in VRF and bridge, ipv4 address 200.200.103.1/30
    - vlan 104: ipv4 in VPLS, ipv4 address 200.200.104.1/30
    - vlan 105: ipv4 in VRF and VPLS, ipv4 address 200.200.105.1/30
  - logical-tunnel/Vurtual-Ethernet: TBD
  - SVI: TBD
  - LAG: TBD

### VRF

- Test001:
  - RD 1.1.1.1:110
  - RT import/export 64501:110

- Test002:
  - RD 64502:110
  - RT import/export 64502:110

- Test003:
  - RD 64503:110
  - RT import/export 64503:110
  - RT policy import RTimport
    - rt:64503:110
    - rt:64503:111
    - rt:64503:112
  - RT policy export RTexport
    - rt:64503:110
    - rt:64503:111
    - rt:64503:112

### Bridge

- 300: l2-only
- 301: l2+l3
- 302: l2 split-horizon

### VPLS

- VPLSldp01
- VPLSldp02
- VPLSbgp01
- VPLSbgp02

## Devices

| Vendor  | Type  | Model | Version | Hostname               | OAM ipv4 address  |
| ---     | ---   | ---   | ---     | ---                    | ---               |
| Cisco   | IOS   | 7206  | 15.2    | `cisco-ios-15-7206`    | `192.168.100.111` |
| Juniper | Junos | vMX   | 17.2    | `juniper-junos-17-vmx` | `192.168.100.112` |

### Cisco

#### IOS

Hostname: `cisco-ios-15-7206`

OAM: `192.168.100.111`

Device: 7206 on [`EVE-NG`](https://www.eve-ng.net/)

Version: `15.2(4)S7`

Status: WIP

Configuration:

```cpp
# Basic settings, AAA, connectivity
no logging console

enable secret faddr123
username faddr privilege 15 secret faddr123
no aaa new-model
line vty 0 4
login local

hostname cisco-ios-15-7206
ip domain-name lab.faddr
crypto key generate rsa [768]
ip ssh version 2
transport input telnet ssh

# VRFs
ip vrf OAM
rd 10.10.10.1:10
route-target export 10.10.10.1:10
route-target import 10.10.10.1:10

ip vrf Test001
rd 1.1.1.1:110
route-target export 64501:110
route-target import 64501:110

ip vrf Test002
rd 64502:110
route-target export 64502:110
route-target import 64502:110

ip vrf Test003
rd 64503:110
route-target export 64503:110
route-target import 64503:110

# ACLs
ip access-list standard ACLin01
permit any
ip access-list standard ACLout01
permit any

ip access-list standard ACLin02
permit any
ip access-list standard ACLout02
permit any

# Interfaces
interface Loopback0
description Loopback0: mpls, ldp, address 1.1.1.1/32
ip address 1.1.1.1 255.255.255.255

interface Loopback10
description Loopback10: OaM, vrf OAM, ipv4 address 10.10.10.1/32
ip vrf forwarding OAM
ip address 10.10.10.1 255.255.255.255

interface FastEthernet 0/0
no shutdown
description OAM
ip address 192.168.100.111 255.255.255.0

interface FastEthernet 1/0
no shutdown

interface FastEthernet 1/0.100
description vlan 100: ipv4 address 10.100.100.1/24
encapsulation dot1Q 100
ip address 10.100.100.1 255.255.255.0

interface FastEthernet 1/0.101
description vlan 101: native, ipv4 address 10.101.101.1/24
encapsulation dot1Q 101 native
ip address 10.101.101.1 255.255.255.0

interface FastEthernet1/0.102
description vlan 102: qinq s-vlan 102, c-vlan 999, ipv4 address 10.102.102.1/24
encapsulation dot1Q 102 second-dot1q 999
ip address 10.102.102.1 255.255.255.0

interface FastEthernet1/0.110
description vlan 110: vrf Test001, ipv4 address 10.110.110.1/24
encapsulation dot1Q 110
ip vrf forwarding Test001
ip address 10.110.110.1 255.255.255.0

interface FastEthernet1/0.121
description vlan 121: acl input ACLin01 and output01 ACLout, ipv4 address 10.121.121.121/24
encapsulation dot1Q 121
ip address 10.121.121.121 255.255.255.0
ip access-group ACLin01 in
ip access-group ACLout01 out

interface FastEthernet1/0.122
description vlan 122: acl input ACLin02, ipv4 address 10.122.122.122/24
encapsulation dot1Q 122
ip address 10.122.122.122 255.255.255.0
ip access-group ACLin02 in

interface FastEthernet1/0.123
description vlan 123: acl output ACLout02, ipv4 address 10.123.123.123/24
encapsulation dot1Q 123
ip address 10.123.123.123 255.255.255.0
ip access-group ACLout02 out
```

### Juniper

#### JunOS

Hostname: `juniper-junos-17-vmx`

OAM: `192.168.100.112`

Device: vMX on [`EVE-NG`](https://www.eve-ng.net/)

Version: `17.2R1.13`

Status: WIP

Notes:

- vMX needs trial license for some features to work properly. Read more: <https://www.juniper.net/us/en/dm/vmx-trial-download.html>

Configuration:

```
# Basic settings, AAA, connectivity
delete chassis auto-image-upgrade

set system root-authentication plain-text-password [faddr123]
set system login user faddr class super-user
set system login user faddr authentication plain-text-password [faddr123]

set interfaces fxp0.0 description OAM
set interfaces fxp0.0 family inet address 192.168.100.112/24
delete interfaces fxp0 unit 0 family inet dhcp

set system services telnet
set system services ssh
set system host-name juniper-junos-17-vmx
set system domain-name lab.faddr

set chassis network-services enhanced-ip

# VRFs
set routing-instances Test001 instance-type vrf
set routing-instances Test001 interface ge-0/0/1.110
set routing-instances Test001 route-distinguisher 1.1.1.1:110
set routing-instances Test001 vrf-target target:64501:110

# ACLs
set firewall family inet filter ACLin01 term 001 then accept
set firewall family inet filter ACLin02 term 001 then accept
set firewall family inet filter ACLout01 term 001 then accept
set firewall family inet filter ACLout02 term 001 then accept

# Interfaces
set interfaces ge-0/0/1 description "port 1"
set interfaces ge-0/0/1 flexible-vlan-tagging
set interfaces ge-0/0/1 native-vlan-id 101

set interfaces ge-0/0/1 unit 100 description "vlan 100: ipv4 address 10.100.100.1/24"
set interfaces ge-0/0/1 unit 100 vlan-id 100
set interfaces ge-0/0/1 unit 100 family inet address 10.100.100.1/24

set interfaces ge-0/0/1 unit 101 description "vlan 101: native, ipv4 address 10.101.101.1/24"
set interfaces ge-0/0/1 unit 101 vlan-id 101
set interfaces ge-0/0/1 unit 101 family inet address 10.101.101.1/24

set interfaces ge-0/0/1 unit 102 description "qinq s-vlan 102, c-vlan 999, ipv4 address 10.102.102.1/24"
set interfaces ge-0/0/1 unit 102 vlan-tags outer 102
set interfaces ge-0/0/1 unit 102 vlan-tags inner 999
set interfaces ge-0/0/1 unit 102 family inet mtu 1500
set interfaces ge-0/0/1 unit 102 family inet no-redirects
set interfaces ge-0/0/1 unit 102 family inet address 10.102.102.1/24

set interfaces ge-0/0/1 unit 110 description "vrf Test001, ipv4 address 10.110.110.1/24"
set interfaces ge-0/0/1 unit 110 vlan-id 110
set interfaces ge-0/0/1 unit 110 family inet address 10.110.110.1/24

set interfaces ge-0/0/1 unit 121 description "acl input ACLin01 and output ACLout01, ipv4 address 10.121.121.121/24"
set interfaces ge-0/0/1 unit 121 vlan-id 121
set interfaces ge-0/0/1 unit 121 family inet rpf-check
set interfaces ge-0/0/1 unit 121 family inet no-redirects
set interfaces ge-0/0/1 unit 121 family inet filter input ACLin01
set interfaces ge-0/0/1 unit 121 family inet filter output ACLout01
set interfaces ge-0/0/1 unit 121 family inet address 10.121.121.121/24

set interfaces ge-0/0/1 unit 122 description "acl input ACLin02, ipv4 address 10.122.122.122/24"
set interfaces ge-0/0/1 unit 122 vlan-id 122
set interfaces ge-0/0/1 unit 122 family inet filter input ACLin02
set interfaces ge-0/0/1 unit 122 family inet address 10.122.122.122/24

set interfaces ge-0/0/1 unit 123 disable
set interfaces ge-0/0/1 unit 123 description "acl output ACLout02, ipv4 address 10.123.123.123/24"
set interfaces ge-0/0/1 unit 123 vlan-id 123
set interfaces ge-0/0/1 unit 123 family inet filter output ACLout02
set interfaces ge-0/0/1 unit 123 family inet address 10.123.123.123/24
```

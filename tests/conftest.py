"""PyTest fixtures that are accessible by all tests."""

import pathlib

import pytest

from faddr.dataclasses import Interface, IPv4, Vlan, ACL, XConnect


CISCO_IOS_SIMPLE_CONFIG_PATH = (
    "tests/fixtures/config_snippets/cisco_ios/simple_config.conf"
)


@pytest.fixture
def cisco_ios_simple_config_path():
    """Returns Path-object for default test config."""
    config_path = pathlib.Path(CISCO_IOS_SIMPLE_CONFIG_PATH)
    return config_path


@pytest.fixture
def cisco_ios_simple_config_raw():
    """Reads config from file to list of strings."""
    with open(
        CISCO_IOS_SIMPLE_CONFIG_PATH, mode="r", errors="ignore", encoding="ascii"
    ) as config_file:
        raw_config = config_file.readlines()
    return raw_config


@pytest.fixture
def cisco_ios_simple_config():
    """Creares raw cisco config of comments etc."""
    with open(
        CISCO_IOS_SIMPLE_CONFIG_PATH, mode="r", errors="ignore", encoding="ascii"
    ) as config_file:
        raw_config = config_file.readlines()
    config = []
    for line in raw_config:
        line = line.rstrip()
        if line.startswith("!") is False:
            config.append(line)
    return config


@pytest.fixture
def cisco_ios_l3_simple_raw():
    """Cisco IOS L3 Interface with ip address, description and vlan."""
    raw_config = [
        "interface FastEthernet0/0.100",
        ' description "Test logical subinterface"',
        " encapsulation dot1Q 100",
        " ip address 10.1.1.1 255.255.255.252",
    ]
    return raw_config


@pytest.fixture
def cisco_ios_l3_simple_parsed():
    """Cisco IOS L3 Interface with ip address, description and vlan."""
    vlan = Vlan(id="100", encapsulation="dot1Q")
    ipv4 = IPv4(address="10.1.1.1", mask="255.255.255.252")
    interface = Interface(
        name="FastEthernet0/0.100",
        description='"Test logical subinterface"',
        vlans=[vlan],
        ipv4=[ipv4],
    )
    parsed_config = interface.dict()
    return parsed_config


@pytest.fixture
def cisco_ios_l3_vrf_raw():
    """Cisco IOS L3 Interface with ip address, vrf, description and vlan."""
    raw_config = [
        "interface FastEthernet0/0.200",
        ' description "Test logical subinterface 2"',
        " encapsulation dot1Q 200",
        " ip vrf forwarding VoIP",
        " ip address 10.2.2.10 255.255.255.0",
    ]
    return raw_config


@pytest.fixture
def cisco_ios_l3_vrf_parsed():
    """Cisco IOS L3 Interface with ip address, vrf, description and vlan."""
    vlan = Vlan(id="200", encapsulation="dot1Q")
    ipv4 = IPv4(address="10.2.2.10", mask="255.255.255.0")
    interface = Interface(
        name="FastEthernet0/0.200",
        description='"Test logical subinterface 2"',
        vlans=[vlan],
        ipv4=[ipv4],
        vrf="VoIP",
    )
    parsed_config = interface.dict()
    return parsed_config


@pytest.fixture
def cisco_ios_l3_acl_raw():
    """Cisco IOS L3 Interface with ip address, acl, description and vlan."""
    raw_config = [
        "interface FastEthernet0/0.300",
        ' description "Test logical subinterface 3"',
        " encapsulation dot1Q 300",
        " ip address 10.3.3.13 255.255.255.128",
        " ip access-group Common_Client_IN in",
        " ip access-group TEST_ACL_03 out",
    ]
    return raw_config


@pytest.fixture
def cisco_ios_l3_acl_parsed():
    """Cisco IOS L3 Interface with ip address, acl, description and vlan."""
    vlan = Vlan(id="300", encapsulation="dot1Q")
    ipv4 = IPv4(address="10.3.3.13", mask="255.255.255.128")
    acl_in = ACL(name="Common_Client_IN", direction="in")
    acl_out = ACL(name="TEST_ACL_03", direction="out")
    interface = Interface(
        name="FastEthernet0/0.300",
        description='"Test logical subinterface 3"',
        vlans=[vlan],
        ipv4=[ipv4],
        acl=[acl_in, acl_out],
    )
    parsed_config = interface.dict()
    return parsed_config


@pytest.fixture
def cisco_ios_l3_multiple_ipv4_raw():
    """Cisco IOS L3 Interface with multiple ip addresses, description and vlan."""
    raw_config = [
        "interface FastEthernet0/0.444",
        ' description "Test logical subinterface"',
        " encapsulation dot1Q 444",
        " ip address 10.4.4.1 255.255.255.252",
        " ip address 20.4.4.1 255.255.255.0 secondary",
        " ip address 30.4.4.1 255.255.0.0 secondary",
    ]
    return raw_config


@pytest.fixture
def cisco_ios_l3_multiple_ipv4_parsed():
    """Cisco IOS L3 Interface with multiple ip addresses, description and vlan."""
    vlan = Vlan(id="444", encapsulation="dot1Q")
    ipv4 = IPv4(address="10.4.4.1", mask="255.255.255.252")
    ipv4_sec1 = IPv4(address="20.4.4.1", mask="255.255.255.0", attr=["secondary"])
    ipv4_sec2 = IPv4(address="30.4.4.1", mask="255.255.0.0", attr=["secondary"])
    interface = Interface(
        name="FastEthernet0/0.444",
        description='"Test logical subinterface"',
        vlans=[vlan],
        ipv4=[ipv4, ipv4_sec1, ipv4_sec2],
    )
    parsed_config = interface.dict()
    return parsed_config


@pytest.fixture
def cisco_ios_l3_shutdown_raw():
    """Cisco IOS L3 Interface with ip address, description and vlan in shutdown."""
    raw_config = [
        "interface FastEthernet0/0.100",
        ' description "Test logical subinterface"',
        " encapsulation dot1Q 100",
        " ip address 10.1.1.1 255.255.255.252",
        " shutdown",
    ]
    return raw_config


@pytest.fixture
def cisco_ios_l3_shutdown_parsed():
    """Cisco IOS L3 Interface with ip address, description and vlan in shutdown."""
    vlan = Vlan(id="100", encapsulation="dot1Q")
    ipv4 = IPv4(address="10.1.1.1", mask="255.255.255.252")
    interface = Interface(
        name="FastEthernet0/0.100",
        description='"Test logical subinterface"',
        vlans=[vlan],
        ipv4=[ipv4],
        shutdown=True,
    )
    parsed_config = interface.dict()
    return parsed_config


@pytest.fixture
def cisco_ios_xconnect_simple_raw():
    """Cisco IOS L2 Interface with simple xconnect."""
    raw_config = [
        "interface GigabitEthernet2/2.555",
        ' description "Test logical subinterface with XC"',
        " encapsulation dot1Q 555",
        " xconnect 5.5.5.5 555001 encapsulation mpls",
    ]
    return raw_config


@pytest.fixture
def cisco_ios_xconnect_simple_parsed():
    """Cisco IOS L2 Interface with simple xconnect."""
    vlan = Vlan(id="555", encapsulation="dot1Q")
    xconnect = XConnect(neighbour="5.5.5.5", vcid=555001, encapsulation="mpls")
    interface = Interface(
        name="GigabitEthernet2/2.555",
        description='"Test logical subinterface with XC"',
        vlans=[vlan],
        xconnect=xconnect,
    )
    parsed_config = interface.dict()
    return parsed_config


@pytest.fixture
def cisco_ios_xconnect_mtu_raw():
    """Cisco IOS L2 Interface with xconnect and mtu."""
    raw_config = [
        "interface GigabitEthernet2/2.666",
        ' description "Test logical subinterface with XC an XC mtu"',
        " encapsulation dot1Q 666",
        " xconnect 6.6.6.6 666001 encapsulation mpls",
        "  mtu 1600",
    ]
    return raw_config


@pytest.fixture
def cisco_ios_xconnect_mtu_parsed():
    """Cisco IOS L2 Interface with xconnect and mtu."""
    vlan = Vlan(id="666", encapsulation="dot1Q")
    xconnect = XConnect(
        neighbour="6.6.6.6", vcid=666001, encapsulation="mpls", mtu=1600
    )
    interface = Interface(
        name="GigabitEthernet2/2.666",
        description='"Test logical subinterface with XC an XC mtu"',
        vlans=[vlan],
        xconnect=xconnect,
    )
    parsed_config = interface.dict()
    return parsed_config


@pytest.fixture
def cisco_ios_qinq_unpack_raw():
    """CISCO IOS Interface with QinQ."""
    raw_config = [
        "interface GigabitEthernet2/2.777",
        ' description "Test logical subinterface with QinQ"',
        " encapsulation dot1Q 1777 second-dot1q 2777",
    ]
    return raw_config


@pytest.fixture
def cisco_ios_qinq_unpack_parsed():
    """CISCO IOS Interface with QinQ."""
    vlan_1 = Vlan(id="1777", encapsulation="dot1Q")
    vlan_2 = Vlan(id="2777", encapsulation="dot1Q", secondary=True)
    interface = Interface(
        name="GigabitEthernet2/2.777",
        description='"Test logical subinterface with QinQ"',
        vlans=[vlan_1, vlan_2],
    )
    parsed_config = interface.dict()
    return parsed_config


@pytest.fixture
def config_file_absent():
    """Absent config file."""
    return pathlib.Path("tests/fixtures/nonexistant_config.yaml")


@pytest.fixture
def config_empty():
    """Empty config."""
    return {}


@pytest.fixture
def config_file_valid():
    """Valig config file."""
    return pathlib.Path("tests/fixtures/faddr_config_valid.yaml")


@pytest.fixture
def config_valid():
    """Valid config dictionary."""
    config = {
        "database": {
            "dir": "data/",
            "file": "faddr-db.json",
        },
        "rancid": {
            "dir": "tests/fixtures/rancid_dir/",
            "mapping": {
                "cisco-mf": "cisco_ios",
            },
        },
    }
    return config


@pytest.fixture
def config_file_invalid():
    """Broken yaml file."""
    return pathlib.Path("tests/fixtures/faddr_config_invalid.yaml")

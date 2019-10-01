import getpass
from netmiko import ConnectHandler

debug = False

palo = {
    'device_type': 'paloalto_panos',
    'host':   input("What's your firewall IP?"),
    'username': input("What's your user name?\n"),
    'password': getpass.getpass("What's your user password?\n")
}

print("Attempting To Connect")
net_connect = ConnectHandler(**palo)
print("Connection Success")

object_name = input("Name the address object(example: TEST-Interface): ")
object_address = input("Peer Endpoint Address(example: 162.33.22.23 ): ")
interface_id = input("Enter Interface ID(example: 150): ")

peer_local_address = input("Enter peer local address(example: 10.10.1.0/24): ")
pre_shared_key = input("Enter pre-shared key(example: myPassword123): ")

local_address = input("Enter your local address(example: 172.20.130.0/18): ")

commands = [
    'set address {} ip-netmask {}'.format(object_name, object_address),
    'set network interface tunnel units tunnel.{} ipv6 enabled no'.format(interface_id),
    'set network interface tunnel units tunnel.{} comment {}'.format(interface_id, object_name),
    'set network virtual-router default interface tunnel.{}'.format(interface_id),
    'set zone trust network layer3 tunnel.{}'.format(interface_id),
    'set network virtual-router default routing-table ip static-route {} destination {} interface tunnel.{}'.format(object_name, peer_local_address, interface_id),
    'set network ike crypto-profiles ike-crypto-profiles {} dh-group group2 encryption 3des hash sha1 lifetime seconds 28800'.format(object_name),
    'set network ike crypto-profiles ipsec-crypto-profiles {} dh-group no-pfs lifetime seconds 28800'.format(object_name),
    'set network ike crypto-profiles ipsec-crypto-profiles {} esp authentication sha1 encryption aes-256-cbc'.format(object_name),
    'set network ike gateway {} authentication pre-shared-key key {}'.format(object_name, pre_shared_key),
    'set network ike gateway {} local-address interface ethernet1/1 ip ATT_Subnet'.format(object_name),
    'set network ike gateway {} peer-address ip {}'.format(object_name, object_name),
    'set network ike gateway {} protocol ikev1 exchange-mode main'.format(object_name),
    'set network ike gateway {} protocol ikev1 ike-crypto-profile {}'.format(object_name, object_name),
    'set network tunnel ipsec {} tunnel-interface tunnel.{} auto-key ike-gateway {}'.format(object_name, interface_id, object_name),
    'set network tunnel ipsec {} tunnel-interface tunnel.{} auto-key ipsec-crypto-profile {} proxy-id Entry1 local {} remote {}'.format(object_name, interface_id, object_name, local_address, peer_local_address)
]

output = []
total_commands = len(commands)
for index, command in enumerate(commands):
    print("Running Command {} of {} : \n {} \n".format(index, total_commands-1, command))
    result = net_connect.send_config_set(config_commands=command, delay_factor=0)
    search_result = result.find("Invalid syntax")
    if search_result == -1:
        print("SUCCESS\n")
    else:
        print("FAILURE\n")

    output.append(result)

if debug:
    print(output)
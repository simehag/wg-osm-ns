from charmhelpers.core.hookenv import (
    action_get,
    action_fail,
    action_set,
    status_set,
)
from charms.reactive import (
    clear_flag,
    set_flag,
    when,
    when_not,
)
import charms.sshproxy

@when('sshproxy.configured')
@when_not('simple.installed')
def install_simple_proxy_charm():
    set_flag('simple.installed')
    status_set('active', 'Ready!')

@when('actions.touch')
def touch():
    err = ''
    try:
        filename = action_get('filename')
        cmd = ['touch {}'.format(filename)]
        result, err = charms.sshproxy._run(cmd)
        cmd = ['sudo sysctl -w net.ipv4.ip_forward=1']
        result, err = charms.sshproxy._run(cmd)
        cmd = ['sudo sysctl -w net.ipv4.conf.all.proxy_arp=1']
        result, err = charms.sshproxy._run(cmd)
        cmd = ['sudo ip link set ens4 up']
        result, err = charms.sshproxy._run(cmd)
        cmd = ['sudo ip link set ens5 up']
        result, err = charms.sshproxy._run(cmd)
        cmd = ['sudo netplan apply']
        result, err = charms.sshproxy._run(cmd)
    except:
        action_fail('command failed:' + err)
    else:
        action_set({'outout': result})
    finally:
        clear_flag('actions.touch')

@when('actions.generate-keys')
def generate_keys():
    err = ''
    try:
        cmd = ['wg genkey | sudo tee /etc/wireguard/privatekey | wg pubkey | sudo tee /etc/wireguard/publickey']
        result, err = charms.sshproxy._run(cmd)
    except:
        action_fail('command failed:' + err)
    else:
        action_set({'outout': result})
    finally:
        clear_flag('actions.generate-keys')

@when('actions.generate-config')
def generate_config():
    err = ''
    try:
        gateway_ip = action_get('gateway-ip')
        cmd = ['echo -e "[Interface]\nAddress = {}\nListenPort = 51820\nPrivatekey = $(sudo cat /etc/wireguard/privatekey)" | sudo tee /etc/wireguard/wg0.conf'.format(gateway_ip)]
        result, err = charms.sshproxy._run(cmd)
    except:
        action_fail('command failed:' + err)
    else:
        action_set({'outout': result})
    finally:
        clear_flag('actions.generate-config')

@when('actions.wireguard-up')
def wireguard_up():
    err = ''
    try:
        cmd = ['sudo wg-quick up wg0']
        result, err = charms.sshproxy._run(cmd)
    except:
        action_fail('command failed:' + err)
    else:
        action_set({'outout': result})
    finally:
        clear_flag('actions.wireguard-up')


@when('actions.add-peer')
def add_peer():
    err = ''
    try:
        peer_public_key = action_get('peer-publickey')
        gateway_ip = action_get('gateway-ip')
        subnet_behind_tunnel = action_get('subnet-behind-tunnel')
        public_endpoint = action_get('public-endpoint')
        cmd = ['sudo wg set wg0 peer {} allowed-ips {},{} endpoint {}:51820 persistent-keepalive 25'.format(peer_public_key, gateway_ip,subnet_behind_tunnel, public_endpoint)]
        result, err = charms.sshproxy._run(cmd)
        cmd = ['sudo ip -4 route add {} dev wg0'.format(gateway_ip)]
        result, err = charms.sshproxy._run(cmd)
        cmd = ['sudo ip -4 route add {} dev wg0'.format(subnet_behind_tunnel)]
        result, err = charms.sshproxy._run(cmd)
        cmd = ['sudo wg-quick save wg0']
        result, err = charms.sshproxy._run(cmd)
    except:
        action_fail('command failed:' + err)
    else:
        action_set({'outout': result})
    finally:
        clear_flag('actions.add-peer')

@when('actions.del-peer')
def del_peer():
    err = ''
    try:
        peer_public_key = action_get('peer-publickey')
        subnet_behind_tunnel = action_get('subnet-behind-tunnel')
        cmd = ['sudo wg set wg0 peer {} remove'.format(peer_public_key)]
        result, err = charms.sshproxy._run(cmd)
        cmd = ['sudo ip -4 route del {} dev wg0'.format(subnet_behind_tunnel)]
        result, err = charms.sshproxy._run(cmd)
        cmd = ['sudo wg-quick save wg0']
        result, err = charms.sshproxy._run(cmd)
    except:
        action_fail('command failed:' + err)
    else:
        action_set({'outout': result})
    finally:
        clear_flag('actions.del-peer')

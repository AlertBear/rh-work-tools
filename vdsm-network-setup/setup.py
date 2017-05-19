#!/usr/bin/python2.7


import os
import sys
import subprocess
import tempfile
from sysinfo import NETWORK_SYS


ABSPATH = os.path.abspath(sys.argv[0])
ABSPATH = os.path.dirname(ABSPATH) + "/"


def execute(cmd, check=False):
    print "Executing [%s]..." % cmd
    try:
        out = subprocess.check_output(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        if check:
            raise e
        else:
            return e.output
    else:
        return out


def update_kv(file, kv):
    for k, v in kv.items():
        cmd = "sed -i 's/{key}=.*/{key}=\"{value}\"/' {file}".format(
            key=k, value=v, file=file)
        execute(cmd)


def avoid_disc():
    # Add the route to avoid the disconnection from remote server
    # Firstly, get the default gateway
    cmd = "ip route list|grep default"
    output = execute(cmd)
    s, tmpfile = tempfile.mkstemp()
    with open(tmpfile, 'w') as f:
        f.write(output)
    cmd = "sed -n '/^default/p' %s" % tmpfile
    output = execute(cmd)
    pub_gw = output.split()[2]

    # Add a route to avoid the disconnection by "ifup bridge"
    cmd = "ip route add 10.0.0.0/8 via %s" % pub_gw
    execute(cmd)
    return pub_gw


def delete_vlan_gw(vlan):
    # Delete the vlan gateway
    cmd = "ip route list|grep default|grep %s" % vlan
    output = execute(cmd)

    vlan_gw = output.split()[2]
    cmd = "ip route del default via %s" % vlan_gw
    execute(cmd)


def restore_pub_gw(pub_gw):
    # Add the original gateway
    cmd = "ip route add default via %s" % pub_gw
    execute(cmd)

    # Delete the added route after the default was added
    cmd = "ip route del 10.0.0.0/8"
    execute(cmd)


def setup_bond(bond_name, slave1, slave2):
    # Find the ifcfg files templates
    tpl_dir = ABSPATH + "tpls/"
    tpl_path = tpl_dir + "bond"

    # Copy the templates to the tmp dir
    tmp_tpl_dir = "/tmp/vdsm-network-setup/bond/"
    if not os.path.exists(tmp_tpl_dir):
        os.makedirs(tmp_tpl_dir)
    else:
        cmd = "rm -f %sifcfg-*" % tmp_tpl_dir
        execute(cmd)

    #shutil.copytree(tpl_path, tmp_dir)
    cmd = "cp -f %s/ifcfg-* %s" % (tpl_path, tmp_tpl_dir)
    execute(cmd)

    # Get the mac address of slaves
    cmd = "ip link show %s|grep 'link/ether'" % slave1
    output = execute(cmd)
    slave1_mac = output.split()[1]
    cmd = "ip link show %s|grep 'link/ether'" % slave2
    output = execute(cmd)
    slave2_mac = output.split()[1]

    # Rename the template according to the actual variables
    bond_cfg_file = tmp_tpl_dir + "ifcfg-bond0"
    slave1_cfg_file = tmp_tpl_dir + "ifcfg-slave1"
    slave2_cfg_file = tmp_tpl_dir + "ifcfg-slave2"
    nbond_cfg_file = tmp_tpl_dir + "ifcfg-%s" % bond_name
    nslave1_cfg_file = tmp_tpl_dir + "ifcfg-%s" % slave1
    nslave2_cfg_file = tmp_tpl_dir + "ifcfg-%s" % slave2
    os.rename(bond_cfg_file, nbond_cfg_file)
    os.rename(slave1_cfg_file, nslave1_cfg_file)
    os.rename(slave2_cfg_file, nslave2_cfg_file)

    # Update the templates
    bond_cfg_kv = {"DEVICE": bond_name}
    update_kv(nbond_cfg_file, bond_cfg_kv)

    slave1_cfg_kv = {
        "DEVICE": slave1, "HWADDR": slave1_mac, "MASTER": bond_name}
    update_kv(nslave1_cfg_file, slave1_cfg_kv)

    slave2_cfg_kv = {
        "DEVICE": slave2, "HWADDR": slave2_mac, "MASTER": bond_name}
    update_kv(nslave2_cfg_file, slave2_cfg_kv)

    # Move the files to /etc/sysconfig/network-scripts
    network_scripts_dir = "/etc/sysconfig/network-scripts/"
    if os.path.isfile(network_scripts_dir + "ifcfg-%s" % slave1):
        os.rename(
            network_scripts_dir + "ifcfg-%s" % slave1,
            network_scripts_dir + "ifcfg-%s.bak" % slave1)
    if os.path.isfile(network_scripts_dir + "ifcfg-%s" % slave2):
        os.rename(
            network_scripts_dir + "ifcfg-%s" % slave2,
            network_scripts_dir + "ifcfg-%s.bak" % slave2)
    cmd = "mv %sifcfg-* %s" % (tmp_tpl_dir, network_scripts_dir)
    execute(cmd)

    # Restart the service
    cmd = "service network restart"
    execute(cmd)

    # Show all the ip
    cmd = "ip a s"
    print execute(cmd)


def setup_vlan(vlan_device, vlan_id):
    # Find the ifcfg files templates
    tpl_dir = ABSPATH + "tpls/"
    tpl_path = tpl_dir + "vlan"

    # Copy the templates to the tmp dir
    tmp_tpl_dir = "/tmp/vdsm-network-setup/vlan/"
    if not os.path.exists(tmp_tpl_dir):
        os.makedirs(tmp_tpl_dir)
    else:
        cmd = "rm -f %sifcfg-*" % tmp_tpl_dir
        execute(cmd)

    # shutil.copytree(tpl_path, tmp_dir)
    cmd = "cp -f %s/ifcfg-* %s" % (tpl_path, tmp_tpl_dir)
    execute(cmd)

    # Get the mac address of slaves
    cmd = "ip link show %s|grep 'link/ether'" % vlan_device
    output = execute(cmd)
    nic_mac = output.split()[1]

    # Rename the template according to the actual variables
    nic_cfg_file = tmp_tpl_dir + "ifcfg-nic1"
    vlan_cfg_file = tmp_tpl_dir + "ifcfg-nic1.00"
    dnic_cfg_file = tmp_tpl_dir + "ifcfg-%s" % vlan_device
    dvlan_cfg_file = tmp_tpl_dir + "ifcfg-%s.%s" % (vlan_device, vlan_id)
    os.rename(nic_cfg_file, dnic_cfg_file)
    os.rename(vlan_cfg_file, dvlan_cfg_file)

    # Update the templates
    nic_cfg_kv = {"DEVICE": vlan_device, "HWADDR": nic_mac}
    update_kv(dnic_cfg_file, nic_cfg_kv)

    vlan_cfg_kv = {"DEVICE": vlan_device + ".%s" % vlan_id}
    update_kv(dvlan_cfg_file, vlan_cfg_kv)

    # Move the files to /etc/sysconfig/network-scripts
    network_scripts_dir = "/etc/sysconfig/network-scripts/"
    if os.path.isfile(network_scripts_dir + "ifcfg-%s" % vlan_device):
        os.rename(
            network_scripts_dir + "ifcfg-%s" % vlan_device,
            network_scripts_dir + "ifcfg-%s.bak" % vlan_device)
    cmd = "mv %sifcfg-* %s" % (tmp_tpl_dir, network_scripts_dir)
    execute(cmd)

    # Add a gateway to avoid the disconnection by following step
    pub_gateway = avoid_disc()

    # Bring up the vlan ip, may create the internal default gateway
    vlan = vlan_device + '.' + vlan_id
    cmd = "ifup %s" % vlan
    execute(cmd)

    # Delete the internal vlan gateway such as "192.168.xx.1"
    delete_vlan_gw(vlan)

    # Restore the pub gateway
    restore_pub_gw(pub_gateway)

    # Show all the ip
    cmd = "ip a s"
    print execute(cmd)


def setup_bv(bond_name, slave1, slave2, vlan_id):
    # Find the ifcfg files templates
    tpl_dir = ABSPATH + "tpls/"
    tpl_path = tpl_dir + "bv"

    # Copy the templates to the tmp dir
    tmp_tpl_dir = "/tmp/vdsm-network-setup/bv/"
    if not os.path.exists(tmp_tpl_dir):
        os.makedirs(tmp_tpl_dir)
    else:
        cmd = "rm -f %sifcfg-*" % tmp_tpl_dir
        execute(cmd)
    # shutil.copytree(tpl_path, tmp_dir)
    cmd = "cp -f %s/ifcfg-* %s" % (tpl_path, tmp_tpl_dir)
    execute(cmd)

    # Get the mac address of slaves
    cmd = "ip link show %s|grep 'link/ether'" % slave1
    output = execute(cmd)
    slave1_mac = output.split()[1]
    cmd = "ip link show %s|grep 'link/ether'" % slave2
    output = execute(cmd)
    slave2_mac = output.split()[1]

    # Rename the template according to the actual variables
    bond_cfg_file = tmp_tpl_dir + "ifcfg-bond1"
    slave1_cfg_file = tmp_tpl_dir + "ifcfg-slave1"
    slave2_cfg_file = tmp_tpl_dir + "ifcfg-slave2"
    vlan_cfg_file = tmp_tpl_dir + "ifcfg-bond1.00"
    dbond_cfg_file = tmp_tpl_dir + "ifcfg-%s" % bond_name
    dslave1_cfg_file = tmp_tpl_dir + "ifcfg-%s" % slave1
    dslave2_cfg_file = tmp_tpl_dir + "ifcfg-%s" % slave2
    dvlan_cfg_file = tmp_tpl_dir + "ifcfg-%s.%s" % (bond_name, vlan_id)
    os.rename(bond_cfg_file, dbond_cfg_file)
    os.rename(slave1_cfg_file, dslave1_cfg_file)
    os.rename(slave2_cfg_file, dslave2_cfg_file)
    os.rename(vlan_cfg_file, dvlan_cfg_file)

    # Update the templates
    bond_cfg_kv = {"DEVICE": bond_name}
    update_kv(bond_cfg_file, bond_cfg_kv)

    slave1_cfg_kv = {
        "DEVICE": slave1, "HWADDR": slave1_mac, "MASTER": bond_name}
    update_kv(slave1_cfg_file, slave1_cfg_kv)

    slave2_cfg_kv = {
        "DEVICE": slave2, "HWADDR": slave2_mac, "MASTER": bond_name}
    update_kv(slave2_cfg_file, slave2_cfg_kv)

    vlan_cfg_kv = {"DEVICE": vlan_device + ".%s" % vlan_id}
    update_kv(vlan_cfg_file, vlan_cfg_kv)

    # Move the files to /etc/sysconfig/network-scripts
    network_scripts_dir = "/etc/sysconfig/network-scripts/"
    if os.path.isfile(network_scripts_dir + "ifcfg-%s" % slave1):
        os.rename(
            network_scripts_dir + "ifcfg-%s" % slave1,
            network_scripts_dir + "ifcfg-%s.bak" % slave1)
    if os.path.isfile(network_scripts_dir + "ifcfg-%s" % slave2):
        os.rename(
            network_scripts_dir + "ifcfg-%s" % slave2,
            network_scripts_dir + "ifcfg-%s.bak" % slave2)
    cmd = "mv %sifcfg-* %s" % (tmp_tpl_dir, network_scripts_dir)
    execute(cmd)

    # Add a gateway to avoid the disconnection by following step
    pub_gateway = avoid_disc()

    # Bring up the vlan ip, may create the internal default gateway
    bv = bond_name + '.' + vlan_id
    cmd = "ifup %s" % bv
    execute(cmd)

    # Delete the internal vlan gateway such as "192.168.xx.1"
    delete_vlan_gw(bv)

    # Restore the pub gateway
    restore_pub_gw(pub_gateway)

    # Show all the ip
    cmd = "ip a s"
    print execute(cmd)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "ERROR: Append correct parameter, such as \"python %s bond\"" % sys.argv[0]
        sys.exit(1)

    network_mode = sys.argv[1]
    if network_mode not in ["bond", "vlan", "bv"]:
        print "ERROR: Please fill [bond, vlan, bv] as the second parameter"
        sys.exit(1)

    if len(sys.argv) < 3:
        cmd = "hostname"
        output = execute(cmd)
        machine_used = output.strip()
    elif len(sys.argv) == 3:
        machine_used = sys.argv[2]

    if machine_used not in NETWORK_SYS.keys():
        print "ERROR: Hostname [%s] not in record, please see the detail\
        of sysinfo.py and specify the machine as the second parameter follow\
        this script" % machine_used
        sys.exit(1)

    if network_mode == "bond":
        bond_name = "bond0"
        slave1 = NETWORK_SYS[machine_used]["bond"]["slaves"][0]
        slave2 = NETWORK_SYS[machine_used]["bond"]["slaves"][1]
        setup_bond(bond_name, slave1, slave2)
    elif network_mode == "vlan":
        vlan_id = NETWORK_SYS[machine_used]["vlan"]["id"]
        vlan_device = NETWORK_SYS[machine_used]["vlan"]["nics"][0]
        setup_vlan(vlan_device, vlan_id)
    elif network_mode == "bv":
        bond_name = "bond1"
        vlan_id = NETWORK_SYS[machine_used]["vlan"]["id"]
        slave1 = NETWORK_SYS[machine_used]["vlan"]["nics"][0]
        slave2 = NETWORK_SYS[machine_used]["vlan"]["nics"][1]
        setup_bv(bond_name, slave1, slave2, vlan_id)

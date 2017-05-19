# !/usr/bin/python2.7


import os
import sys
import shutil
import subprocess
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
        cmd = "sed -i 's/{key}=.*/=\"{value}\"/' {file}".format(
            key=k, value=v, file=file)
        execute(cmd)


def setup_bond(bond_name, slave1, slave2):
    # Find the ifcfg files templates
    tpl_dir = ABSPATH + "tpls/"
    tpl_path = tpl_dir + "bond"

    # Copy the templates to the tmp dir
    tmp_dir = "/tmp/vdsm-network-setup"
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    shutil.copytree(tpl_path, tmp_dir)

    tmp_tpl_dir = tmp_dir + "/bond"
    bond_cfg_file = tmp_tpl_dir + "ifcfg-bond0"
    slave1_cfg_file = tmp_tpl_dir + "ifcfg-slave1"
    slave2_cfg_file = tmp_tpl_dir + "ifcfg-slave2"

    # Get the mac address of slaves
    cmd = "ip link show %s|grep 'link/ether'" % slave1
    output = execute(cmd)
    slave1_mac = output.split(1)
    cmd = "ip link show %s|grep 'link/ether'" % slave2
    output = execute(cmd)
    slave2_mac = output.split(1)

    # Rename the template according to the actual variables
    os.rename(bond_cfg_file, tmp_tpl_dir + "ifcfg-%s" % bond_name)
    os.rename(slave1_cfg_file, tmp_tpl_dir + "ifcfg-%s" % slave1)
    os.rename(slave2_cfg_file, tmp_tpl_dir + "ifcfg-%s" % slave2)

    # Update the templates
    bond_cfg_kv = {"DEVICE": bond_name}
    update_kv(bond_cfg_kv, bond_cfg_file)

    slave1_cfg_kv = {
        "DEVICE": slave1, "HWADDR": slave1_mac, "MASTER": bond_name}
    update_kv(slave1_cfg_kv, slave1_cfg_file)

    slave2_cfg_kv = {
        "DEVICE": slave2, "HWADDR": slave2_mac, "MASTER": bond_name}
    update_kv(slave2_cfg_kv, slave2_cfg_file)

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
    cmd = "mv %s/ifcfg-* %s/" % (tmp_tpl_dir, network_scripts_dir)
    execute(cmd)

    # Restart network service
    cmd = "ll %s" % network_scripts_dir
    print execute(cmd)


def setup_vlan(vlan_device, vlan_id):
    # Find the ifcfg files templates
    tpl_dir = ABSPATH + "tpls/"
    tpl_path = tpl_dir + "vlan"

    # Copy the templates to the tmp dir
    tmp_dir = "/tmp/vdsm-network-setup"
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    shutil.copytree(tpl_path, tmp_dir)

    tmp_tpl_dir = tmp_dir + "/vlan"
    nic_cfg_file = tmp_tpl_dir + "ifcfg-nic1"
    vlan_cfg_file = tmp_tpl_dir + "ifcfg-nic1.00"

    # Get the mac address of slaves
    cmd = "ip link show %s|grep 'link/ether'" % vlan_device
    output = execute(cmd)
    nic_mac = output.split(1)

    # Rename the template according to the actual variables
    os.rename(nic_cfg_file, tmp_tpl_dir + "ifcfg-%s" % vlan_device)
    os.rename(vlan_cfg_file, tmp_tpl_dir + "ifcfg-%s.%s" % (
        vlan_device, vlan_id))

    # Update the templates
    nic_cfg_kv = {"DEVICE": vlan_device, "HWADDR": nic_mac}
    update_kv(nic_cfg_kv, nic_cfg_file)

    vlan_cfg_kv = {"DEVICE": vlan_device + ".%s" % vlan_id}
    update_kv(vlan_cfg_kv, vlan_cfg_file)

    # Move the files to /etc/sysconfig/network-scripts
    network_scripts_dir = "/etc/sysconfig/network-scripts/"
    if os.path.isfile(network_scripts_dir + "ifcfg-%s" % vlan_device):
        os.rename(
            network_scripts_dir + "ifcfg-%s" % slave1,
            network_scripts_dir + "ifcfg-%s.bak" % slave1)
    cmd = "mv %s/ifcfg-* %s/" % (tmp_tpl_dir, network_scripts_dir)
    execute(cmd)

    # Restart network service
    cmd = "ll %s" % network_scripts_dir
    print execute(cmd)


def setup_bv(bond_name, slave1, slave2, vlan_id):
    # Find the ifcfg files templates
    tpl_dir = ABSPATH + "tpls/"
    tpl_path = tpl_dir + "bv"

    # Copy the templates to the tmp dir
    tmp_dir = "/tmp/vdsm-network-setup"
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    shutil.copytree(tpl_path, tmp_dir)

    tmp_tpl_dir = tmp_dir + "/bv"
    bond_cfg_file = tmp_tpl_dir + "ifcfg-bond1"
    slave1_cfg_file = tmp_tpl_dir + "ifcfg-slave1"
    slave2_cfg_file = tmp_tpl_dir + "ifcfg-slave2"
    vlan_cfg_file = tmp_tpl_dir + "ifcfg-bond1.00"

    # Get the mac address of slaves
    cmd = "ip link show %s|grep 'link/ether'" % slave1
    output = execute(cmd)
    slave1_mac = output.split(1)
    cmd = "ip link show %s|grep 'link/ether'" % slave2
    output = execute(cmd)
    slave2_mac = output.split(1)

    # Rename the template according to the actual variables
    os.rename(bond_cfg_file, tmp_tpl_dir + "ifcfg-%s" % bond_name)
    os.rename(slave1_cfg_file, tmp_tpl_dir + "ifcfg-%s" % slave1)
    os.rename(slave2_cfg_file, tmp_tpl_dir + "ifcfg-%s" % slave2)
    os.rename(vlan_cfg_file, tmp_tpl_dir + "ifcfg-%s.%s" % (bond_name, vlan_id))

    # Update the templates
    bond_cfg_kv = {"DEVICE": bond_name}
    update_kv(bond_cfg_kv, bond_cfg_file)

    slave1_cfg_kv = {
        "DEVICE": slave1, "HWADDR": slave1_mac, "MASTER": bond_name}
    update_kv(slave1_cfg_kv, slave1_cfg_file)

    slave2_cfg_kv = {
        "DEVICE": slave2, "HWADDR": slave2_mac, "MASTER": bond_name}
    update_kv(slave2_cfg_kv, slave2_cfg_file)

    vlan_cfg_kv = {"DEVICE": vlan_device + ".%s" % vlan_id}
    update_kv(vlan_cfg_kv, vlan_cfg_file)

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
    cmd = "mv %s/ifcfg-* %s/" % (tmp_tpl_dir, network_scripts_dir)
    execute(cmd)

    # Restart network service
    cmd = "ll %s" % network_scripts_dir
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
        machine_used = output
    elif len(sys.argv) == 3:
        machine_used = sys.argv[2]

    if machine_used not in NETWORK_SYS.keys():
        print "ERROR: Hostname [%s] not in record, \
            please see the detail of sysinfo.py \
            and specify the machine as the second\
            parameter follow this script" % machine_used
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

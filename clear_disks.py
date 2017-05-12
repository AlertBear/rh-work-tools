#!/usr/bin/python

import re
import subprocess


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


if __name__ == "__main__":
    # Get all the PVs and VGs
    cmd = "pvs|grep -v 'PV'|awk '{print $1}'"
    output = execute(cmd)
    pvs = output.split()

    # Get all the VGs
    cmd = "pvs|grep -v 'PV'|awk '{print $2}'"
    output = execute(cmd)
    vgs = output.split()

    # Get the partitions if exists and delete
    for pv in pvs:
        if re.search('/dev/sd\w.*', pv):
            pv_blk_name = pv.lstrip('/dev/')
        elif re.search('/dev/mapper/.*', pv):
            pv_blk_name = pv.lstrip('/dev/mapper/')

        cmd = "lsblk -l %s|grep '%s '" % (pv, pv_blk_name)
        output = execute(cmd)
        pv_blk_type = output.split()[5]
        if re.search('part', pv_blk_type):
            pv_prefix = pv.rstrip(pv_blk_name)
            # Get the related disk and all the parts
            if re.search('.*p[0-9]$', pv_blk_name):
                # format like 36005076300810b3e0000000000000267p2
                map_disk = pv[:-2]
                map_disk_blk_name = pv_blk_name[:-2]
            elif re.search('^sd\w\d+', pv_blk_name):
                # format like sda3
                map_disk = pv[:-1]
                map_disk_blk_name = pv_blk_name[:-1]

            # Get all the parts on map disk
            cmd = "lsblk -l %s|grep %s|awk '{print $1}'" % (
                map_disk, map_disk_blk_name)
            output = execute(cmd)
            pv_related_blk_names = output.split()
            # Delete disks and parts
            for pv_related_blk_name in pv_related_blk_names:
                pv_related_dp_name = pv_prefix + pv_related_blk_name
                cmd = "dd if=/dev/zero of=%s bs=50M count=10" % pv_related_dp_name
                execute(cmd)
        cmd = "dd if=/dev/zero of=%s bs=50M count=10" % pv
        execute(cmd)

    # Delete all the floating lvm under the destroyed vgs
    # since pv had been deleted above
    for vg in vgs:
        cmd = "dmsetup remove /dev/%s/*" % vg
        execute(cmd)

    # Also there might be some floating lvm after above steps
    float_vgs = []
    cmd = "lsblk -l|grep lvm|awk '{print $1}'"
    output = execute(cmd)
    lvms = output.split()
    for lvm in lvms:
        new_lvm = lvm.replace("--", "##")
        lvm_prefix = new_lvm.split('-')[0]
        vg = lvm_prefix.replace("##", "-")
        float_vgs.append(vg)

    float_vgs = list(set(float_vgs))
    cmd = "dmsetup remove /dev/%s/*" % vg
    execute(cmd)

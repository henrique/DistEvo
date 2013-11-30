#!/usr/bin/env python2.7

import os, sys
import re
import time
import struct
import socket

from libcloud.compute.types import Provider as ComputeProvider
from libcloud.compute.providers import get_driver as get_compute_driver

CRED_FILE = "tobias.klauser.cred"
KEYNAME = 'lsci2012_alheto'
EC2_IMAGE_ID = 'ami-b527a6dc'
EC2_SIZE_ID = 'm1.xlarge'
EC2_LOCATION_ID = '0'
EC2_USERDATA_FILE = 'lsci-fp-userdata'
PUBKEY_FILE = '/Users/tklauser/.ssh/id_rsa.pub'

# source: http://stackoverflow.com/a/8339939
def is_public_ip(lookup):
    f = struct.unpack('!I', socket.inet_pton(socket.AF_INET, lookup))[0]
    private = ([ 2130706432 , 4278190080 ],
               [ 3232235520 , 4294901760 ],
               [ 2886729728 , 4293918720 ],
               [ 167772160 , 4278190080 ])
    for net in private:
        if (f & net[1] == net[0]):
            return False
    return True

def fp_ec2_create_vms(n_nodes,
                      cred_file=CRED_FILE,
                      keyname=KEYNAME,
                      ec2_image_id=EC2_IMAGE_ID,
                      ec2_size_id=EC2_SIZE_ID,
                      ec2_location_id=EC2_LOCATION_ID,
                      ec2_userdata_file=EC2_USERDATA_FILE,
                      pubkey_file=PUBKEY_FILE):
     # set to None to load values from cred_file
    AWSAccessKey = None
    AWSSecretKey = None

    f = open(cred_file, "r")
    for line in f:
        m = re.match(r"^(\w+)='(\w+)'$", line)
        if m.group(1) == 'AccessKeyId' and AWSAccessKey is None:
            AWSAccessKey = m.group(2)
        elif m.group(1) == 'SecretAccessKey' and AWSSecretKey is None:
            AWSSecretKey = m.group(2)
    f.close()

    if AWSAccessKey is None or AWSSecretKey is None:
        print "Failed to read AWS credentials from " + cred_file
        return None

    if not os.path.exists(ec2_userdata_file):
        print "Userdata file %s not found" % ec2_userdata_file
        return None

    # Amazon EC2
    ec2_driver = get_compute_driver(ComputeProvider.EC2)
    ec2_compute = ec2_driver(AWSAccessKey, AWSSecretKey, secure=False)

    ec2_images = ec2_compute.list_images()
    ec2_nodes = ec2_compute.list_nodes()
    ec2_sizes = ec2_compute.list_sizes()
    ec2_locations = ec2_compute.list_locations()

    print "[EC2] loaded %d images, %d nodes, %d sizes, %d locations" % (len(ec2_images), len(ec2_nodes), len(ec2_sizes), len(ec2_locations))

    try:
        ec2_compute.ex_import_keypair(keyname, pubkey_file)
        ec2_compute.ex_describe_keypairs(keyname)
    except:
        pass # if the keypair already exists, just leave it

    # Select NodeImage to start
    ec2_image = None
    for img in ec2_images:
        if img.id == ec2_image_id:
            ec2_image = img
            break

    if ec2_image is None:
        print "[EC2] Couldn't find image with ID " + ec2_image_id
        sys.exit(-1)

    ec2_size = None
    for sz in ec2_sizes:
        if sz.id == ec2_size_id:
            ec2_size = sz
            break

    if ec2_size is None:
        print "[EC2] Couldn't find size with ID " + ec2_size_id
        sys.exit(-1)

    ec2_location = None
    for loc in ec2_locations:
        if loc.id == ec2_location_id:
            ec2_location = loc
            break

    if ec2_location is None:
        print "[EC2] Couldn't find location"# + ec2_location_name
        sys.exit(-1)

    ips = []
    nodes = []

    ud = open(ec2_userdata_file, 'r').read()

    print "[EC2] Starting %d nodes..." % n_nodes
    for i in range(0, n_nodes):
        ec2_node = ec2_compute.create_node(name='lsci2012', image=ec2_image,
                                           size=ec2_size,location=ec2_location,
                                           ex_keyname=keyname,
                                           ex_securitygroup='lsci2012',
                                           ex_userdata=ud)

        # wait until nodes are running
        print "[EC2] Waiting for node %d to become available..." % i
        ec2_running = False
        while not ec2_running:
            for node in ec2_compute.list_nodes():
                if node.extra['keyname'] == keyname:
                    if node.state == 0 and len(node.public_ips) > 0 and not node.public_ips[0] in ips:
                        ec2_node = node
                        ips.append(ec2_node.public_ips[0])
                        nodes.append(node)
                        ec2_running = True
                        break
            if not ec2_running:
                time.sleep(2)

        print "[EC2] Node {0} with IP {1} running".format(i, ec2_node.public_ips[0])

    return nodes

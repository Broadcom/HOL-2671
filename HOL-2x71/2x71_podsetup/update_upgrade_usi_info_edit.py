#!/usr/bin/python3
############################################################################
# ========================================================================
# Copyright 2023 VMware, Inc. All rights reserved. VMware Confidential
# ========================================================================
###

#pylint:  skip-file
import sys, os, django
import logging
from avi.infrastructure.avi_logging import get_root_logger
from avi.infrastructure.db_transaction import db_transaction
sys.path.append("/opt/avi/python/bin/portal")
os.environ["DJANGO_SETTINGS_MODULE"] = "portal.settings_full"
django.setup()


import argparse, copy, traceback
from api.models import Image
from avi.util.cluster_info import cluster_uuid
from avi.infrastructure.datastore import Datastore
from avi.rest.pb2model import protobuf2model
import avi.protobuf.upgrade_pb2 as upgrade_pb
from avi.protobuf import options_pb2
from avi.upgrade.upgrade_utils import notif_upgrade_status_info, clear_upgrade_status_info_fields

UPGRADE_LOG = '/var/lib/avi/log/update_upgrade_usi_info.log'
log = get_root_logger(__name__, UPGRADE_LOG, logging.INFO)

def print_and_log(msg):
    ''' Output is printed in console and logs are generated'''
    print(msg)
    log.info(msg)

def get_image_info_from_uuid(image_uuid):
    ''' Return image info for given image uuid '''
    try:
        image_pb = Image.objects.get(uuid = image_uuid).protobuf()
    except Exception as e:
        err_msg = 'Invalid image uuid:%s \n exception:%s' % (image_uuid, str(e))
        print(err_msg)
        logging.error(err_msg)
        logging.exception(e)
        raise e
    return image_pb

def update_upgrade_usi_info(args):
    """
    Clean up stale upgrade status info
    """
    try:
        ds = Datastore()
        if args.upgrade_usi_uuid:
            upgrade_usi_uuid = args.upgrade_usi_uuid
        else:
            upgrade_usi_uuid = str(cluster_uuid())
        usi_obj = ds.get('upgradestatusinfo', upgrade_usi_uuid)
        print_and_log('***Current UpgradeStatusInfo for controller *** \n%s' % str(usi_obj['config']))
        if not usi_obj:
            print_and_log("Invalid UpgradeStatusInfo with uuid: %s" % upgrade_usi_uuid)
        usinfo = copy.deepcopy(usi_obj['config'])
        usinfo.state.state = options_pb2.UPGRADE_FSM_COMPLETED
        # Update Upgrade Operation
        usinfo.upgrade_ops = upgrade_pb.UPGRADE
        if args.upgrade_ops:
            if args.upgrade_ops == 'rollback':
                usinfo.upgrade_ops = upgrade_pb.ROLLBACK
            elif args.upgrade_ops == 'patch':
                usinfo.upgrade_ops = upgrade_pb.PATCH
            elif args.upgrade_ops == 'rollbackpatch':
                usinfo.upgrade_ops = upgrade_pb.ROLLBACKPATCH
        # Update version, image uuid info
        if args.image_uuid:
            image_pb = get_image_info_from_uuid(args.image_uuid)
            usinfo.version = image_pb.name
            usinfo.image_uuid = image_pb.uuid
        if args.patch_image_uuid:
            image_pb = get_image_info_from_uuid(args.patch_image_uuid)
            usinfo.patch_version = image_pb.name.split("-")[2]
            usinfo.patch_image_uuid = image_pb.uuid
        if args.previous_image_uuid:
            image_pb = get_image_info_from_uuid(args.previous_image_uuid)
            usinfo.previous_version = image_pb.name
            usinfo.previous_image_uuid = image_pb.uuid
        if args.previous_patch_image_uuid:
            image_pb = get_image_info_from_uuid(args.previous_patch_image_uuid)
            usinfo.previous_patch_version = image_pb.name.split("-")[2]
            usinfo.previous_patch_image_uuid = image_pb.uuid
        print_and_log("*** After Update UpgradeStatusInfo values ***\n%s" % usinfo)
        if args.new_uuid:
            usinfo.uuid = args.new_uuid
        if args.update:
            print_and_log("Successfully updated to DS")
            notif_upgrade_status_info(usinfo)
        else:
            print_and_log("Skip Update")
        if args.update_db:
            print_and_log("Successfully updated to DB")
            commit2db(usinfo)
    except Exception as e:
        print_and_log("Error in swapping values for usinfo entry: %s" % str(e))
        traceback.print_exc()

@db_transaction
def commit2db(usinfo):
    clear_upgrade_status_info_fields(usinfo)
    protobuf2model(usinfo, None, False, skip_unfinished_pb=False)


if __name__ == "__main__":
        parser = argparse.ArgumentParser()
        parser.add_argument("--upgrade-usi-uuid", required=False, action="store", default=None, \
                help="USI uuid (cluster uuid/segroup uuid) to which USI info want to update, default cluster uuid")
        parser.add_argument("--new-uuid", required=False, action="store", default=None, \
                help="USI uuid (cluster uuid/segroup uuid) to which USI info want to update, default cluster uuid")
        parser.add_argument("--upgrade-ops", required=False, action="store", default=None, \
                help="valid values [ upgrade, rollback, patch,  rollbackpatch ] ")
        parser.add_argument("--image-uuid", required=False, action="store", default=None, \
                help="current version image uuid, image_uuid can pick from < show image >")
        parser.add_argument("--patch-image-uuid", required=False, action="store", default=None, \
                help="current patch version image uuid, image_uuid can pick from < show image >")
        parser.add_argument("--previous-image-uuid", required=False, action="store", default=None, \
                help="previous version image uuid, image_uuid can pick from < show image >")
        parser.add_argument("--previous-patch-image-uuid", required=False, action="store", default=None, \
                help="previous patch version image uuid, image_uuid can pick from < show image >")
        parser.add_argument("--update", required=False, action="store_true",
                help="If provided, will print and update the usinfo in same command\
                        else print the pre and post UpgradeStatusInfo value)")
        parser.add_argument("--update-db", required=False, action="store_true",
                help="If provided, will print and update the usinfo in DB")
        args = parser.parse_args()
        update_upgrade_usi_info(args)

"""
Usage:
=====
#> python3 /opt/avi/scripts/upgrade/update_upgrade_usi_info.py --help
usage: update_upgrade_usi_info.py [-h] [--upgrade-usi-uuid UPGRADE_USI_UUID] [--upgrade-ops UPGRADE_OPS]
                                  [--image-uuid IMAGE_UUID] [--patch-image-uuid PATCH_IMAGE_UUID]
                                  [--previous-image-uuid PREVIOUS_IMAGE_UUID]
                                  [--previous-patch-image-uuid PREVIOUS_PATCH_IMAGE_UUID] [--update]

optional arguments:
  -h, --help            show this help message and exit
  --upgrade-usi-uuid UPGRADE_USI_UUID
                        USI uuid (cluster uuid/segroup uuid) to which USI info want to update, default cluster uuid
  --upgrade-ops UPGRADE_OPS
                        valid values [ upgrade, rollback, patch, rollbackpatch ]
  --image-uuid IMAGE_UUID
                        current version image uuid, image_uuid can pick from < show image >
  --patch-image-uuid PATCH_IMAGE_UUID
                        current patch version image uuid, image_uuid can pick from < show image >
  --previous-image-uuid PREVIOUS_IMAGE_UUID
                        previous version image uuid, image_uuid can pick from < show image >
  --previous-patch-image-uuid PREVIOUS_PATCH_IMAGE_UUID
                        previous patch version image uuid, image_uuid can pick from < show image >
  --update              If provided, will print and update the usinfo in same command else print the pre and post
                        UpgradeStatusInfo value)
  --update-db           If provided, will print and update the usinfo in DB

  --new_cluster_uuid

$> cd /opt/avi/scripts/upgrade/

R1> Update Controller Upgrade status info (Current image version and image uuid)
  $> python3 update_upgrade_usi_info.py --image-uuid <Image UUID info from show image>
  ex: python3 update_upgrade_usi_info.py --image-uuid image-43569ddc-6e0e-42f0-8b8b-feef2e86573f \
                                         --update

R2> Update Controller Upgrade status info (Current Patch image version and Patch image uuid)
  $> python3 update_upgrade_usi_info.py --patch-image-uuid <Patch Image UUID from show image> \
                                         --update

R3> Update Controller Upgrade status info (Previous  image version and image uuid)
  $> python3 update_upgrade_usi_info.py --previous-image-uuid <Image UUID from show image> \
                                         --update

R4> Update current version, patch version and upgrade operations to rollback
  $> python3 update_upgrade_usi_info.py --image-uuid <Image UUID info from show image> \
                                        --patch-image-uuid <Patch Image UUID from show image> \
                                        --upgrade-ops rollback \
                                         --update


=> Cluster / SE Group UUID info can be pick from below commands:
[admin:ctr1]: > show cluster
[admin:ctr1]: > show serviceenginegroup

=> Image UUID can be pick from below command:
[admin:ctr1]: > show image
+---------------------------------+--------------------------------------------+-------------------+
| Name                            | UUID                                       | Type              |
+---------------------------------+--------------------------------------------+-------------------+
| 20.1.1-9071-20200728.222806     | image-43569ddc-6e0e-42f0-8b8b-feef2e86573f | IMAGE_TYPE_SYSTEM |
| 20.1.2-9167-20201008.021542     | image-ad3f6afe-02f0-42c9-9376-94647217fc21 | IMAGE_TYPE_SYSTEM |
| 20.1.2-9167-2p1-20201008.051446 | image-49459e8f-2f12-4960-b1c6-50f0422c8e6c | IMAGE_TYPE_PATCH  |
+---------------------------------+--------------------------------------------+-------------------+


For more info contact us at avi-upgrade-dev@vmware.com
"""
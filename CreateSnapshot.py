# create snapshot of drive and copy it from one vpc to another

from boto3 import resource,client

# Volume to copy
VOLUMEID = 'vol-027164d6795297037'
SNAPSHOT_DESCRIPTION = 'Dev_DB_2016'
FROMREGION = 'us-east-1'
TOREGION = 'us-west-2'
TOSUBREGION = 'us-west-2a'
# Size of drive
SIZE = 255
VOLUMETYPE = 'standard'
# Name of drive
TAGKEY = 'Name'
TAGVALUE = 'Dev_DB_D'
# Name of Instance to attach new volume
INSTANCEID = 'i-050c8c4497c3e52d2'
# Currently set for 10 minutes
DELAY = 25
MAX_ATTEMPTS = 48


# creates a new snapshot of given volume id and returns the id of the created snapshot
def create_snapshot(region, volume_id, description):
    # create a connection to ec2 in the region that the drive exists
    ec2_resource = resource('ec2', region_name=region)
    
    # create a snapshot of the specified volume and return the id of the snapshot
    snapshot = ec2_resource.create_snapshot(VolumeId=volume_id, Description=description)
    snapshot.wait_until_completed()

    return snapshot.id


# copies a snapshot to a different region and returns the id of the new snapshot
def copy_snapshot_to_region(to_region,from_region,snapshot_id,snapshot_description, delay, max_attempts):
    # create a connection in the region we want the new drive to be
    ec2_resource = resource('ec2', region_name=to_region)
    # need this connection for the waiter
    ec2_connection = client('ec2', region_name=to_region)
    
    # copy volume to other region which returns the new snapshot id
    new_snapshotid = (ec2_resource.Snapshot(snapshot_id).copy(Description=snapshot_description,SourceRegion=from_region))['SnapshotId']
    snapshot = ec2_resource.Snapshot(new_snapshotid)
    # create a connection to ec2 and wait until snapshot is completed
    #ec2 = client('ec2', region_name=TOREGION)
    
    config_snapshot_waiter(ec2_connection, snapshot, delay, max_attempts)
    
    snapshot.wait_until_completed()
    
    return snapshot.id


# creates volume from snapshot
def create_volume_from_snapshot (region,subregion,volume_size,snapshot_id,volume_type,tag_key,tag_value):
    ec2_resource = resource('ec2', region_name=region)
    new_volume = ec2_resource.create_volume(
        AvailabilityZone=subregion,
        Size=volume_size,
        SnapshotId=snapshot_id,
        VolumeType=VOLUMETYPE,
        TagSpecifications=[
            {
                'ResourceType': 'volume', 
                'Tags': [{ 'Key': tag_key, 'Value': tag_value },]
            },
        ]
    )
        
    return new_volume.id


'''
xvd[b-z]

xvd[b-c][a-z]

/dev/sda1

/dev/sd[b-e]
'''
# above is allowed device names
# will return next drive letter based on give list of drives
# currently only uses xvd[b-z]

def get_next_drive_name(device_name_list):
    range1 = 'b'
    range2 = 'z'    
    # Generates the characters from range1 to range2, inclusive
    def letter_range(range1,range2):
        for letter in range(ord(range1), ord(range2)+1):
            yield chr(letter)    
    
    string = ''       
    for letter in letter_range(range1,range2):
        seq = ('xvd',letter)
        device_name = string.join(seq)
        if device_name not in device_name_list:
            return device_name
        
    
def attach_drive_to_instance(region,volume_id,instance_id):
    ec2_resource = resource('ec2', region_name=region)
    
    volumes = ec2_resource.Instance(instance_id).volumes.all()
    
    devices = []
    for volume in list(volumes):
        devices.append(volume.attachments[0]['Device'])
    
    device_name = get_next_drive_name(devices)
    
    response = ec2_resource.Volume(volume_id).attach_to_instance(Device=device_name,InstanceId= instance_id, DryRun= False)
    
    
# https://boto3.readthedocs.io/en/latest/reference/services/ec2.html#EC2.Waiter.SnapshotCompleted
# Configures an existing waiter
def config_snapshot_waiter(ec2, snapshot, delay, max_attempts):
    waiter = ec2.get_waiter('snapshot_completed')
    
    waiter.wait(WaiterConfig={'Delay':delay,'MaxAttempts':max_attempts})
    

snapshotid = create_snapshot(FROMREGION,VOLUMEID,'dev_db')

copied_snapshotid = copy_snapshot_to_region(TOREGION,FROMREGION,snapshotid,'dev_db', DELAY, MAX_ATTEMPTS)

volume_id = create_volume_from_snapshot(TOREGION,TOSUBREGION,SIZE,copied_snapshotid,VOLUMETYPE,TAGKEY,TAGVALUE)

attach_drive_to_instance(TOREGION,volume_id,INSTANCEID)


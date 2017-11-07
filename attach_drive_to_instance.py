REGION = 'us-west-2'
VOLUME_ID = 'vol-09fddc4c0b4ee2f18'
INSTANCE_ID = 'i-04abdb581ec263142'

from boto3 import resource

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

attach_drive_to_instance(REGION,VOLUME_ID,INSTANCE_ID)
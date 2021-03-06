import createSecurityGroupObjects
import compareSecurityGroups
from sys import exit as sysexit
from csv import reader,writer
from writeSecurityGroupsToFile import write_row
from botocore.exceptions import ClientError

# def get_aws_security_groups():
    # return createSecurityGroupObjects.get_security_groups_from_aws

#def get_file_security_groups(csv_file):
    #return compareSecurityGroups.get_security_groups_from_file(csv_file)

def delete_security_group():
    pass

# gets security groups attached to network interface and removes security_group_id from that 
# list and then updates that interfaces security groups
def remove_security_group_from_interface(network_interface,security_group_id):
    groups = (network_interface.describe_attribute(Attribute='groupSet'))['Groups']
    
    for group in groups:
        if group['GroupId'] == security_group_id:
            groups.remove(group)
    
    modified_groups = ( group['GroupId'] for group in groups)
            
    network_interface.modify_attribute( Groups= modified_groups )
    
# TODO: Handle identical id's
def add_security_group_from_interface(network_interface,security_group_id):
    groups = (network_interface.describe_attribute(Attribute='groupSet'))['Groups']
    
    group_ids = [group['GroupId'] for group in groups]
    
    group_ids.append(security_group_id)
            
    network_interface.modify_attribute( Groups= group_ids )


# takes a Security_Group object defined in SecurityGroupClassDef
def add_security_group (ec2_resource, ec2_client, security_group):
    # TODO: Not adding the value for the Name Tag
    # TODO: Need to handle sg already exists
    try:
        return_group_id = (ec2_client.create_security_group(Description= security_group.description, GroupName= security_group.group_name, VpcId= security_group.vpc_id))['GroupId']
        # TODO: Need to add tag- key - name and the value
        updated_security_group = ec2_resource.SecurityGroup(return_group_id)
    
        # TODO: see if we can do this quicker with threading and the IpPermissions syntax from security_group.authorize_ingress
        for security_group_rule in security_group.list_Security_Group_Rules:
                updated_security_group.authorize_ingress(
                    CidrIp= security_group_rule.cidr_ip,
                    FromPort= security_group_rule.from_port,
                    ToPort= security_group_rule.to_port,
                    IpProtocol= security_group_rule.ip_protocol
                )
    except (ClientError):
        print ('Boto3 Client Error: SecurityGroup Name already exists. Appending "_<integer>" to the name')
        
        sgn = security_group.group_name
        sgn_len = len(sgn)
        
        try: 
            security_group.group_name = '{}_{}'.format(sgn[0:(sgn_len-1):],str(sgn[::sgn_len -1] + 1) )
        except (ValueError):
            security_group.group_name = '{}_{}'.format(sgn,'_1')
            
def get_network_interface_with_security_group(ec2_client, security_group_id):
    return ec2_client.describe_network_interfaces(Filters=[{'Name': 'group-id','Values': security_group_id}])

    
def replace_security_group(security_group_id, csv_file, ec2_client):
    # get all network interfaces that have the argument security_group_id
    network_interfaces = get_network_interface_with_security_group(ec2_client, security_group_id)
    security_group = ec2_client.describe_security_groups(Filters=[{'Name':'group-id','Values':security_group_id}])
    
    for network_interface in network_interfaces:
        # detatch security group
        remove_security_group_from_interface(security_group_id)
    
        
    # delete security group from aws
    try:
        security_group.delete()
    except (DependencyViolation):
        # TODO: Write this to file
        network_interfaces = get_network_interface_with_security_group(ec2_client, security_group_id)
        print ('Dependency Violation, still need to detach sg from network interface: {}'.format(network_interfaces))
        
        
    # create security group from file, return id, write id to cell in file
    group_id = add_security_group(ec2_client, security_group_id, csv_file)
    
    # attach sg to each id
    for network_interface in network_interfaces:
        add_security_group(network_interface, group_id)
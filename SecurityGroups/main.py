import createSecurityGroupObjects
import SecurityGroupClassDef
import compareSecurityGroups
import changeSecurityGroups
from boto3 import client,resource
from writeSecurityGroupsToFile import write_security_group_CSV

REGION = 'us-west-2'
CSVFILE = './sginfo.csv'
REGION = 'us-west-2'
VPC = 'vpc-d3338eb5' 

def main ():
    ec2_client = client('ec2',region_name=REGION)
    ec2_resource = resource('ec2',region_name=REGION)
    
    list_security_groups_from_aws = createSecurityGroupObjects.get_security_groups_from_aws(ec2_client, VPC)
    list_security_groups_from_file = createSecurityGroupObjects.get_security_groups_from_file(CSVFILE)    
    
    print (compareSecurityGroups.compare_all(list_security_groups_from_aws,list_security_groups_from_file))
    print (compareSecurityGroups.get_removed_security_groups(list_security_groups_from_file,list_security_groups_from_aws))
    
    new_groups = compareSecurityGroups.get_added_security_groups(list_security_groups_from_file,list_security_groups_from_aws)
   
    for security_group in new_groups:
        new_id = changeSecurityGroups.add_security_group(ec2_resource, ec2_client, security_group)
    
    # get newly updated list from aws and update local file
    list_security_groups_from_aws = createSecurityGroupObjects.get_security_groups_from_aws(ec2_client, VPC)
    write_security_group_CSV(CSVFILE,list_security_groups_from_aws)

def tests():
    ec2_client = client('ec2',region_name=REGION)
    ec2_resource = resource('ec2',region_name=REGION)
    
    list_security_groups_from_aws = createSecurityGroupObjects.get_security_groups_from_aws(ec2_client, VPC)
    list_security_groups_from_file = createSecurityGroupObjects.get_security_groups_from_file(CSVFILE)    
    
    print (compareSecurityGroups.compare_all(list_security_groups_from_aws,list_security_groups_from_file))
    print (compareSecurityGroups.get_removed_security_groups(list_security_groups_from_file,list_security_groups_from_aws))
    
    new_groups = compareSecurityGroups.get_added_security_groups(list_security_groups_from_file,list_security_groups_from_aws)
   
    for security_group in new_groups:
        new_id = changeSecurityGroups.add_security_group(ec2_resource, ec2_client, security_group)
    
    # get newly updated list from aws and update local file
    list_security_groups_from_aws = createSecurityGroupObjects.get_security_groups_from_aws(ec2_client, VPC)
    write_security_group_CSV(CSVFILE,list_security_groups_from_aws)
    
main()
# tests()
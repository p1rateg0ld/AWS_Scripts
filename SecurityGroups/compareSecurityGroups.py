# update security groups from csv file

# maybe read csv as generator. 
# TODO: MAKE THREADED SO WE CAN WRITE MULTIPLE GROUPS AT ONCE
# TODO: TEST PASSING list_Security_Group_Rules to Security_Group class

from boto3 import client,ec2,resource
from csv import reader
from sys import exc_info
from re import match
from collections import namedtuple
from multiprocessing.dummy import Pool as ThreadPool

# local module - import class object
from SecurityGroupClassDef import Security_Group
# local module - gets security group info and returns list of Security_Group objects
import createSecurityGroupObjects
            
# if security group in file isn't in aws, return that group
def get_added_security_groups ( security_group_list_file, security_group_list_aws ):
    return [ s_g for s_g in security_group_list_file if s_g.group_id not in [ security_group.group_id for security_group in security_group_list_aws ] or not s_g.group_id ]
# if security group in aws is not in file, return that group id
def get_removed_security_groups ( security_group_list_file, security_group_list_aws ):
    return [ s_g.group_id for s_g in security_group_list_file if s_g.group_id not in [ security_group.group_id for security_group in security_group_list_aws ] or not s_g.group_id ]

# calls security_group's compare function and returns group_ids that are not similar
def compare_all(security_group_list_1, security_group_list_2):    
    # if the group_id in the first list is found in the second, compare
    different_group_ids = [ s_g.group_id for security_group in security_group_list_1 
                            for s_g in security_group_list_2
                            if security_group.group_id == s_g.group_id
                            if not s_g.compare_sg(security_group) ]

    return different_group_ids


# create ec2 client
#ec2_client = client('ec2',region_name=REGION)

## create ec2 resource object for resource specific requests
#ec2_resource = resource('ec2',region_name=REGION)

# Assumes the rule was already checked to make sure it needs updating
# TODO Handle -2 values wherever those are


# TODO: IF SECURITY GROUP DOESN'T HAVE AN ID, THEN IT IS A NEW SG - MAYBE PLACE A NAME LIKE NEW IN THE CELL
# TODO: Modify to get all security groups and return a list
# TODO handle IpProtocol -1 (All Traffic)
#def get_security_groups_from_file(csv_reader):
    #list_security_groups = []
    #def title_from_row(row):
        #if any(string for string in row):  
            #security_group = Security_Group(*row)
            #return security_group
        #else:
            #return False
    
    
    #def sec_group_rule_from_row(row,security_group):
        #if any(string for string in row):
            #security_group.list_Security_Group_Rules.append(security_group.Security_Group_Rule(*row))
            #return True
        #else:
            #return False
         
    #while True:
        #try:
            #row = csv_reader.__next__()
            #security_group = title_from_row(row)
        #except (StopIteration):
            #print('StopIteration error')
            #break
        #if not security_group:
            #print('title_from_row returned false')
            #break
        #while True:
            #try:
                #row = csv_reader.__next__()
                #if not sec_group_rule_from_row(row,security_group):
                    #print('sec_group_rule_from_row returned false')
                    #break
            #except (StopIteration):
                #print('StopIteration error')
                #break
        #list_security_groups.append(security_group)
        
    #return list_security_groups
        

## TODO handle IpProtocol -1 (All Traffic)

#def get_security_groups_from_aws(region,vpc_id):
    #list_security_groups_from_aws = []
    
    ## Catch KeyError Wrapper
    #def attempt_key(dict_var,key):
        #try:
            #return dict_var[key]
        #except:
            #return ''
    #def extract_rules_to_security_group(security_group, from_aws): 
        #IP_PROTOCOL,FROM_PORT,TO_PORT,CIDR_IP,DESCRIPTION = ['']*5
        
        #for ip_permission in from_aws['IpPermissions']:
            #IP_PROTOCOL = attempt_key(ip_permission,'IpProtocol')
            #FROM_PORT = attempt_key(ip_permission,'FromPort')
            #TO_PORT = attempt_key(ip_permission,'ToPort')
            
            #for ip_range in ip_permission['IpRanges']:
                #CIDR_IP = attempt_key(ip_range,'CidrIp')
                #DESCRIPTION = attempt_key(ip_range,'Description')
                
                
            #security_group.list_Security_Group_Rules.append(
                #security_group.Security_Group_Rule(
                    #ip_protocol=IP_PROTOCOL,
                    #from_port=FROM_PORT,
                    #to_port=TO_PORT,
                    #cidr_ip=CIDR_IP,
                    #description=DESCRIPTION)
            #)
        
        
    #def create_security_group(s_group):
        #try:
            #security_group = Security_Group(
                #key_name=s_group['Tags'][0]['Value'],
                #group_name=attempt_key(s_group,'GroupName'),
                #vpc_id=attempt_key(s_group,'VpcId'),
                #group_id=attempt_key(s_group,'GroupId'),
                #description=attempt_key(s_group,'Description')
            #)
        #except(KeyError):
            #security_group = Security_Group(
                #key_name='',
                #group_name=attempt_key(s_group,'GroupName'),
                #vpc_id=attempt_key(s_group,'VpcId'),
                #group_id=attempt_key(s_group,'GroupId'),
                #description=attempt_key(s_group,'Description')
            #)            
        #extract_rules_to_security_group(security_group,s_group)
        #return security_group

        
    ## create ec2 client
    #ec2client = client('ec2',region_name=region)
    
    ## get security groups, gets all security group information from vpc
    #response = ec2client.describe_security_groups(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
    #for sg in response['SecurityGroups']:
        #list_security_groups_from_aws.append(create_security_group(sg))
    
    #return list_security_groups_from_aws

#def compare_security_groups(security_group_1,security_group_2):



    


    # This returns group ids not found in the other list - do we need to do the inverse for deleted s_g's?
    #[ security_group.group_id for security_group in security_group_list_1 
              #if security_group.group_id not in (s_g.group_id for s_g in security_group_list_2) ]    
    
    


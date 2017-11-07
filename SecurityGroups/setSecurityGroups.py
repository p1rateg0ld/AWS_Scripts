# update security groups from csv file

# maybe read csv as generator. 
# TODO: MAKE THREADED SO WE CAN WRITE MULTIPLE GROUPS AT ONCE

from boto3 import client,ec2,resource
from csv import reader
from sys import exc_info
from re import match
from collections import namedtuple
from multiprocessing.dummy import Pool as ThreadPool

CSVFILE = './sginfo.csv'
REGION = 'us-west-2'
VPC = 'vpc-d3338eb5'

# create ec2 client
ec2_client = client('ec2',region_name=REGION)

# create ec2 resource object for resource specific requests
ec2_resource = resource('ec2',region_name=REGION)

SecurityGroupRule = namedtuple('SecurityGroupRule', {'ip_protocol', 'from_port', 'to_port', 'cidr_ip','description'}, verbose=False)
# key_name: Value of Tag 'Name'
# security_group_rules: list of SecurityGroupRule named tuples
SecurityGroup = namedtuple('SecurityGroup', {'key_name','group_name','vpc_id','security_group_id','description','security_group_rules'}, verbose=False)

def get_sec_group_id_list(ec2_client):
    # get security groups, gets all security group information from vpc
    # there may be an issue with sg's in a non-default vpc's needing to be specified in initial request
    response = ec2_client.describe_security_groups(Filters=[{'Name': 'vpc-id', 'Values':[VPC]}]) 
    
    # extract GroupId's into a list of values
    group_id = []
    [group_id.append(security_group['GroupId']) for security_group in response['SecurityGroups']]

    return group_id
    
    
# takes an ec2.SecurityGroup object
def compare_to_sg(security_group, SecurityGroupRule): 
    # check if any rules don't exist in request iterate over CIDR's inside ranges iteration
    # list of dicts
    for ip_permission in security_group.ip_permissions:
        '''
        CSV ROW STRUCTURE:
        [IpProtocol][FromPort][ToPort][CidrIp][Description]
        '''
        # test line
        print (ip_permission)
        # seems to have an issue as an iterable
        
        #test line
        print ('ip protocol: ' + SecurityGroupRule.ip_protocol + ' from port: ' + SecurityGroupRule.from_port + ' to port: ' + SecurityGroupRule.to_port + ' Cidr: ' + SecurityGroupRule.cidr_ip + ' Description: ' + SecurityGroupRule.description)
        if SecurityGroupRule.ip_protocol == ip_permission['IpProtocol']:
            # test line
            print (SecurityGroupRule.ip_protocol)
            if int(SecurityGroupRule.from_port) == int(ip_permission['FromPort']):
                # test line
                print (SecurityGroupRule.from_port)
                if int(SecurityGroupRule.to_port) == int(ip_permission['ToPort']):
                    # test line
                    print (SecurityGroupRule.from_port)
                    for ip_ranges in ip_permission['IpRanges']:
                        # test line
                        print (SecurityGroupRule.cidr_ip)
                        # test line
                        print (ip_ranges)
                        if str(SecurityGroupRule.cidr_ip) == str(ip_ranges['CidrIp']):
                            # test line
                            print ('cidr_ip identical')
                            if SecurityGroupRule.description and 'Description' in ip_ranges:
                                if str(SecurityGroupRule.description) == str(ip_ranges['Description']):
                                    # logging line
                                    print ('SecurityGroupRule identical to SG')  
                            elif not SecurityGroupRule.description and 'Description' not in ip_ranges:
                                # logging line
                                print ('SecurityGroupRule identical to SG')                                 
                            else:
                                return False
                        else:
                            return False
                else:
                    return False
            else:
                return False
        else:
            return False
    return True

# Assumes the rule was already checked to make sure it needs updating
# Takes an ec2 resource security group
def update_rule(security_group,old_rule,new_rule):
    response = security_group.revoke_ingress(CidrIp=old_rule.ip_protocol,FromPort=old_rule.from_port,ToPort=old_rule.to_port)
    # test line
    print (response)
    
    # TODO Need to test these description conditionals
    if new_rule.description:
        response = security_group.authorize_ingress(
            IpPermissions=[
                {'IpProtocol': new_rule.ip_protocol,
                 'FromPort': new_rule.from_port,
                 'ToPort': new_rule.to_port,
                 'IpRanges': [
                     {
                         'CidrIp': new_rule.cidr_ip,
                         'Description':new_rule.description                                     
                     }
                 ]
                 
                }
            ]
        )          
    
    else:
        response = security_group.authorize_ingress(CidrIp=new_rule.ip_protocol,FromPort=new_rule.from_port,ToPort=new_rule.to_port)
      
    # test line
    print (response)    
    

def update_sg():
    pass

def new_sg():
    
    pass


# TODO: IF SECURITY GROUP DOESN'T HAVE AN ID, THEN IT IS A NEW SG - MAYBE PLACE A NAME LIKE NEW IN THE CELL
# TODO: Modify to get all security groups and return a list
def get_security_group_from_file(csv_reader):
    try:
        row = csv_reader.__next__()
    except (StopIteration):
        row = None
        pass
    
    list_of_rules = []
    
    title_row = row
    
    if not row:
        return False
        
    while True:
        try:
            row = csv_reader.__next__()
        except (StopIteration):
            row = None
            pass
        if not row or not row[0]:
            break
        
        rowlen = len(row)
        if rowlen > 4:
            security_group_rule = SecurityGroupRule(ip_protocol=row[0],from_port=row[1],to_port=row[2],cidr_ip=row[3],description=row[4])
        else:
            security_group_rule = SecurityGroupRule(ip_protocol=row[0],from_port=row[1],to_port=row[2],cidr_ip=row[3])
            
        list_of_rules.append(security_group_rule)

    if len(title_row) > 4:
        security_group = SecurityGroup(key_name=title_row[0],group_name=title_row[1],vpc_id=title_row[2],security_group_id=title_row[3],description=title_row[4],security_group_rules=list_of_rules)
    elif len(title_row):
        security_group = SecurityGroup(key_name=title_row[0],group_name=title_row[1],vpc_id=title_row[2],security_group_id=title_row[3],security_group_rules=list_of_rules)        
    
    return security_group


def get_security_groups_from_aws(region,vpc_id):
    # create ec2 client
    ec2client = client('ec2',region_name=region)
    
    # get security groups, gets all security group information from vpc
    security_groups = ec2client.describe_security_groups(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
    
    list_of_security_groups_from_aws = []
    for security_group in security_groups['SecurityGroups']:
        list_of_security_group_rules = []
        for ip_permission in security_group['IpPermissions']:
            IP_PROTOCOL = ip_permission['IpProtocol']
            FROM_PORT = ip_permission['FromPort']
            TO_PORT = ip_permission['ToPort']
            for ip_range in ip_permission['IpRanges']:
                CIDR_IP = ip_range['CidrIp']
                DESCRIPTION = ''
                try: 
                    DESCRIPTION = ip_range['Description']
                except(KeyError):
                    print('no description')
                security_group_rule = SecurityGroupRule(ip_protocol=IP_PROTOCOL,from_port=FROM_PORT,to_port=TO_PORT,cidr_ip=CIDR_IP,description=DESCRIPTION)
                list_of_security_group_rules.append(security_group_rule)
        # TODO Case for description not being there
        DESCRIPTION = ''
        try:
            DESCRIPTION = security_group['Description']
        except(KeyError):
            print('no description')
        list_of_security_groups_from_aws.append(SecurityGroup(key_name=security_group['Tags'][0]['Value'],group_name=security_group['GroupName'],vpc_id=security_group['VpcId'],security_group_id=security_group['GroupId'],description=security_group['Description'],security_group_rules=list_of_security_group_rules))
    return list_of_security_groups_from_aws

def compare_security_groups(security_group_1,security_group_2):
    if security_group_1 == security_group_2:
        return true

with open(CSVFILE,newline='') as csvfile:
    c_reader = reader(csvfile, delimiter= '^', quotechar= '\"')

    list_security_groups_from_file= []
    while True:
        returnvalue = get_security_group_from_file(c_reader)
        if not returnvalue:
            break
        list_security_groups_from_file.append(returnvalue)
    
    
    # TODO If CSV_SG has no ID, create new sg
    
    aws_security_groups = get_security_groups_from_aws(REGION,VPC)
    
    pool = ThreadPool(4)
    
    # pool.starmap(function, zip(list_a,list_b))
    
    # TODO Define security group compare
    # pass lists of security groups to pool
    # pool should be able to run the sequence of functions down to the update script and return successful state
    
    #multi thread this
    for security_group in list_of_security_groups_from_file:
        found = False
        group_id = security_group.security_group_id
        for aws_security_group in aws_security_groups:
            if group_id == aws_security_group['GroupId']:
                found = True
                for security_group_rule in security_group.security_group_rules:
                    # if it returns false we will update the sg in aws
                    if not compare_to_sg(aws_security_group,security_group_rule):
                        update_sg()
        if not found:
            new_sg()
    
# Get Security Groups from AWS

# Get Security Group from file

# check if sg_id is in AWS SG's
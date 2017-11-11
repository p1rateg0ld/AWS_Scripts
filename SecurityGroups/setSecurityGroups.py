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

CSVFILE = './sginfo.csv'
REGION = 'us-west-2'
VPC = 'vpc-d3338eb5'

class Security_Group:
    def __init__(self,key_name='',group_name='',vpc_id='',group_id='',description='',list_Security_Group_Rules=[]):
        self.key_name = key_name
        self.group_name = group_name
        self.vpc_id = vpc_id
        self.group_id = group_id
        self.description = description
        if list_Security_Group_Rules:
            print(id(list_Security_Group_Rules))
            self.list_Security_Group_Rules = list_Security_Group_Rules
        self.list_Security_Group_Rules = []
    
    class Security_Group_Rule:
        def __init__(self,ip_protocol=-2,from_port=-2,to_port=-2,cidr_ip='',description=''):
            self.ip_protocol = ip_protocol
            self.from_port = from_port
            self.to_port = to_port
            self.cidr_ip = cidr_ip
            self.description = description
            
    def compare(self, other_security_group):
        self_values = vars(self)
        other_values = vars(other_security_group)
        #this needs to call the update to aws for rules -- possible to get all instances with the sg, delete the sg and replace it
        if not [False for i in range(0,len(self_values)) for key in self_values.keys() if self_values[key] != other_values[key] ]:
            print(self.group_id)
            self = other_security_group
            print ('updated')
            return self.group_id
        else:
            print ('identical')
            

# create ec2 client
ec2_client = client('ec2',region_name=REGION)

# create ec2 resource object for resource specific requests
ec2_resource = resource('ec2',region_name=REGION)
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
    

def new_sg():
    
    pass


# TODO: IF SECURITY GROUP DOESN'T HAVE AN ID, THEN IT IS A NEW SG - MAYBE PLACE A NAME LIKE NEW IN THE CELL
# TODO: Modify to get all security groups and return a list
# TODO handle IpProtocol -1 (All Traffic)
def get_security_groups_from_file(csv_reader):
    list_security_groups = []
    def title_from_row(row):
        if any(string for string in row):  
            security_group = Security_Group(*row)
            return security_group
        else:
            return False
    
    
    def sec_group_rule_from_row(row,security_group):
        if any(string for string in row):
            security_group.list_Security_Group_Rules.append(security_group.Security_Group_Rule(*row))
            return True
        else:
            return False
         
    while True:
        try:
            row = csv_reader.__next__()
            security_group = title_from_row(row)
        except (StopIteration):
            print('StopIteration error')
            break
        if not security_group:
            print('title_from_row returned false')
            break
        while True:
            try:
                row = csv_reader.__next__()
                if not sec_group_rule_from_row(row,security_group):
                    print('sec_group_rule_from_row returned false')
                    break
            except (StopIteration):
                print('StopIteration error')
                break
        list_security_groups.append(security_group)
        
    return list_security_groups
        

# TODO handle IpProtocol -1 (All Traffic)
def get_security_groups_from_aws(region,vpc_id):
    list_security_groups_from_aws = []
    
    # Catch KeyError Wrapper
    def attempt_key(dict_var,key):
        try:
            return dict_var[key]
        except:
            return ''
    def extract_rules_to_security_group(security_group, from_aws): 
        IP_PROTOCOL,FROM_PORT,TO_PORT,CIDR_IP,DESCRIPTION = ['']*5
        
        for ip_permission in from_aws['IpPermissions']:
            IP_PROTOCOL = attempt_key(ip_permission,'IpProtocol')
            FROM_PORT = attempt_key(ip_permission,'FromPort')
            TO_PORT = attempt_key(ip_permission,'ToPort')
            
            for ip_range in ip_permission['IpRanges']:
                CIDR_IP = attempt_key(ip_range,'CidrIp')
                DESCRIPTION = attempt_key(ip_range,'Description')
                
                
            security_group.list_Security_Group_Rules.append(
                security_group.Security_Group_Rule(
                    ip_protocol=IP_PROTOCOL,
                    from_port=FROM_PORT,
                    to_port=TO_PORT,
                    cidr_ip=CIDR_IP,
                    description=DESCRIPTION)
            )
        
        
    def create_security_group(s_group):
        try:
            security_group = Security_Group(
                key_name=s_group['Tags'][0]['Value'],
                group_name=attempt_key(s_group,'GroupName'),
                vpc_id=attempt_key(s_group,'VpcId'),
                group_id=attempt_key(s_group,'GroupId'),
                description=attempt_key(s_group,'Description')
            )
        except(KeyError):
            security_group = Security_Group(
                key_name='',
                group_name=attempt_key(s_group,'GroupName'),
                vpc_id=attempt_key(s_group,'VpcId'),
                group_id=attempt_key(s_group,'GroupId'),
                description=attempt_key(s_group,'Description')
            )            
        extract_rules_to_security_group(security_group,s_group)
        return security_group

        
    # create ec2 client
    ec2client = client('ec2',region_name=region)
    
    # get security groups, gets all security group information from vpc
    response = ec2client.describe_security_groups(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
    for sg in response['SecurityGroups']:
        list_security_groups_from_aws.append(create_security_group(sg))
    
    return list_security_groups_from_aws

#def compare_security_groups(security_group_1,security_group_2):
    
    
with open(CSVFILE,newline='') as csvfile:
    c_reader = reader(csvfile, delimiter= '^', quotechar= '\"')

    print('xxxxxxxxxxxxxxxxxxxxxxxxxx')
    list_security_groups_from_aws = get_security_groups_from_aws(REGION,VPC)
    print('xxxxxxxxxxxxxxxxxxxxxxxxxx')
    list_security_groups_from_file = get_security_groups_from_file(c_reader)
    print('xxxxxxxxxxxxxxxxxxxxxxxxxx')
    
    # for each sg in list1
    #  for each sg in list2 
    #   if group_id2 == group_id1
    #    compare all values	
    
    [ s_g.compare(security_group) for security_group in list_security_groups_from_file 
      for s_g in list_security_groups_from_aws
      if security_group.group_id == s_g.group_id ]
    
    # This returns group ids not found in the other list - do we need to do the inverse for deleted s_g's?
    x = [ security_group.group_id for security_group in list_security_groups_from_file 
          if security_group.group_id not in (s_g.group_id for s_g in list_security_groups_from_aws) ]
    
    print(x)
    
    
     
    
        #if not returnvalue:
            #break
        #list_security_groups_from_file.append(returnvalue)
    
    
    ## TODO If CSV_SG has no ID, create new sg
    
    #aws_security_groups = get_security_groups_from_aws(REGION,VPC)
    
    #pool = ThreadPool(4)
    
    ## pool.starmap(function, zip(list_a,list_b))
    
    ## TODO Define security group compare
    ## pass lists of security groups to pool
    ## pool should be able to run the sequence of functions down to the update script and return successful state
    
    ##multi thread this
    #print('xxxxxxxxxxxxxxxxxxxx')
    #print(aws_security_groups)
    #print('xxxxxxxxxxxxxxxxxxxx')
    #print(list_security_groups_from_file)
    #print('xxxxxxxxxxxxxxxxxxxx')
    
    
    
    #for security_group in list_security_groups_from_file:
        #found = [
            #not group_id&1
            #for aws_security_group in aws_security_groups
            #if aws_security_group.group_id == security_group.group_id]
# Get Security Groups from AWS

# Get Security Group from file

# check if sg_id is in AWS SG's
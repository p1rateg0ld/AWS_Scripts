# Parse Roles and create security groups

from csv import reader
from re import split
from createSecurityGroupObjects import get_security_groups_from_aws

#temp import
from boto3 import client

ROLESFILE = './roles.csv'
USERSFILE = './users.csv'

def read_data(csv_file):
    with open(csv_file,newline='') as csvfile:
        c_reader = reader(csvfile, delimiter= '^', quotechar= '\"')
        data = [line for line in c_reader]
        
        return data
    
def get_data(rolesfile,userfile):
    roles = read_data(rolesfile)
    users = read_data(userfile)
    yield roles[1::]
    yield users[1::]
    
def create_rules(user,role, list_security_groups):
    def split_data(data):
        return split(',', data)
    def get_security_groups(input_rules_list, list_security_groups):
        if input_rules_list == 'all':
            input_rules_list = list_security_groups
        return [rule for rule in input_rules_list if rule in list_security_groups]
    def add_rule(security_group, ip_protocol, cidr, port, description):
        security_group.add_new_rule([ip_protocol,cidr,port,description])
        
    description = 'User {}'.format(user[0])
    
    security_groups = get_security_groups(role[2], list_security_groups)
    
    # need to catch empty cells errors
    for security_group in security_groups:
        for cidr in user[1]:
            # add tcp rules
            for port in split_data(role[1]):
                add_rule(security_group,'tcp',cidr,description)
            # add udp rules
            for port in split_data(role[2]):
                add_rule(security_group,'udp',cidr,description)
    
    print (security_groups)    
    
    
def test_main():
    REGION = 'us-west-2'
    VPC = 'vpc-d3338eb5'  
    ec2_client = client('ec2',region_name=REGION)
    
    role_data,user_data = get_data(ROLESFILE,USERSFILE)
    list_security_groups=get_security_groups_from_aws(ec2_client,VPC)
    
    for role,user in zip(role_data,user_data):
        create_rules(role,
                     user,
                     list_security_groups
                    )

test_main()
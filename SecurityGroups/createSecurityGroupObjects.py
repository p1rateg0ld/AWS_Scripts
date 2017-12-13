from SecurityGroupClassDef import Security_Group
from csv import reader
from boto3 import client

# Creates Security_Group objects from the AWS response
def get_security_groups_from_aws(ec2_client, vpc_id):
    list_security_groups_from_aws = []
    
    # Catch KeyError Wrapper
    def attempt_key(dict_var,key):
        try:
            return dict_var[key]
        except:
            return ''
        
        
    def extract_rules_to_security_group(security_group, from_aws): 
        print (('extract_rules %i' ) % id(security_group))
        IP_PROTOCOL,FROM_PORT,TO_PORT,CIDR_IP,DESCRIPTION = ['']*5
        
        for ip_permission in from_aws['IpPermissions']:
            IP_PROTOCOL = attempt_key(ip_permission,'IpProtocol')
            FROM_PORT = attempt_key(ip_permission,'FromPort')
            TO_PORT = attempt_key(ip_permission,'ToPort')
            
            for ip_range in ip_permission['IpRanges']:
                CIDR_IP = attempt_key(ip_range,'CidrIp')
                DESCRIPTION = attempt_key(ip_range,'Description')
                
                security_group.add_new_rule([
                            IP_PROTOCOL,
                                FROM_PORT,
                                TO_PORT,
                                CIDR_IP,
                                DESCRIPTION ]
                )                
                
        
        # TODO: Security Group is adding rules, but not returning the object with assigned list
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
            print(('create_security_group %i') % id(security_group))
        extract_rules_to_security_group(security_group,s_group)
        return security_group
    
    # get security groups, gets all security group information from vpc
    response = ec2_client.describe_security_groups(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
    for sg in response['SecurityGroups']:
        list_security_groups_from_aws.append(create_security_group(sg))
    
    return list_security_groups_from_aws


# Creates Security_Group objects from the csv file 
def get_security_groups_from_file(csv_file):
    with open(csv_file,newline='') as csvfile:
        c_reader = reader(csvfile, delimiter= '^', quotechar= '\"')    
        list_security_groups = []
        def security_group_from_title(row):
            if any(row): 
                security_group = Security_Group(*row)
                return security_group
            else:
                return False
        
        
        def sec_group_rule_from_row(row,security_group):
            if any(row):
                security_group.add_new_rule(row)
                return True
            else:
                return False
             
        while True:
            try:
                row = c_reader.__next__()
                security_group = security_group_from_title(row)
            except (StopIteration):
                print('StopIteration error')
                break
            if not security_group:
                print('title_from_row returned false')
                break
            while True:
                try:
                    row = c_reader.__next__()
                    if not sec_group_rule_from_row(row,security_group):
                        print('sec_group_rule_from_row returned false')
                        break
                except (StopIteration):
                    print('StopIteration error')
                    break
            list_security_groups.append(security_group)
            
    return list_security_groups
        

def get_security_group_by_id(list_security_groups, security_group_id):
    for security_group in list_security_groups:
        if security_group.group_id == security_group_id:
            return security_group
    
    return False
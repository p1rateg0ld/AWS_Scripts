# parse aws ec2 describe-security-groups

# starting with modifying output to a csv file

# TODO: Currently assumes file doesn't exist. 
#       Should probably import an existing file and update it
#       in case the amount of data becomes sizeable

from csv import writer
from boto3 import client,ec2
from sys import exc_info

CSVFILE = './sginfo.csv'
REGION = 'us-west-2'
VPC = 'vpc-d3338eb5'

'''
Security Groups response structure
{
'Description': 'Staging - allow all TCP/UDP from public',
'GroupName': 'STG_All_from_public',
'IpPermissions': 
    [
        {'FromPort': 5439, 'IpProtocol': 'tcp', 'IpRanges': [{'CidrIp': '68.101.189.211/32'}], 'Ipv6Ranges': [], 'PrefixListIds': [], 'ToPort': 5439, 'UserIdGroupPairs': []},
        {'FromPort': 0, 'IpProtocol': 'tcp', 'IpRanges': [{'CidrIp': '176.0.0.0/24'}], 'Ipv6Ranges': [], 'PrefixListIds': [], 'ToPort': 65535, 'UserIdGroupPairs': []}, 
        {'FromPort': 0, 'IpProtocol': 'udp', 'IpRanges': [{'CidrIp': '176.0.0.0/24'}], 'Ipv6Ranges': [], 'PrefixListIds': [], 'ToPort': 65535, 'UserIdGroupPairs': []}, 
        {'FromPort': -1, 'IpProtocol': 'icmp', 'IpRanges': [{'CidrIp': '176.0.0.0/24'}], 'Ipv6Ranges': [], 'PrefixListIds': [], 'ToPort': -1, 'UserIdGroupPairs': [
    ],
'OwnerId': '131481646883',
'GroupId': 'sg-03f6cc79',
'IpPermissionsEgress': [{'IpProtocol': '-1', 'IpRanges': [{'CidrIp': '0.0.0.0/0'}], 'Ipv6Ranges': [], 'PrefixListIds': [], 'UserIdGroupPairs': []}],
'Tags': [{'Key': 'Name', 'Value': 'STG_All_from_public'}],
'VpcId': 'vpc-d3338eb5'
}
'''

'''
CSV STRUCTURE:

<Tag:Name:Value>^NAME(GroupName)^VPC_ID^GROUP_ID^DESCRIPTION
FROM_PORT^TO_PORT^IP_PROTOCOL^IP_RANGES^DESCRIPTION (for each CidrIp)
'''


# create ec2 client
ec2client = client('ec2',region_name=REGION)

# get security groups, gets all security group information from vpc
response = ec2client.describe_security_groups(Filters=[{'Name': 'vpc-id', 'Values':[VPC]}])

# test lines
# print (response)
# print ('---------------------------')

securitygroups = response['SecurityGroups']

# write SG to csv
with open(CSVFILE,'w',newline='') as csvfile:
    c_writer = writer(csvfile,delimiter='^',quotechar='\"')
    for sg in securitygroups:
        # write group name, \n
        # test line
        # print(sg['Tags'][0]['Value'] + '^' + sg['GroupName'] + '^' + sg['VpcId'] + '^' + sg['GroupId'] + '^' + sg['Description'] + '^')
        c_writer.writerow([sg['Tags'][0]['Value']] + [sg['GroupName']] + [sg['VpcId']] + [sg['GroupId']] + [sg['Description']])
        
        # write ip info
        for ip_permissions in sg['IpPermissions']:
            # test line
            # print (ip_permissions)
        
            try:
                for ipranges in ip_permissions['IpRanges']:
                    # test line
                    # print (ipranges)
                    
                    #if the Cidr has a description
                    if 'Description' in ipranges:
                        c_writer.writerow([ip_permissions['IpProtocol']] + [ip_permissions['FromPort']] + [ip_permissions['ToPort']] + [ipranges['CidrIp']] + [ipranges['Description']])
                    else:
                        c_writer.writerow([ip_permissions['IpProtocol']] +[ip_permissions['FromPort']] + [ip_permissions['ToPort']] + [ipranges['CidrIp']])  
                        
            except (IndexError):
                exc_type, exc_obj, tb = sys.exc_info()
                print('{} {}' % (exc_type, tb_lineno))
            except (KeyError):
                exc_type, exc_obj, tb = exc_info()
                print (exc_type, ' ',tb.tb_lineno)
        # test line
        # print() 
        
        #add a space
        c_writer.writerow('')

# open text file

# read lines
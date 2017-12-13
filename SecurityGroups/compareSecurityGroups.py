# update security groups from csv file

# maybe read csv as generator. 

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

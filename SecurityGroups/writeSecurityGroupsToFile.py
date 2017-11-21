from createSecurityGroupObjects import get_security_groups_from_aws
from csv import writer
from boto3 import client

# Uses the Security_Group object from SecurityGroupClassDef.py
# TODO create multiple files in case there's an error
def write_row (csv_writer,args):
    try:
        csv_writer.writerow(args)
    except:
        with open('./security_group_error_log.txt', 'r+', newline='\n') as errorlog:
            errorlog.write('Unable to write line: ', ' '.join(map(str, a)))
    
def write_security_group_CSV(csv_file, list_security_groups):
    with open(csv_file,'w',newline='') as csvfile:
        # TODO use closer to standard delimiters since data from aws was already extracted (may not work actually)
        c_writer = writer(csvfile,delimiter='^',quotechar='\"')
        
        # We're hoping that vars returns the values in the right order...
        for securitygroup in list_security_groups:
            # Last object in securitygroup should be a list of Security_Group_Rules
            title_row = [value for value in vars(securitygroup).values() if type(value) is not list]
            write_row(c_writer,title_row)
            # TODO Currently writing the securitygroup id, not the actual values
            for securitygrouprule in securitygroup.list_Security_Group_Rules:
                row = [value for value in vars(securitygrouprule).values()]
                write_row(c_writer,row)
            
            # Separate Security Groups with a blank line
            c_writer.writerow([])
    
from createSecurityGroupObjects import get_security_groups_from_aws
from csv import writer
from boto3 import client
from shutil import copyfile
from os import rename
from re import split,IGNORECASE

# Copy CSV File and rename to old
# TODO: Handle absolute path symbols correctly. Currently can't pass './'
# TODO: copying file doesn't copy all sheets on the csv 
def copy_file (filename):
   try:
      # this might not work, using parentheses instead of brackets might return the symbols which could be annoying
      name = split('[\_|.]', filename, flags=IGNORECASE)
      
      # looking for the part of the filename that doesn't include _latest, if that exists
      if 'latest' in name:
         appendage = 2
      else:
         appendage = 1
          
      part = ''.join(name[0:(len(name)-appendage):])   
      # len(name) - 1 should return the extension
      filename_old = '{}_old.{}'.format(part,name[len(name) - 1])
  
      rename(filename, filename_old) 
      
      if '_latest' not in name:
         filename = '{}_latest.{}'.format(part,name[len(name) - 1])
          
      copyfile(filename_old,filename)
   except(FileNotFoundError):
      pass
        
# Uses the Security_Group object from SecurityGroupClassDef.py
def write_row (csv_writer,args):
   try:
      csv_writer.writerow(args)
   except:
      with open('./security_group_error_log.txt', 'r+', newline='\n') as errorlog:
            errorlog.write('Unable to write line: ', ' '.join(map(str, a)))
    
def write_security_group_CSV(csv_file, list_security_groups):
   copy_file(csv_file)
   with open(csv_file,'w',newline='') as csvfile:
      c_writer = writer(csvfile,delimiter='^',quotechar='\"')
     
      # We're hoping that vars returns the values in the right order...
      for securitygroup in list_security_groups:
          # Last object in securitygroup should be a list of Security_Group_Rules
         title_row = [value for value in vars(securitygroup).values() if type(value) is not list]
         write_row(c_writer,title_row)
         for securitygrouprule in securitygroup.list_Security_Group_Rules:
            row = [value for value in vars(securitygrouprule).values()]
            write_row(c_writer,row)
         
         # Separate Security Groups with a blank line
         c_writer.writerow([])
    
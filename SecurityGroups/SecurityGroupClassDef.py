# Security_Group class definition:

# TODO Test passing a list_Security_Group_Rules value into init
class Security_Group:
    def __init__(self,key_name='',group_name='',vpc_id='',group_id='',description='',list_Security_Group_Rules=None):
        self.key_name = key_name
        self.group_name = group_name
        print(group_name)
        self.vpc_id = vpc_id
        self.group_id = group_id
        self.description = description
        self.list_Security_Group_Rules = []
        if list_Security_Group_Rules is not None:
            [self.add_existing_rule(rule) for rule in list_Security_Group_Rules]
                
        
    # TODO Handle -2 values throughout code - don't want to write -2 to csv or try to send it to AWS
    # TODO Handle -1 ip_protocol which means that all open
    class Security_Group_Rule:
        def __init__(self,ip_protocol=-2,from_port=-2,to_port=-2,cidr_ip='',description=''):
            self.ip_protocol = ip_protocol
            if type(from_port) is str:
                try:
                    self.from_port = int(from_port)
                except:
                    print ('unable to initialize from_port value. setting to -2, since -1 is a valid value')
                    self.from_port = -2
            else:
                self.from_port = from_port
            if type(to_port) is str:
                try:
                    self.to_port = int(to_port)
                except:
                    print ('unable to initialize to_port value. setting to -2, since -1 is a valid value')
                    self.to_port = -2
            else:
                self.to_port = to_port
            self.cidr_ip = cidr_ip
            self.description = description
            
          
    # TODO: I don't think this works
    def add_existing_rule(self,security_group_rule):
        self.list_Security_Group_Rules.append(security_group_rule)
        
    def add_new_rule(self,data):
        self.list_Security_Group_Rules.append(self.Security_Group_Rule(*data))
        print (self.list_Security_Group_Rules)

    # assumes arguments have the same keys - length comparison is performed in compare_sg
    def compare_values(self,first_vars,second_vars):
        
        for key in first_vars.keys():
            if type(first_vars[key]) is not list:
                if first_vars[key] != second_vars[key]:
                    return False
        return True
                
        
    # compares classes and returns true if all the values in them are identical       
    def compare_sg(self, other_security_group):
        self_values = vars(self)
        other_values = vars(other_security_group)
        
        if len(self_values) != len(other_values):
            return False
        
        if len(self.list_Security_Group_Rules) != len(other_security_group.list_Security_Group_Rules):
            return False
        
        if not self.compare_values(self_values,other_values):
            return False

        for self_rule in self.list_Security_Group_Rules:
            rule_found = False
            for other_rule in other_security_group.list_Security_Group_Rules:
                if self.compare_values(vars(self_rule),vars(other_rule)):
                    rule_found = True
                    break
            if not rule_found:
                return False
        return True
        
     
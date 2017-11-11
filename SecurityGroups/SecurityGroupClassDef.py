# Security_Group class definition:

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
        
        # returns non similar groups
        if not [False for i in range(0,len(self_values)) for key in self_values.keys() if self_values[key] != other_values[key] ]:
            return True
        else:
            return False
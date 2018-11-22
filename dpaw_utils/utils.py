class RangeChoice(dict):
    """
     a dict object which key is choosed against a range
     choices is a list of tuple or list with 2 members. the first member is a number, the second member is the value
    """
    def __init__(self,choices,operator="lt"):
        self.choices = choices or []
        self.operator = getattr(self,"_{}".format(operator))

    def _lt(self,choice_value,value):
        return choice_value is None or value < choice_value

    def _lte(self,choice_value,value):
        return choice_value is None or value <= choice_value

    def _gt(self,choice_value,value):
        return choice_value is None or value > choice_value

    def _gt(self,choice_value,value):
        return choice_value is None or value >= choice_value

    def __contains__(self,name):
        try:
            value = self[name]
            return True
        except:
            return False

    def __getitem__(self,name):
        for choice in self.choices:
            if self.operator(choice[0],name):
                return choice[1]

        raise KeyError("Key '{}' does not exist.".format(name))
        
    def __len__(self):
        return len(self.choices)

    def __str__(self):
        return str(self.choices)

    def __repr__(self):
        return repr(self.choices)

    def get(self,name,default=None):
        try:
            return self[name]
        except KeyError as ex:
            return default

class ConditionalChoice(dict):
    """
     a dict object which key is a object or a list or tuple
     choices is a list of tuple or list with 2 members. the first member is a lambda expression with the same parameters, the second member is the value
    """
    def __init__(self,choices,single_parameter = True):
        self.choices = choices or []
        self.single_parameter = single_parameter

    def __contains__(self,key):
        try:
            value = self[key]
            return True
        except:
            return False

    def __getitem__(self,key):
        for choice in self.choices:
            if self.single_parameter:
                if choice[0](key):
                    return choice[1]
            else:
                if choice[0](*key):
                    return choice[1]


        raise KeyError("Key '{}' does not exist.".format(key))
        
    def __len__(self):
        return len(self.choices)

    def __str__(self):
        return str(self.choices)

    def __repr__(self):
        return repr(self.choices)

    def get(self,key,default=None):
        try:
            return self[key]
        except KeyError as ex:
            return default


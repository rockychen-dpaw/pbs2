import hashlib
import imp
import sys
import os


def hashvalue(value):
    m = hashlib.sha1()
    m.update(value.encode('utf-8'))
    return m.hexdigest()
    
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

def load_module(name,base_path="."):
    # Fast path: see if the module has already been imported.
    try:
        return sys.modules[name]
    except KeyError:
        pass
    
    path,filename = os.path.split(name.replace(".","/"))
    if not path.startswith("/"):
        base_path = os.path.realpath(base_path)
        path = os.path.join(base_path,path)

    # If any of the following calls raises an exception,
    # there's a problem we can't handle -- let the caller handle it.

    fp, pathname, description = imp.find_module(filename,[path])

    try:
        return imp.load_module(name, fp, pathname, description)
    finally:
        # Since we may exit via an exception, close fp explicitly.
        if fp:
            fp.close()

def filesize(f):
    if f:
        size = f.size
        if size < 1024:
            return "{} B".format(size)
        elif size < 1048576:
            return "{} K".format(round(size / 1024,2))
        elif size < 1073741824:
            return "{} M".format(round(size / 1048576,2))
        else:
            return "{} G".format(round(size / 1073741824,2))

    else:
        return None


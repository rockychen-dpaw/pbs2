from collections import OrderedDict
import hashlib

def hashvalue(value):
    m = hashlib.sha1()
    m.update(value.encode('utf-8'))
    return m.hexdigest()
    

class FieldClassConfigDict(dict):
    """
    Try to get the value of the key using the following logic
    1. if key exists in the dict, return it directly if its value is not None; if its value is None, means key doesn't exist,
    2. if name part of the key exists in the dict, return it directly if its value is not None; if its value is None, means key doesn't exist,
    3. if the key "[default_key_name].[purpose]" exists in the dict, return it directly if its value is not None; if its value is None, means key doesn't exist,
    4. if the key "[default_key_name]" exists in the dict, return it directly if its value is not None; if its value is None, means key doesn't exist,
    5. key doesn't exist,
    """
    def __init__(self,meta_class,dict_obj):
        super(FieldClassConfigDict,self).__init__()
        self.data = dict_obj if dict_obj is not None else {}
        self._meta_class = meta_class
        self._default_key_name =  "__default__"
        self._editable_fields = self._meta_class.editable_fields if self._meta_class and hasattr(self._meta_class,"editable_fields") else None
        self._purpose = self._meta_class.purpose if self._meta_class and hasattr(self._meta_class,"purpose") else None

    def purpose(self,name):
        if self._purpose:
            if "edit" in self._purpose:
                return self._purpose if (self._editable_fields is None or name in self._editable_fields) else "view"
            else:
                return self._purpose
        else:
            return "edit" if (self._editable_fields is None or name in self._editable_fields) else "view"

    def search_keys(self,name,purpose=None):
        purpose = purpose or self.purpose(name)
        if isinstance(purpose,str):
            if self._meta_class.is_editable_dbfield(name):
                return ("{}.{}".format(name,purpose),name)
            else:
                return ("{}.{}".format(name,purpose),name,"{}.{}".format(self._default_key_name,purpose),self._default_key_name)
        else:
            if self._meta_class.is_editable_dbfield(name):
                keys = ["{}.{}".format(name,p) for p in purpose]
                keys.append(name)
                return keys
            else:
                keys =["{}.{}".format(name,p) for p in purpose]
                keys.append(name)
                for p in purpose:
                    keys.append("{}.{}".format(self._default_key_name,p))
                keys.append(self._default_key_name)
                return keys

    def __contains__(self,name):
        for key in self.search_keys(name):
            if key in self.data:
                return False if self.data[key] is None else True

        return False

    def __getitem__(self,name):
        return self.get_config(name)
        
    def __len__(self):
        return len(self.data) if self.data else 0

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return repr(self.data)

    def get(self,name,default=None):
        try:
            return self[name]
        except KeyError as ex:
            return default


    def get_config(self,name,purpose=None):
        if name=="approval_expiry":
            pass
        for key in self.search_keys(name,purpose):
            try:
                value = self.data[key]
                if value is None:
                    raise KeyError(name)
                return value
            except:
                pass
        raise KeyError(name)

class FieldWidgetConfigDict(FieldClassConfigDict):
    """
    Try to get the value of the key using the following logic
    1. if key exists in the dict, return it directly if its value is not None; if its value is None, means key doesn't exist,
    2. if name part of the key exists in the dict, return it directly if its value is not None; if its value is None, means key doesn't exist,
    3. if the key "[default_key_name].[purpose]" exists in the dict, return it directly if its value is not None; if its value is None, means key doesn't exist,
    4. if the key "[default_key_name]" exists in the dict, return it directly if its value is not None; if its value is None, means key doesn't exist,
    5. key doesn't exist,
    """

    def search_keys(self,name,purpose=None):
        purpose = purpose or self.purpose(name)
        if isinstance(purpose,str):
            if purpose == 'edit' and self._meta_class.is_dbfield(name):
                return ("{}.{}".format(name,purpose),name)
            else:
                return ("{}.{}".format(name,purpose),"{}.{}".format(self._default_key_name,purpose),self._default_key_name)
        else:
            if "edit" in purpose and self._meta_class.is_dbfield(name):
                keys = ["{}.{}".format(name,p) for p in purpose]
                keys.append(name)
                return keys
            else:
                keys = ["{}.{}".format(name,p) for p in purpose]
                for p in purpose:
                    keys.append("{}.{}".format(self._default_key_name,p))
                keys.append(self._default_key_name)
                return keys

class SubpropertyEnabledDict(dict):
    """
    Support recursive dict structure; that means, the value of dict key can be a dict object.
    Compund key "key.subkey.subkey" can be used to access the value from inner dict object.
    """
    def __init__(self,dict_obj):
        super(SubpropertyEnabledDict,self).__init__()
        self.data = dict_obj

    def __contains__(self,name):
        if not self.data: return False

        pos = name.find("__")
        if pos >= 0:
            name = name[0:pos]

        return name in self.data

    def __getitem__(self,name):
        if self.data is None: raise TypeError("dict is None")

        pos = name.find("__")
        if pos >= 0:
            names = name.split("__")
            result = self.data
            for key in names:
                if not result: raise KeyError(name)
                try:
                    result = result[key]
                except KeyError as ex:
                    raise KeyError(name)

            return result
        else:
            return self.data[name]

    def __setitem__(self,name,value):
        if self.data is None: raise TypeError("dict is None")

        pos = name.find(".")
        if pos >= 0:
            names = name.split("__")
            result = self.data
            for key in names[0:-1]:
                try:
                    result = result[key]
                except KeyError as ex:
                    #key does not exist, create one
                    result[key] = {}
                    result = result[key]

            result[names[-1]] = value
        else:
            self.data[name] = value

    def __len__(self):
        return len(self.data) if self.data else 0

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return repr(self.data)

    def get(self,name,default=None):
        try:
            return self.__getitem__(name)
        except KeyError as ex:
            return default

class ChainDict(dict):
    """
    A dict object which consist of a array of dict objects.
    The value of a key is the value of the key in the first dict object.
    The the key doesn't exist in all dict objects, then KeyError will be thrown
    """
    def __init__(self,dict_objs):
        super(ChainDict,self).__init__()
        if isinstance(dict_objs,list):
            self.dicts = dict_objs
        elif isinstance(self.dicts,tuple):
            self.dicts = list(dict_objs)
        elif isinstance(self.dicts,dict):
            self.dicts = [dict_objs] 
        else:
            self.dicts = [dict(dict_objs)] 

    def __contains__(self,name):
        for d in self.dicts:
            if name in d:
                return True 
        return False

    def __getitem__(self,name):
        for d in self.dicts:
            try:
                return d[name]
            except:
                continue

        raise KeyError(name)

    def __len__(self):
        """
        return 1 if has value;otherwise return 0
        """
        for d in self.dicts:
            if d:
                return 1 
                
        return 0

    def __str__(self):
        return [str(d) for d in self.dicts]

    def __repr__(self):
        return [repr(d) for d in self.dicts]

    def get(self,name,default=None):
        for d in self.dicts:
            try:
                return d[name]
            except:
                continue

        return default

    def update(self,dict_obj):
        self.dicts.insert(0,dict_obj)


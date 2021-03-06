RAISE_EXCEPTION=548235490564654     #magic number

class XserProperty(object):
    def __init__(self, value):
        self.value=value

def set_xser_prop(obj, prop_name, value):
    assert not hasattr(obj, prop_name)
    assert not isinstance(value, XserProperty)
    prop= XserProperty(value)
    setattr(obj, prop_name, prop)

def get_xser_prop(obj, prop_name, default=RAISE_EXCEPTION):
    prop= getattr(obj,prop_name,None)
    if not isinstance(prop, XserProperty) or prop==None:
        if default== RAISE_EXCEPTION:
            raise AttributeError('The object %s has no suitable attribute %s' %(str(obj), prop_name))
        else:
            return default
    else:
        return prop.value

def has_xser_prop(obj, prop_name):
    try:
        get_xser_prop(obj, prop_name)
        return True
    except:
        return False

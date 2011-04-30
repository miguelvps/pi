#example call for REST methods:
# constant_generator( ['GET', 'PUT'], locals())

def constant_generator(l, locals_dictionary):
    '''given a string list ( a list of names of constants), and the locals(),
    this function assigns each constant a number and registers them as variables'''
    for v,k in enumerate(l):
        #make each method available as a variable.
        locals_dictionary[ k ] = v
        locals_dictionary[ k.lower() ] = v
        locals_dictionary[ k.upper() ] = v

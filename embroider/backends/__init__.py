import os.path

import embroider.backends.fortran

def get_processor(filename):
    ret = None
    
    base, ext = os.path.splitext(filename)
    if len(ext) == 0:
        ext = base
        
    ret = None
    
    if ext in fortran.extensions:
        ret = (fortran.process, fortran.name, fortran.headings)
        
    return ret
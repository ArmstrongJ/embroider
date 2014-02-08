import re

extensions = ['.f90', '.f03', '.f08']
name = 'Fortran Free-Format'
headings = {'proc_name':  "Procedures",
            'struct_name': "Derived Types",
            'constant_name': "Parameters"}

patterns = { 'module': re.compile("(?i)^\\s*module\s+(?P<name>\\w[\\w_\\d]*)"),
             'subroutine': re.compile("(?i)^\\s*(?:pure\\s+)?(?:recursive\\s+)?subroutine\\s+(?P<name>[\\w_\\d]+)\\s*\\(?"),
             'function': re.compile("(?i)^\\s*(?:pure\\s+)?(?:recursive\\s+)?function\\s+(?P<name>[\\w_\\d]+)\\s*\\(?"),
             'interface': re.compile("(?i)^\\s*interface\s+(?P<name>\\w[\\w_\\d]*)"),
            }
end_patterns = { 'module':re.compile("(?i)^\\s*end\\s+module"),
                 'subroutine': re.compile("(?i)^\\s*end\\s+subroutine"),
                 'function': re.compile("(?i)^\\s*end\\s+function"),
                 'interface': re.compile("(?i)^\\s*end\\s+interface"),
                }
                    
debug = False

def check_start(line):
    element = None
    for k in patterns.keys():
        m = re.match(patterns[k], line)
        if m is not None:
            element = {'type':k, 'declaration':line.strip(), 'name':m.group('name'), 
                       'children':[]}
            break
    
    return element
    
def check_end(line):
    ending = None
    for k in end_patterns.keys():
        m = re.match(end_patterns[k], line)
        if m is not None:
            ending = k
            break
            
    return ending

def sort_container(e):
    e['procedures'] = []
    e['constants'] = []
    e['structs'] = []
    e['containers'] = []
    
    for c in e['children']:
        if c['type'] == 'module':
            e['containers'].append(c)
        elif c['type'] == 'subroutine':
            e['procedures'].append(c)
        elif c['type'] == 'function':
            e['procedures'].append(c)
        elif c['type'] == 'interface':  # Put interfaces here as well
            e['procedures'].append(c)
        elif c['type'] == 'parameter':
            e['constants'].append(c)
        elif c['type'] == 'type':
            e['structs'].append(c)
            
    for key in ['procedures', 'constants', 'structs', 'containers']:
        if len(e[key]) == 0:
            e[key] = None

def organize_node_elements(e):
    """Sorts children of an element into parameters, derived types, and
    procedures"""
    
    if e['type'] == 'module' or e['type'] == 'file':
        sort_container(e)

def process(text):
    """This processor is designed to handle well-formed, free-format Fortran.
    It will invariably fail when used with fixed-format source code.
    Subprograms, modules, and interfaces should have at least partially
    explicit "end" statements (e.g. "end module" as opposed to just "end").
    Argument declarations need to use the "::" format."""
    
    ret = []
    
    head = {'children':ret, 'parent':None, 'type':'file'}
    current = head
    
    # This is Fortran, should be easy
    lines = text.splitlines()
    
    for i in range(0, len(lines)):
        
        element = check_start(lines[i])
        ending = check_end(lines[i])
        
        if element is not None:
            element['parent'] = current
            current['children'].append(element)
            
            current = element
            
            if debug:
                print("{0} named '{1}' on line {2}".format(element['type'], element['name'], i))
        
        elif ending is not None:
            
            while ending != current['type'] and current['type'] != 'file':
                organize_node_elements(current)
                current = current['parent']
                
            if current['type'] != 'file':
                organize_node_elements(current)
                current = current['parent']
        
    
    return ret
    
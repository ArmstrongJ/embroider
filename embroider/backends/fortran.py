import re
import io

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
        elif c.get('parameter'):
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
        
def handle_arguments(e):
    """Pulls arguments from a definition"""
    p = re.compile("(?i)^\\s*(?:pure\\s+)?(?:recursive\\s+)?(?:subroutine|function)\\s+(?:\\w[\\w_\\d]*)\\s*\\((?P<args>[\\s\\w_\\d,]+)\\)")
    m = re.match(p, e['declaration'])
    if m is None:
        e['arguments'] = []
    else:
        e['arguments'] = [{"name":x.strip(), "description":None, "type":None} for x in m.group('args').split(",")]

def check_variable_declarations(line):
    """Looks for variable declarations"""
    p_base = re.compile("(?i)^\\s*(?P<type>(integer|real|logical|complex|character|type\\().*)::")
    m = re.match(p_base, line)
    
    if m is None:
        return None
        
    vtype = m.group("type").strip()
    parameter = "parameter" in vtype.lower()
    optional = "optional" in vtype.lower()
    
    p_repl_param = re.compile("(?i)(,\\s*parameter)")
    vtype = re.sub(p_repl_param, "", vtype)
    
    p_repl_opt = re.compile("(?i)(,\\s*optional)")
    vtype = re.sub(p_repl_opt, "", vtype).strip()
    
    p_desc = re.compile("(?P<desc>!.*)$")
    m_desc = re.match(p_desc, vtype)
    if m_desc is None:
        description = None
    else:
        description = m_desc.group('desc')[1:].strip()
        vtype = re.sub(p_desc, "", vtype)
    
    # Should have all necessary type information, so now pull the names
    names_i = line.find("::")
    varnames = line[names_i+2:]
    variables = varnames.split(",")
    
    p_cleanname = re.compile("(?i)^(?P<name>\\w[\\w\\d_]*)[\\s,=]*")
    variables = [re.match(p_cleanname, v.strip()).group("name") for v in variables if re.match(p_cleanname, v.strip())  is not None]
    
    return [{'name':v, 'type':vtype, 'parameter':parameter, 
             'description':description, 'optional':optional} 
                for v in variables]

def check_return_value(e):
    """Processes function elements to determine the name of the return value"""
    p_ret = re.compile("(?i)\\s+result\\s*\\(\\s*(?P<var>\\w[\\w\\d_]*)\\s*\\)")
    m = re.match(p_ret, e['declaration'])
    if m is None:
        e['return_name'] = e['name']
    else:
        e['return_name'] = m.group('var')
        

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
    
    running_comment = None
    for i in range(0, len(lines)):
        
        lines[i] = lines[i].strip()
        
        element = check_start(lines[i])
        ending = check_end(lines[i])
        
        if element is not None:
            element['parent'] = current
            current['children'].append(element)
            
            current = element
            if current['type'] == "function" or current['type'] == "subroutine":
                handle_arguments(current)
                
            if current['type'] == "function":
                check_return_value(current)
            
            if running_comment is not None:
                current['description'] = running_commment.getvalue()
            
            if debug:
                print("{0} named '{1}' on line {2}".format(element['type'], element['name'], i))
        
        elif ending is not None:
            
            while ending != current['type'] and current['type'] != 'file':
                organize_node_elements(current)
                current = current['parent']
                
            if current['type'] != 'file':
                organize_node_elements(current)
                current = current['parent']
        
        else:
            variables = check_variable_declarations(lines[i])
            if variables is not None:
                for v in variables:
                    if v.get('description') is None and running_comment is not None:
                        v['description'] = running_comment.getvalue().strip()
                        
                    if current['type'] == 'function' or current['type'] == 'subroutine':
                        for arg in current['arguments']:
                            if v['name'] == arg['name']:
                                arg['type'] = v['type']
                                if v['description'] is None:
                                    v['description'] = ""
                                if v['optional']:
                                    v['description'] = "_(optional)_ "+v['description']
                                arg['description'] = v['description']
                                break
                    
                    if current['type'] == 'function' and v['name'] == current['return_name']:
                        current['return'] = {'type':v['type'],'description':v.get('description')}
                    
                    if current['type'] == 'type' or current['type'] == 'module':
                        current['children'].append(v)
        
        if running_comment is None:
            if lines[i].strip().startswith("!"):
                running_comment = io.StringIO(lines[i].strip()[1:].strip()+"\n")
        else:
            if lines[i].strip().startswith("!"):
                running_comment.write(lines[i].strip()[1:].strip()+"\n")
            else:
                running_comment.close()
                running_comment = None
    
    return ret
    
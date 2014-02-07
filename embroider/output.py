
def output_heading(heading, dest, level):
    """Outputs a section heading"""
    dest.write("h{0}. {1}\n\n".format(level, heading))

def output_general(element, heading, member, dest, level):
    """Outputs a component of the element as a simple string"""
    
    output_heading(heading, dest, level)
    
    if element[member] is None:
        dest.write("Not available\n\n")
    else:
        dest.write(element[member])
        dest.write("\n\n")

def output_description(element, dest, level):
    """Outputs the description component"""
    output_general(element, "Description", "description", dest, level)
    
def output_notes(element, dest, level):
    """Outputs notes, if available"""
    if element['notes'] is not None:
        output_general(element, "Notes", "notes", dest, level)

def output_arguments(element, dest, level):
    if element['arguments'] is None:
        return
        
    output_heading("Arguments", dest, level)
    
    dest.write("|Argument|Type|Description|\n")
    for x in element['arguments']:
        if x['type'] is None:
            x['type'] = " "
        if x['description'] is None:
            x['description'] = " "
        dest.write("|{name}|{type}|{description}|\n".format(**x))
    
    dest.write("\n")
    
def output_return(element, dest, level):
    if element['return'] is None:
        return
    
    output_heading("Return", dest, level)
    
    if element['return']['type'] is not None:
        dest.write('**{0}**\n\n'.format(element['return']['type']))
    
    if element['return']['description'] is None:
        dest.write("Not available\n\n")
    else:
        dest.write(element['return']['description'])
        dest.write("\n\n")

def output_procedure(element, dest, level):
    output_heading(element['name'], dest, level)
    
    if element['declaration'] is not None:
        dest.write("**{0}**\n\n".format(element['declaration']))
        
    output_description(element, dest, level+1)
    output_arguments(element, dest, level+1)
    output_return(element, dest, level+1)
    output_notes(element, dest, level+1)
    
def output_constants(elements, dest):
    dest.write("|Id|Type|Value|Description|\n")
    for x in elements:
        if x["type"] is None:
            x["type"] = " "
        if x["description"] is None:
            x["description"] = " "
        if x["value"] is None:
            x["value"] = " "
            
        dest.write("|{name}|{type}|{value}|{description}|\n".format(**x))
    dest.write("\n")
    
def output_struct_components(components, dest, indent):
    for x in components:
        dest.write("".join(["*" for i in range(0, indent)]))
        dest.write(" {0}".format(x['name']))
        
        if x['type'] is not None:
            dest.write(" - **{0}**".format(x['type']))
            
        if x['description'] is not None:
            dest.write(" - {0}".format(x['description']))
        
        dest.write("\n")
        
        if x['children'] is not None:
            output_struct_components(x['children'], dest, indent+1)
        
    dest.write("\n")
    
def output_struct(element, dest, level):
    output_heading(element['name'], dest, level)
    
    if element['description']:
        dest.write("{0}\n\n".format(element['description']))
    
    output_struct_components(element['children'], dest, 1)
    
def output_container(element, dest, level, 
                     constant_name="Constants", 
                     struct_name="Structs/Unions",
                     proc_name="Procedures"):
                     
    heading = element['name']
    if element['type'] is not None:
        heading = heading + " " + element["type"]
    
    if element['constants'] is not None:
        output_heading(constant_name, dest, level+1)
        output_constants(element['constants'])
    
    if element['structs'] is not None:
        output_heading(struct_name, dest, level+1)
        for x in element['structs']:
            output_struct(x, dest, level+2)
    
    if element['procedures'] is not None:
        output_heading(proc_name, dest, level+1)
        for x in element['procedures']:
            output_procedure(x, dest, level+2)

def output_to_file(container, filename,
                   constant_name="Constants", 
                   struct_name="Structs/Unions",
                   proc_name="Procedures"):
    
    with open(filename, "wt") as dest:
        if hasattr(container, "__iter__"):
            for c in container:
                output_container(c, dest, 1, 
                                 constant_name=constant_name,
                                 struct_name=struct_name,
                                 proc_name=proc_name)
        else:
            output_container(c, dest, 1, 
                             constant_name=constant_name,
                             struct_name=struct_name,
                             proc_name=proc_name)
    
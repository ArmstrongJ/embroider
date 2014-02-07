import os
import os.path

import embroider.backends
import embroider.output

ignored = ['CVS', '__pycache__', 'build', 'modules']

def process_file(filename, output_file=None, output_dir=".", processor=None):
    if processor is None:
        processor = embroider.backends.get_processor(filename)
        
    if processor is None:
        print("WARN: No processor found for {0}".format(filename))
        return
    else:
        print("Processing {0} using {1}...".format(filename, processor[1]))
    
    print("   * Loading...")
    text = ""
    with open(filename, 'r') as fp:
        text = fp.read()
        
    print("   * Parsing...")
    tree = processor[0](text)
    
    if output is None:
        output, ext = os.path.splitext(filename)
        output = output + ".textile"
        
    output_file = output
    if output_dir is not None:
        output_file = os.path.join(output_dir, output_file)
        
    print("   * Writing {0}...".format(output))
    if len(processor) == 3:
        embroider.output.output_to_file(tree, output_file,  **processor[2])
    else:
        embroider.output.output_to_file(tree, output_file)
    
    print("   * Done")


def process_directory(directory, output_dir="."):
    """Walks the directory tree starting at the specified location,
    processing all source files encoutered along the way"""
    count = 0
    for root, dirs, files in os.walk(directory):
        for f in files:
            count = count + 1
            process_file(os.path.join(root, f), output_dir=output_dir)
        
        removal = [d for d in dirs if d.startswith(".")]
        for d in removal + ignored:
            try:
                dirs.remove(d)
            except ValueError:
                pass
        
    print("{0} files processed".format(count))

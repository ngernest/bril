import json 
import sys 
from collections import OrderedDict

TERMINATORS = ('jmp', 'br', 'ret')

# List[Instr] -> List[List[Instr]]
def form_blocks(body):
    """Forms a basic block containing the instructions in `body`
    """

    blocks = []
    cur_block = []

    for instr in body:
        if 'op' in instr:   # an actual instruction
            cur_block.append(instr)

            # Check for terminator (yield the current block to the client)
            if instr['op'] in TERMINATORS:
               blocks.append(cur_block)
               cur_block = [] 
               
        else:   # A label 

            # Only yield blocks that contain non-zero no. of instructions
            if cur_block:
                blocks.append(cur_block)

            # Put the label in the next basic block
            cur_block = [instr]
    
    if cur_block:
        blocks.append(cur_block)
    
    return blocks

# List[Block] -> Dict[String, Block]
def block_map(blocks):
    """Creates labels for a list of blocks 
    (generating fresh labels when necessary)
    """
    out = OrderedDict()

    for block in blocks:
        # A label already exists (first instruction in the block)
        if 'label' in block[0]:
            name = block[0]['label']
            block = block[1:]
        else:
            name = 'b{}'.format(len(out))

        out[name] = block  

    return out 

def get_cfg(name2block):
    """Given a name-to-block map, produces a map from block names to 
    successor block names
    """
    out = dict()
    for i, (name, block) in enumerate(name2block.items()):
        last = block[-1]
        if last['op'] in ('jmp', 'br'):
            succ = last['labels']
        elif last['op'] == 'ret':
            succ = []
        else:
            # We've reached the last instruction in the block
            if i == len(name2block) - 1:
                succ = []
            else:
                # We fall through to the next block in `name2block`
                succ = [list(name2block.keys())[i + 1]]

        out[name] = succ
    return out 
 

# Constructs a CFG for a Bril program
def mycfg():
    prog = json.load(sys.stdin)
    for func in prog['functions']:
        # Get labelled basic blocks
        name2block = block_map(form_blocks(func['instrs']))
        for name, block in name2block.items():
            print(name)
            print('  ', block)

        cfg = get_cfg(name2block)
        
        # Produce GraphViz visualization
        print('digraph {} {{'.format(func['name']))
        for name in name2block:
            print('  {};'.format(name))
        for name, succs in cfg.items():
            for succ in succs:
                print('  {} -> {};'.format(name, succ))
        print('}')


if __name__ == '__main__':
    mycfg()    
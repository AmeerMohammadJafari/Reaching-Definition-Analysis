import re
import networkx as nx

# Function to extract action name and (kill)/(gen) sets based on specific patterns
def extract_action_info(action_str):
    # Define regular expressions for each pattern
    patterns = {
        r'(\w+)\s*:=\s*(.+)$': 'assign',     # Pattern for x := a
        r'(\w+)\s*\[\s*(\w+)\s*\]\s*:=\s*(.+)$': 'array_assign',  # Pattern for A[a1] := a2
        r'(\w+)\s*\?\s*(\w+)': 'read',        # Pattern for c?x
        r'(\w+)\s*\?\s*(\w+)\s*\[\s*(\w+)\s*\]': 'array_read',    # Pattern for c?A[a]
        r'(\w+)\s*!\s*(\w+)': 'write'         # Pattern for c!a
    }
    
    
    
    # Iterate over patterns and check for a match
    for pattern, action_name in patterns.items():
        match = re.match(pattern, action_str)
        if match:
            if action_name == 'assign' or action_name == 'array_assign':
                return (action_name, match.groups()[0])
            if action_name == 'read' or action_name == 'array_read':
                return (action_name, match.groups()[1])
            if action_name == 'write':
                return (action_name, None)
            
        

    # List of operators and boolean values
    operators = ['=','!=', '<=', '>=', '<', '>', 'true', 'false', '!']

    # If no match found, check for operators and boolean values
    for op in operators:
        if op in action_str:
            return 'boolean', None  # Return 'boolean' with empty (kill) and (gen) sets
        
    
    # Treat 'skip' as a special action
    if action_str == 'skip':
        return 'skip', None  # Return 'skip' with empty (kill) and (gen) sets
    
    # If no match found, return None with empty (kill) and (gen) sets
    return None, None
    


# Function to build the directed graph from input file
def build_graph_from_file(file_name):
    G = nx.DiGraph()
    variables = set()
    arrays = set()
    with open(file_name, 'r') as file:
        num_nodes, num_edges = map(int, file.readline().split())
        edges = []
        for _ in range(num_edges):
            start_node, end_node, action_str = file.readline().split()
            edges.append((start_node, end_node))
            action_name, z = extract_action_info(action_str)
            G.add_edge(start_node, end_node, action=action_name, variable=z, kill={}, gen={})


    for start_node, end_node, data in G.edges(data=True):
        action_name = data['action']
        data['kill'] = set()  # Initialize kill set as empty set
        data['gen'] = set()   # Initialize gen set as empty set
        
        if action_name == 'assign':
            variables |= {data['variable']}
            data['kill'].update({(data['variable'], q0, q1) for q0, q1 in edges})
            data['kill'].add((data['variable'], -1, 0))
            data['gen'].update({(data['variable'], start_node, end_node)})
        elif action_name == 'array_assign':
            arrays |= {data['variable']}
            data['gen'].add((data['variable'], start_node, end_node))
        elif action_name == 'read':
            variables |= {data['variable']}
            data['kill'].update({(data['variable'], q0, q1) for q0, q1 in edges})
            data['kill'].add((data['variable'], -1, 0))
            data['gen'].update({(data['variable'], start_node, end_node)})
        elif action_name == 'array_read':
            arrays |= {data['variable']}
            data['gen'].add((data['variable'], start_node, end_node))
    G.graph['variables'] = variables
    G.graph['arrays'] = arrays
    return G, edges


def analysis(graph, edges):
    RD = [set() for _ in graph.nodes()]
    RD[0] |= {(x, '?', 0) for x in graph.graph['variables']}
    RD[0] |= {(x, '?', 0) for x in graph.graph['arrays']}



    while True:
        flag = False
        for (q0, q1) in edges:
            if not (((RD[int(q0)] - graph.get_edge_data(q0, q1)['kill']) | graph.get_edge_data(q0, q1)['gen']) <= RD[int(q1)]):
                flag = True
                RD[int(q1)] = RD[int(q1)] | ((RD[int(q0)] - graph.get_edge_data(q0, q1)['kill']) | graph.get_edge_data(q0, q1)['gen'])
        if not flag:
            break



    for i, entry in enumerate(RD):
        print(f"RD[{i}]:", entry)


# Example usage
input_file = "pg1.txt"
graph, edges = build_graph_from_file(input_file)
analysis(graph, edges)
print('-----------------------------------------------------------------------------------------------------------')

input_file = "pg2.txt"
graph, edges = build_graph_from_file(input_file)
analysis(graph, edges)

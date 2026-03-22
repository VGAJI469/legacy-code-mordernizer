import networkx as nx
import re

class DependencyGraph:

    def __init__(self):
        self.graph = nx.DiGraph()

    def extract_functions(self, code):
        pattern = r'(public|private|protected)?\s+\w+\s+(\w+)\s*\('
        return [match[1] for match in re.findall(pattern, code)]

    def extract_calls(self, code):
        calls = re.findall(r'(\w+)\(', code)

        # Filter out common keywords / noise
        ignore = {
            "if", "for", "while", "switch",
            "System", "out", "println", "return"
        }

        return [call for call in calls if call not in ignore]

    def build(self, files):
        for file, code in files.items():

            functions = self.extract_functions(code)

            for func in functions:
                self.graph.add_node(func)

                # Extract ONLY this function's body
                pattern = rf'\b{func}\s*\([^)]*\)\s*\{{([\s\S]*?)\}}'
                match = re.search(pattern, code)

                if match:
                    function_body = match.group(1)
                    calls = self.extract_calls(function_body)

                    for call in calls:
                        if call != func and call in functions:
                            self.graph.add_edge(func, call)
                else:
                    continue

        return self.graph
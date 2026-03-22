import re
import networkx as nx
from scaledown import compress_code   # uses your ScaleDown API

MAX_TOKENS = 50   # small for demo, later increase to 4096


# -------------------------
# CLEANING
# -------------------------
def remove_comments(code):
    code = re.sub(r'//.*', '', code)
    code = re.sub(r'/\*[\s\S]*?\*/', '', code)
    code = re.sub(r'\n\s*\n', '\n', code)
    return code.strip()


# -------------------------
# TOKEN ESTIMATION
# -------------------------
def estimate_tokens(text):
    return len(text.split())


# -------------------------
# ENTRY POINT DETECTION
# -------------------------
def find_entry_points(graph):
    entry_points = [node for node in graph.nodes if graph.in_degree(node) == 0]

    # Prefer main if exists
    if "main" in graph.nodes:
        return ["main"]

    return entry_points


# -------------------------
# ACTIVE FUNCTION DETECTION
# -------------------------
def get_active_functions(graph):
    entry_points = find_entry_points(graph)

    active = set()

    for entry in entry_points:
        stack = [entry]

        while stack:
            node = stack.pop()
            if node not in active:
                active.add(node)
                stack.extend(list(graph.successors(node)))

    return list(active)


# -------------------------
# FUNCTION EXTRACTION
# -------------------------
def extract_relevant_code(files, functions):
    result = ""

    for file, code in files.items():
        for func in functions:

            pattern = rf'\b{func}\s*\([^)]*\)\s*\{{([\s\S]*?)\}}'
            match = re.search(pattern, code)

            if match:
                result += f"{func}() {{\n{match.group(1)}\n}}\n\n"

    return result


# -------------------------
# MAIN OPTIMIZER
# -------------------------
class ContextOptimizer:

    def optimize(self, files, graph):

        total_functions = list(graph.nodes)

        # Step 1: Active functions
        active_functions = get_active_functions(graph)

        # Step 2: Dead functions
        dead_functions = set(total_functions) - set(active_functions)

        # Step 3: Extract relevant code
        raw_code = extract_relevant_code(files, active_functions)

        tokens_before = estimate_tokens(raw_code)

        compression_used = False

        # Save BEFORE compression for demo
        before_compression = raw_code

        # 🔥 COMPRESS RAW CODE (max impact)
        if tokens_before > MAX_TOKENS:
            print("⚡ Applying ScaleDown compression...")

            compressed_code = compress_code(raw_code)

            if compressed_code and len(compressed_code.strip()) > 0:
                intermediate_code = compressed_code
                compression_used = True
            else:
                intermediate_code = raw_code
        else:
            intermediate_code = raw_code

        # Step 4: Clean AFTER compression
        clean_code = remove_comments(intermediate_code)

        tokens_after = estimate_tokens(clean_code)

        # Save AFTER compression for demo
        after_compression = clean_code

        # Step 5: Reduction %
        reduction = 0
        if tokens_before > 0:
            reduction = ((tokens_before - tokens_after) / tokens_before) * 100

        return {
            "optimized_code": clean_code,
            "tokens_before": tokens_before,
            "tokens_after": tokens_after,
            "reduction": reduction,
            "compression_used": compression_used,
            "total_functions": len(total_functions),
            "active_functions": len(active_functions),
            "dead_functions": len(dead_functions),
            "dead_function_list": list(dead_functions),
            "before_compression": before_compression,
            "after_compression": after_compression
        }
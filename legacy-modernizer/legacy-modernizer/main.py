from ingester import CodeIngester
from dependency_graph import DependencyGraph
from context_optimizer import ContextOptimizer

# Input
source = input("Enter repo path or GitHub URL: ")

# Load repo
ingester = CodeIngester(source)
files = ingester.load()

print("\nLoaded files:")
for f in files:
    print(f)

print("\nFiles loaded:", len(files))

# Build graph
graph = DependencyGraph().build(files)

print("\nNodes:", graph.number_of_nodes())
print("Edges:", graph.number_of_edges())

# Optimize
optimizer = ContextOptimizer()
result = optimizer.optimize(files, graph)

# Output
print("\n--- OPTIMIZED CODE ---\n")
print(result["optimized_code"])

print("\n--- METRICS ---")
print("Total Functions:", result["total_functions"])
print("Active Functions:", result["active_functions"])
print("Dead Functions Removed:", result["dead_functions"])
print("Tokens Before:", result["tokens_before"])
print("Tokens After:", result["tokens_after"])
print(f"Reduction: {result['reduction']:.2f}%")

print("\nDead Functions List:", result["dead_function_list"])


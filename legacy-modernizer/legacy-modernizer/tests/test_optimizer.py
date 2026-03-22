from ingester import CodeIngester
from dependency_graph import DependencyGraph
from context_optimizer import ContextOptimizer

def test_token_reduction():

    ingester = CodeIngester("./sample_repo")
    files = ingester.load()

    graph = DependencyGraph().build(files)

    optimizer = ContextOptimizer()

    result = optimizer.optimize(files, graph, "main")

    print("Before:", result["tokens_before"])
    print("After:", result["tokens_after"])

    assert result["tokens_after"] <= result["tokens_before"]
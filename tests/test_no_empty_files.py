import ast
import glob
import os

def test_no_empty_test_files():
    test_dir = os.path.dirname(__file__)
    for path in glob.glob(os.path.join(test_dir, "test_*.py")):
        with open(path, "r", encoding="utf-8") as fh:
            content = fh.read().strip()
        assert content, f"{os.path.basename(path)} is empty"

        tree = ast.parse(content, filename=path)
        has_test = False
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_"):
                has_test = True
                break
            if isinstance(node, ast.ClassDef):
                for item in node.body:
                    if (
                        isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                        and item.name.startswith("test_")
                    ):
                        has_test = True
                        break
                if has_test:
                    break
        assert has_test, f"{os.path.basename(path)} contains no tests"

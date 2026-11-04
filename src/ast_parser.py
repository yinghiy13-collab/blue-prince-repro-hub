
import ast, json, hashlib
from pathlib import Path
def parse_py_to_miron(py_path: Path):
    code = py_path.read_text()
    tree = ast.parse(code)
    ir = {"file": str(py_path), "sha256": hashlib.sha256(code.encode()).hexdigest(), "functions": [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]}
    return ir
if __name__ == "__main__":
    import sys
    p = Path(sys.argv[1]) if len(sys.argv)>1 else Path("src/ast_parser.py")
    print(json.dumps(parse_py_to_miron(p), indent=2))

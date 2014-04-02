import ast

from tater import Visitor, Node


class _AstConverter(Visitor):

    def __init__(self):
        self.root = Node()

    def finalize(self):
        return self.root

    def generic_visit(self, node, iter_fields=ast.iter_fields, AST=ast.AST):
        """Called if no explicit visitor function exists for a node.
        """
        for field, value in iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, AST):
                        self.visit(item)
            elif isinstance(value, AST):
                self.visit(value)


def from_ast(
        pyast_node, node=None, node_cls=None, Node=Node,
        iter_fields=ast.iter_fields, AST=ast.AST):
    '''Convert the ast tree to a tater tree.
    '''
    node_cls = node_cls or Node
    node = node or node_cls()
    name = pyast_node.__class__.__name__

    attrs = []
    for field, value in iter_fields(pyast_node):
        if name == 'Dict':
            for key, value in zip(pyast_node.keys, pyast_node.values):
                if isinstance(value, list):
                    for item in value:
                        if isinstance(item, AST):
                            value = from_ast(item)
                elif isinstance(value, AST):
                    value = from_ast(value)
                attrs.append((key.s, value))
        else:
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, AST):
                        value = from_ast(item)
            elif isinstance(value, AST):
                value = from_ast(value)
            attrs.append((field, value))
    node.update(attrs, type=name)
    return node
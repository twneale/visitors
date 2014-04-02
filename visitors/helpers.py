# ---------------------------------------------------------------------------
# Helpers for figuring out the start/end indexes of a parse tree.
# ---------------------------------------------------------------------------
class IndexVisitor(Visitor):
    '''Base for visitors that aggregate information about
    string indices of modeled text.
    '''
    def __init__(self):
        self.indices = []


class StartIndexVisitor(IndexVisitor):
    '''This visitor finds the starting index of the left-most string
    modeled by the ast.
    '''
    def get_index(self):
        if self.indices:
            return min(self.indices)

    def generic_visit(self, node):
        for pos, token, text in node.tokens:
            self.indices.append(pos)


class EndIndexVisitor(IndexVisitor):
    '''This visitor finds the ending index of the right-most string
    modeled by the ast.
    '''

    def get_index(self):
        if self.indices:
            return max(self.indices)

    def generic_visit(self, node):
        '''The end index will be the `pos` obtained from
        the lexer, plus the length of the associated text.
        '''
        for pos, token, text in node.tokens:
            self.indices.append(pos + len(text))


def get_start(tree):
    return StartIndexVisitor().visit(tree).get_index()


def get_end(tree):
    return EndIndexVisitor().visit(tree).get_index()


def get_span(tree):
    return (get_start(tree), get_end(tree))


# ---------------------------------------------------------------------------
# Helpers for getting leaf nodes.
# ---------------------------------------------------------------------------
class LeafYielder(IteratorVisitor):

    def generic_visit(self, node):
        if not node.children:
            yield node


def get_leaf_nodes(node):
    return LeafYielder().itervisit(node)


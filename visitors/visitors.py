from visitors.base import Visitor


class TypeVisitor(Visitor):

    def get_nodekey(self, token):
        '''Given a particular token, check the visitor instance for methods
        mathing the computed methodnames (the function is a generator).
        '''
        for mro_type in type(token).__mro__:
            yield mro_type.__name__


class StreamVisitor(TypeVisitor):

    def visit(self, iterable, gentype=types.GeneratorType):
        '''The main visit function. Visits the passed-in node and calls
        finalize.
        '''
        self.iterable = iter(iterable)
        for token in self.iterable:
            result = self.visit_node(token)
            if isinstance(result, gentype):
                for output in result:
                    yield output
            elif result is not None:
                yield result
        result = self.finalize()
        if isinstance(result, gentype):
            for output in result:
                yield output


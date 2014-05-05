'''
Note: it's critical to visit a copy of node.children,
otherwise children might be mutated by the visitor
functions, causing the visitor to skip children
and not visit them.
'''
import types
import contextlib
from hercules import CachedClassAttr


class Continue(Exception):
    '''If a user-defined visitor function raises this exception,
    children of the visited node won't be visited.
    '''


class Break(Exception):
    '''If raised, the visit is immediately done,
    so stop and call finalize.
    '''


class Visitor(object):
    '''Define a generic_visit function to do the same
    thing on each node.

    '''
    Continue = Continue
    Break = Break

    # ------------------------------------------------------------------------
    # Define some class level types needed by the internals.
    # ------------------------------------------------------------------------
    GeneratorType = types.GeneratorType
    GeneratorContextManager = contextlib._GeneratorContextManager

    # ------------------------------------------------------------------------
    # Plumbing.
    # ------------------------------------------------------------------------
    @CachedClassAttr
    def _methods(cls):
        return {}

    @CachedClassAttr
    def _method_prefix(cls):
        return getattr(cls, 'method_prefix', 'visit_')
    # ------------------------------------------------------------------------
    # Define the default overridables.
    # ------------------------------------------------------------------------
    def apply_visitor_method(self, method_data, node):
        if hasattr(method_data, '__call__'):
            return method_data(self, node)
        elif isinstance(method_data, tuple):
            method = method_data[0]
            args = method_data[1:]
            return method(self, *args)

    def get_nodekey(self, node):
        '''Given a node, return the string to use in computing the
        matching visitor methodname. Can also be a generator of strings.
        '''
        yield node.__class__.__name__

    def get_children(self, node):
        '''Given a node, return its children.
        '''
        return node.children[:]

    def get_methodnames(self, node):
        '''Given a node, generate all names for matching visitor methods.
        '''
        nodekey = self.get_nodekey(node)
        prefix = self._method_prefix
        if isinstance(nodekey, self.GeneratorType):
            for nodekey in nodekey:
                yield self._method_prefix + nodekey
        else:
            yield self._method_prefix + nodekey

    def get_method(self, node):
        '''Given a particular node, check the visitor instance for methods
        mathing the computed methodnames (the function is a generator).

        Note that methods are cached at the class level.
        '''
        methods = self._methods
        for methodname in self.get_methodnames(node):
            if methodname in methods:
                return methods[methodname]
            else:
                cls = self.__class__
                method = getattr(cls, methodname, None)
                if method is not None:
                    methods[methodname] = method
                    return method

    def get_children(self, node):
        '''Override this to determine how child nodes are accessed.
        '''
        return node.children[:]

    def finalize(self):
        '''Final steps the visitor needs to take, plus the
        return value of .visit, if any.
        '''
        return self

    # ------------------------------------------------------------------------
    # Define the core functionality.
    # ------------------------------------------------------------------------
    def visit(self, node):
        '''The main visit function. Visits the passed-in node and calls
        finalize.
        '''
        tuple(self.itervisit(node))
        result = self.finalize()
        if result is not self:
            return result

    def itervisit(self, node):
        try:
            yield from self.itervisit_nodes(node)
        except self.Break:
            pass

    def itervisit_nodes(self, node):
        try:
            yield from self.itervisit_node(node)
        except self.Continue:
            return
        itervisit_nodes = self.itervisit_nodes
        for child in self.get_children(node):
            yield from itervisit_nodes(child)

    def itervisit_node(self, node):
        '''Given a node, find the matching visitor function (if any) and
        run it. If the result is a context manager, yield from all the nodes
        children before allowing it to exit. Otherwise, return the result.
        '''
        # Get the corresponding method and run it.
        func = self.get_method(node)
        if func is None:
            generic_visit = getattr(self, 'generic_visit', None)
            if generic_visit is not None:
                result = generic_visit(node)
            else:
                # There is no handler defined for this node.
                return
        else:
            result = self.apply_visitor_method(func, node)

        # If result is a generator, yield from it.
        if isinstance(result, self.GeneratorType):
            yield from result

        # If result is a context manager, enter, visit children, then exit.
        elif isinstance(result, self.GeneratorContextManager):
            with result:
                itervisit_nodes = self.itervisit_nodes
                for child in self.get_children(node):
                    try:
                        yield from itervisit_nodes(child)
                    except self.Continue:
                        continue

        # Otherwise just yield the result.
        else:
            yield result

    def visit_node(self, node):
        for result in self.itervisit_node(node):
            return result
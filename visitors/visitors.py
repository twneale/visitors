import types
import collections.abc

from visitors.base import Visitor


class TypeVisitor(Visitor):
    '''Visitor that dispatches based on instance type.

    class TypeVisitor(Visitor):

        dispatcher = TypenameDispatcher()

        def get_method(self, *args, **kwargs):
            return self.dispatcher.get_method(self, *args, **kwargs)

        You can either define get_method or gen_methods
    '''
    def get_nodekey(self, token, types=types, coll_abc=collections.abc):
        '''Given a particular token, check the visitor instance for methods
        mathing the computed methodnames (the function is a generator).
        '''
        for mro_type in type(token).__mro__:
            yield mro_type.__name__

        # Check for the collections.abc types.
        abc_types = (
            'Hashable',
            'Iterable',
            'Iterator',
            'Sized',
            'Container',
            'Callable',
            'Set',
            'MutableSet',
            'Mapping',
            'MutableMapping',
            'MappingView',
            'KeysView',
            'ItemsView',
            'ValuesView',
            'Sequence',
            'MutableSequence',
            'ByteString')
        for type_name in abc_types:
            type_ = getattr(coll_abc, type_name)
            if isinstance(token, type_):
                yield type_name

        # Check for the standard interpreter types in the types module.
        interp_types = (
            'BuiltinFunctionType',
            'BuiltinMethodType',
            'CodeType',
            'DynamicClassAttribute',
            'FrameType',
            'FunctionType',
            'GeneratorType',
            'GetSetDescriptorType',
            'LambdaType',
            'MappingProxyType',
            'MemberDescriptorType',
            'MethodType',
            'ModuleType',
            'SimpleNamespace',
            'TracebackType')
        for type_name in interp_types:
            type_ = getattr(types, type_name)
            if isinstance(token, type_):
                yield type_name


class StreamVisitor(TypeVisitor):

    def itervisit(self, iterable, gentype=types.GeneratorType):
        '''The main visit function. Visits the passed-in node and calls
        finalize.
        '''
        self.iterable = iter(iterable)
        for token in self.iterable:
            result = self.itervisit_node(token)
            if isinstance(result, gentype):
                for output in result:
                    yield output
            elif result is not None:
                yield result
        result = self.finalize()
        if result is self:
            return
        if isinstance(result, gentype):
            for output in result:
                yield output


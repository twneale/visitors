'''Tools for visiting html and xml etrees, and for converting tater graphs
 to and from etrees.
'''
import re
import functools

import lxml.etree as et
from lxml.html import HtmlComment

from treebie import Node
from visitors import Visitor


class XmlEtreeVisitor(Visitor):

    def get_children(self, el):
        return tuple(el)

    def get_nodekey(self, el):
        return el.tag


class LxmlHtmlVisitor(XmlEtreeVisitor):

    def visit_HtmlComment(self, node):
        '''Skip comments.
        '''
        raise self.Continue()

    def get_nodekey(self, el):
        key = el.tag
        if callable(key):
            return
        yield key


class _TaterXmlEtreeConverter(Visitor):

    def __init__(self):
        self.uuid_to_el = {}

    def get_nodekey(self, node):
        return node['tag']

    def finalize(self):
        return self.root

    def generic_visit(self, node):
        attrs = dict(node)
        tag = attrs.pop('tag')
        text = attrs.pop('text', None)
        tail = attrs.pop('tail', None)
        attrs = dict((k, str(v)) for k, v in attrs.items())
        parent = self.uuid_to_el.get(node.parent.uuid)
        if parent is None:
            this = et.Element(tag, **attrs)
            self.root = this
        else:
            this = et.SubElement(parent, tag, **attrs)
        this.text = text
        this.tail = tail
        self.uuid_to_el[node.uuid] = this


def to_etree(node):
    return _TaterXmlEtreeConverter().visit(node)


def from_etree(
    el, node=None, node_cls=None,
    tagsub=functools.partial(re.sub, r'\{.+?\}', ''),
    Node=Node):
    '''Convert the element tree to a tater tree.
    '''
    node_cls = node_cls or Node
    if node is None:
        node = node_cls()
    tag = tagsub(el.tag)
    attrib = dict((tagsub(k), v) for (k, v) in el.attrib.items())
    node.update(attrib, tag=tag)

    if el.text:
        node['text'] = el.text
    for child in el:
        child = from_etree(child, node_cls=node_cls)
        node.append(child)
    if el.tail:
        node['tail'] = el.tail
    return node


def from_html(
    el, node=None, node_cls=None,
    tagsub=functools.partial(re.sub, r'\{.+?\}', ''),
    Node=Node, HtmlComment=HtmlComment):
    '''Convert the element tree to a tater tree.
    '''
    node_cls = node_cls or Node
    node = node or node_cls()
    tag = tagsub(el.tag)
    attrib = dict((tagsub(k), v) for (k, v) in el.attrib.items())
    node.update(attrib, tag=tag)

    if el.text:
        node['text'] = el.text
    for child in el:
        if isinstance(child, HtmlComment):
            continue
        elif getattr(child, '__name__', None) == 'Comment':
            continue
        child = from_html(child, node_cls=node_cls)
        node.append(child)
    if el.tail:
        node['tail'] = el.tail
    return node



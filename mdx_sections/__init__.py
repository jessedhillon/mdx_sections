import re
import logging

from markdown.util import etree
from markdown import Extension
from markdown.treeprocessors import Treeprocessor
from markdown.blockprocessors import BlockProcessor

Logger = logging.getLogger('mdx_sections')

def makeExtension(config=None):
    return DocumentSectionExtension(config)

class DocumentSectionExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        self.config = {
            'section_cls': ['section', 'Default CSS class applied to sections'],
            'heading_cls': ['title', 'CSS class applied to transformed h{1-6} element']
        }
        self.section_processor = DocumentSectionProcessor(self.getConfig('section_cls'), self.getConfig('heading_cls'))
        self.heading_processor = HeadingProcessor(md.parser, self.getConfig('section_cls'))

        md.treeprocessors.add('document_section', self.section_processor, '_end')
        md.parser.blockprocessors.add('header_id', self.heading_processor, '_begin')

class HeadingProcessor(BlockProcessor):
    pattern = re.compile('^(?P<depth>#+)\s+{(?P<id>[,A-Za-z0-9_-]+)}\s+(?P<text>.*)')
    current_section = []

    def __init__(self, md, section_cls='section'):
        self.section_cls = section_cls
        BlockProcessor.__init__(self, md)

    def test(self, parent, block):
        if self.pattern.match(block):
            return True

    def run(self, parent, blocks):
        lines = blocks.pop(0).split('\n')

        heading = self.pattern.match(lines[0]).groupdict()
        depth = min(6, int(len(heading.get('depth'))))

        id = heading.get('id').split(',')
        if len(id) == 2:
            cls = id[1]
            id = id[0]
        else:
            id = id[0]
            cls = 'section'

        h = etree.SubElement(parent, 'h{depth}'.format(depth=depth))
        h.attrib['id'] = id
        h.attrib['class'] = cls
        h.text = heading.get('text')

        for i, line in enumerate(lines[1:]):
            blocks.insert(i, line)

class DocumentSectionProcessor(Treeprocessor):
    def __init__(self, section_cls='section', heading_cls='title'):
        self.section_cls = section_cls
        self.heading_cls = heading_cls
        Treeprocessor.__init__(self)

    def process_nodes(self, node):
        s = []
        pattern = re.compile('^h(\d)')

        for n in node.getchildren():
            match = pattern.match(n.tag.lower())

            if match:
                section = etree.SubElement(node, 'div')
                section.append(n)
                section.attrib['class'] = n.attrib.get('class', self.section_cls)

                node.remove(n)

                if 'id' in n.attrib:
                    section.attrib['id'] = n.attrib['id']
                    del n.attrib['id']

                n.attrib['class'] = self.heading_cls

                depth = int(match.group(1))
                Logger.debug('matched %s>%s#%s.%s', depth, n.tag, n.attrib.get('id'), n.attrib.get('class'))

                contained = False
                while s:
                    Logger.debug('searching for container')
                    container, container_depth = s[-1]
                    if depth <= container_depth:
                        s.pop()
                    else:
                        contained = True
                        break

                if contained:
                    Logger.debug('using container %s>%s#%s.%s', container_depth, container.tag, container.attrib.get('id'), container.attrib.get('class'))
                    container.append(section)
                    node.remove(section)

                else:
                    Logger.debug('no container found, appending to root')

                Logger.debug('current container %s>%s#%s.%s', depth, section.tag, section.attrib.get('id'), section.attrib.get('class'))
                s.append((section, depth))

            else:
                Logger.debug('non-heading element %s', n.tag)
                if s:
                    container, container_depth = s[-1]
                    container.append(n)
                    node.remove(n)
                    Logger.debug('appending to container %s>%s#%s.%s', container_depth, container.tag, container.attrib.get('id'), container.attrib.get('class'))

    def run(self, root):
        Logger.info('processing %s', root.tag)
        self.process_nodes(root)
        return root

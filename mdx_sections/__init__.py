"""
This module is an extension to Python-Markdown which provides the ability
to add a small amount of structure to your Markdown documents.

Entry point: mdx_sections
"""

import logging
import re
from xml.etree.ElementTree import SubElement

from markdown.blockprocessors import BlockProcessor
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor

Logger = logging.getLogger("mdx_sections")


def makeExtension(*args, **kwargs):  # pylint: disable=invalid-name; as specified
    """ Returns the extension instance. """
    return DocumentSectionExtension(**kwargs)


class DocumentSectionExtension(Extension):
    """ Block processor extension. """

    def __init__(self, **kwargs):
        """ Configure the extension. """
        self.config = {
            "section_cls": [
                kwargs.get("section_cls", "section"),
                "Default CSS class applied to sections",
            ],
            "heading_cls": [
                kwargs.get("heading_cls", "title"),
                "CSS class applied to transformed h{1-6} element",
            ],
        }
        super().__init__(**kwargs)
        self.setConfigs(kwargs)

    def extendMarkdown(self, md):
        """ Register processors. """
        md.treeprocessors.register(
            DocumentSectionProcessor(
                self.getConfig("section_cls"), self.getConfig("heading_cls")
            ),
            "document_section",
            45,
        )
        md.parser.blockprocessors.register(
            HeadingProcessor(md.parser, self.getConfig("section_cls")),
            "header_id",
            55,
        )


class HeadingProcessor(BlockProcessor):
    pattern = re.compile(r"^(?P<depth>#+)\s+{(?P<id>[,A-Za-z0-9_-]+)}\s+(?P<text>.*)")

    def __init__(self, md, section_cls="section"):
        self.section_cls = section_cls
        BlockProcessor.__init__(self, md)

    def test(self, parent, block):
        return bool(self.pattern.match(block))

    def run(self, parent, blocks):
        lines = blocks.pop(0).split("\n")

        heading = self.pattern.match(lines[0]).groupdict()
        depth = min(6, int(len(heading.get("depth"))))

        heading_id = heading.get("id").split(",")
        if len(heading_id) == 2:
            cls = heading_id[1]
            heading_id = heading_id[0]
        else:
            heading_id = heading_id[0]
            cls = "section"

        h_tag = SubElement(parent, "h{depth}".format(depth=depth))
        h_tag.attrib["id"] = heading_id
        h_tag.attrib["class"] = cls
        h_tag.text = heading.get("text")

        for i, line in enumerate(lines[1:]):
            blocks.insert(i, line)


class DocumentSectionProcessor(Treeprocessor):
    def __init__(self, section_cls="section", heading_cls="title"):
        self.section_cls = section_cls
        self.heading_cls = heading_cls
        Treeprocessor.__init__(self)

    def process_nodes(self, node):
        sections = []
        pattern = re.compile(r"^h(\d)")

        for child in node.getchildren():
            match = pattern.match(child.tag.lower())

            if match:
                section = SubElement(node, "div")
                section.append(child)
                section.attrib["class"] = child.attrib.get("class", self.section_cls)

                node.remove(child)

                if "id" in child.attrib:
                    section.attrib["id"] = child.attrib["id"]
                    del child.attrib["id"]

                child.attrib["class"] = self.heading_cls

                depth = int(match.group(1))
                Logger.debug(
                    "matched %s>%s#%s.%s",
                    depth,
                    child.tag,
                    child.attrib.get("id"),
                    child.attrib.get("class"),
                )

                contained = False
                while sections:
                    Logger.debug("searching for container")
                    container, container_depth = sections[-1]
                    if depth <= container_depth:
                        sections.pop()
                    else:
                        contained = True
                        break

                if contained:
                    Logger.debug(
                        "using container %s>%s#%s.%s",
                        container_depth,
                        container.tag,
                        container.attrib.get("id"),
                        container.attrib.get("class"),
                    )
                    container.append(section)
                    node.remove(section)

                else:
                    Logger.debug("no container found, appending to root")

                Logger.debug(
                    "current container %s>%s#%s.%s",
                    depth,
                    section.tag,
                    section.attrib.get("id"),
                    section.attrib.get("class"),
                )
                sections.append((section, depth))

            else:
                Logger.debug("non-heading element %s", child.tag)
                if sections:
                    container, container_depth = sections[-1]
                    container.append(child)
                    node.remove(child)
                    Logger.debug(
                        "appending to container %s>%s#%s.%s",
                        container_depth,
                        container.tag,
                        container.attrib.get("id"),
                        container.attrib.get("class"),
                    )

    def run(self, root):
        Logger.info("processing %s", root.tag)
        self.process_nodes(root)
        return root

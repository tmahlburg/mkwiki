#! /usr/bin/env python3

import os

# This needs to be installed on the host system (python3-commonmark)
import commonmark


# path to commonmark source files
wiki_src = ''
# path to the generated html wiki
wiki_trg = ''
# this should be empty for deployment and 'wiki_trg' for development
base_url = ''
# base URL of the page, where one can edit the article
edit_base_url = ''

header = """
<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <title>Wiki</title>
        <style>
            body {
              max-width: 80ch;
              padding: 2ch;
              margin: auto;
              font-family: "Noto Serif", Serif;
              font-size: 18px;
            }
            p {
              text-align: justify;
            }
            h1 {
              font-size: 40px;
            }
            h2 {
              font-size: 30px;
            }
            h3 {
              font-size: 25px;
            }
            h4 {
              font-size: 20px;
            }
            img {
              max-width: 100%;
              height: auto;
            }
            hr {
              border: none;
              height: 0.3rem;
            }
        </style>
    </head>
    <body>
"""

footer = """
    </body>
</html>
"""

index_header = """
<h1>Wiki</h1>
<h2>Index</h2>
"""


readme = ''


def links(rel_path: str) -> str:
    index = os.path.join(base_url, 'index.html')
    edit = os.path.join(edit_base_url, rel_path)
    return ('<p><a href="' + index + '">Zurück zur Übersicht</a> | '
            + '<a href="' + edit + '">Artikel bearbeiten</a></p>')


def build_page(md_content: str, rel_path: str) -> str:
    content = commonmark.commonmark(md_content)
    if rel_path.lower() == 'readme.md':
        global readme
        readme = content
    return (header + links(rel_path) + content + footer)


def build_tree(index_list: list[list[str]]):
    root_node = Node(name='root', link=None)
    tree = Tree(root_node)
    for entry in index_list:
        for i in range(len(entry)):
            # build new node
            if (i == len(entry) - 1):
                node = Node(name=entry[i],
                            link=os.path.join(base_url, *entry))
            else:
                node = Node(name=entry[i],
                            link=None)
            # insert into tree
            if (i == 0):
                tree.insert('root', node)
            else:
                tree.insert(entry[i-1], node)
    return(tree)


def build_index_content(node, indent=0) -> str:
    if len(node.children) == 0:
        result = '<a href="' + node.link + \
            '" style="margin-left:' + str(indent) + 'px">'
        result += node.name.removesuffix(".html") + '</a><br>\n'
        return result
    else:
        result = ''
        if (node.name != 'root'):
            result += '<details style="margin-left:' + str(indent) + 'px">\n'
            result += '<summary>' + node.name + '</summary>\n'
        for child in node.children:
            result += build_index_content(child, indent + 10)
        if (node.name != 'root'):
            result += '</details>\n'
    return result


def build_index(index_list: list[str]) -> str:
    list_copy = []
    for entry in index_list:
        list_copy.append(entry.split('/'))
    tree = build_tree(list_copy)

    content = build_index_content(tree.root)

    return (header + index_header + content + readme + footer)


def build_wiki():
    index_list = []
    for root, dirs, files in os.walk(wiki_src):
        for name in files:
            src_path = os.path.join(root, name)
            rel_path = os.path.relpath(src_path, wiki_src)
            # only process files with 'md' extension in non hidden dirs
            if (rel_path[0] != '.'
                    and os.path.splitext(rel_path)[1] == '.md'):
                with open(src_path, 'r') as f:
                    content = f.read()
                page = build_page(content, rel_path)
                # change extension to html
                rel_path = os.path.splitext(rel_path)[0] + '.html'
                trg_path = os.path.join(wiki_trg, rel_path)
                os.makedirs(os.path.dirname(trg_path), exist_ok=True)
                with open(trg_path, 'w') as f:
                    f.write(page)
                index_list.append(rel_path)
    index_list.sort(key=str.lower)
    index_page = build_index(index_list)
    with open(os.path.join(wiki_trg, 'index.html'), 'w') as f:
        f.write(index_page)


class Node:
    def __init__(self, name: str, link: str):
        self.name = name
        self.link = link
        self.children = []

    def add_child(self, child):
        for entry in self.children:
            if entry.name == child.name:
                # already in tree
                return False
        self.children.append(child)
        return True

    def __str__(self):
        return self.name


class Tree:
    def __init__(self, root):
        self.root = root
        self.node_list = [self.root]

    def insert(self, parent_name: str, node):
        parent = self.find(parent_name, self.root)
        if (parent is not None):
            if parent.add_child(node):
                self.node_list.append(node)
                return True
        return False

    def find(self, name: str, current):
        if (current.name == name):
            return current
        result = None
        for child in current.children:
            if result is None:
                result = self.find(name, child)
            else:
                break
        return result

    def __str__(self):
        result = ''
        for node in self.node_list:
            result += ' ' + str(node)
        return result


build_wiki()

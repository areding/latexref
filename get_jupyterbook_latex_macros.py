# -*- coding: utf-8 -*-
"""
Get all Latex macros used in a Jupyter Book with .md and .ipynb files and store them.

Output: macros_used.txt

Attributes:
    LatexNodeType: pylatexenc.latexwalker node types
"""
# @Author: Aaron Reding
# @Date:   2023-07-15 00:27:05
# @Last Modified by:   areding
# @Last Modified time: 2023-07-15 23:13:51
import jupytext
from pylatexenc.latexwalker import LatexWalker
from pylatexenc.latexwalker import (
    LatexMathNode,
    LatexMacroNode,
    LatexGroupNode,
    LatexSpecialsNode,
    LatexCharsNode,
    LatexEnvironmentNode,
)
from pathlib import Path
import warnings
from typing import Union
from tqdm import tqdm

LatexNodeType = Union[
    LatexMathNode,
    LatexMacroNode,
    LatexGroupNode,
    LatexSpecialsNode,
    LatexCharsNode,
    LatexEnvironmentNode,
]


def get_content_filepaths(book_dir: Path, unit_list: list[str]) -> tuple:
    """Get Pathlib Paths for all content files, separated into md and ipynb.

    Limitations:
        - Currently only searches in folders, won't return paths in book_dir.
        - Only returns markdown or ipynb files, warns about other file types.

    Args:
        book_dir (Path): The base directory of the Jupyter Book.
        unit_list (list[str]): Folder list for chapters.

    Returns:
        tuple: markdown filepaths, ipynb filepaths
    """
    all_md_filepaths = []
    all_ipynb_filepaths = []

    for unit in unit_list:
        current_path = book_dir / unit
        assert current_path.exists(), f"Path {current_path} doesn't exist!"

        for file in current_path.iterdir():
            if file.suffix == ".md":
                all_md_filepaths.append(file)

            elif file.suffix == ".ipynb":
                all_ipynb_filepaths.append(file)

            elif not file.suffix:
                print(f"Ignoring hidden file {file}")

            else:
                warnings.warn(
                    f"Non-hidden file type ignored: {file} is not .md or .ipynb."
                )

    return all_md_filepaths, all_ipynb_filepaths


def get_nodelist(text: str) -> list[LatexNodeType]:
    """Use pylatexenc.latexwalker to get latex nodes from text.

    Args:
        text (str)

    Returns:
        list[LatexNodeType]: list of identified nodes
    """
    w = LatexWalker(text)
    (node_list, pos_, len_) = w.get_latex_nodes(pos=0)
    return node_list


def is_macro(node: LatexNodeType) -> bool:
    """Check if LatexMacroNode which contains the name of the macro.

    Args:
        node (LatexNodeType)

    Returns:
        bool: True if MacroNode
    """
    return node.isNodeType(LatexMacroNode)


def has_nodelist(node: LatexNodeType) -> bool:
    """Check if MathNode or EnvironmentNode, both have nodelists

    Args:
        node (LatexNodeType)

    Returns:
        bool: True if is a type that has nodelist attribute
    """
    return node.isNodeType(LatexMathNode) or node.isNodeType(LatexEnvironmentNode)


def get_macros(node_list: list[LatexNodeType]) -> set:
    """Recursive function to get all macros in list of nodes

    Args:
        node_list (list[LatexNodeType]): list of nodes from get_nodelist

    Returns:
        set: unique nodes in this list
    """
    macros = set()
    if not node_list:
        return macros

    for node in node_list:
        if is_macro(node):
            macros.add(node.macroname)
        elif has_nodelist(node):
            macros.update(get_macros(node.nodelist))
        else:
            continue

    return macros


def process_md_files(md_filelist: list[Path]) -> set:
    """Get all macros used in given filelist. For md files only!

    Args:
        md_filelist (list[Path]): all md filepaths from get_content_filepaths

    Returns:
        set: All macros used in all md files in the book
    """
    all_md_macros = set()

    print("Processing .md files...")
    for file in tqdm(md_filelist):
        assert file.suffix == ".md", f"File {file} is not a markdown file!"
        with open(file, "r") as file:
            file_text = file.read()

        nodelist = get_nodelist(file_text)
        nb_macros = get_macros(nodelist)

        all_md_macros.update(nb_macros)

    return all_md_macros


def process_ipynb_files(ipynb_filelist: list[Path]) -> set:
    """Get all macros used in given filelist. For ipynb files only!

    Args:
        ipynb_filelist (list[Path]): all ipynb filepaths from get_content_filepaths

    Returns:
        set: All macros used in all ipynb files in the book
    """
    all_nb_macros = set()

    print("Processing .ipynb files...")
    for file in tqdm(ipynb_filelist):
        nb_text = ""
        nb = jupytext.read(file)

        for cell in nb["cells"]:
            nb_text += cell["source"]

        base_nodelist = get_nodelist(nb_text)
        nb_macros = get_macros(base_nodelist)

        all_nb_macros.update(nb_macros)

    return all_nb_macros


def final_clean(macros: set) -> set:
    """Cleans some issues I noticed in the final list including blank lines.

    Should probably update the logic so they don't show in the first place.

    Args:
        macros (set)

    Returns:
        set: Returns a cleaned version of the set
    """
    problem_list = ["{", "}", "t", "n", "&", "\\"]

    return {item for item in macros if item.strip() and item not in problem_list}


def write_file(macros: set):
    """Save the macros found in the Jupyter Book to a txt file.

    Args:
        macros (set)
    """
    with open("macros_used.txt", "w") as f:
        f.write("\n".join(macros))


def main():
    # Jupyter Book directory
    book_dir = Path.home() / "bayes/6420-redo"
    assert book_dir.exists(), f"Book directory {book_dir} not found!"

    # Jupyter Book content folders
    unit_list = [f"unit{x}" for x in range(1, 11)]
    unit_list.append("backmatter")

    # .md and .ipynb content lists
    md_files, ipynb_files = get_content_filepaths(book_dir, unit_list)

    # get all macros used in the Jupyter Book
    all_macros_used = set()
    all_macros_used.update(process_md_files(md_files))
    all_macros_used.update(process_ipynb_files(ipynb_files))

    clean_macros = final_clean(all_macros_used)
    write_file(clean_macros)


if __name__ == "__main__":
    main()

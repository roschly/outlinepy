from typing import List, Tuple
from pathlib import Path
from argparse import ArgumentParser, Namespace
import logging
import sys

import astroid
from xml.etree import ElementTree as ET

from .data_types import ModuleData
from .text_layouts import ModuleLayout as ModuleLayoutText
from .html_layouts import ModuleLayout as ModuleLayoutHtml
from .default_styling import get_default_styling


def parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("dir", type=str, help="root directory path of project.")
    parser.add_argument(
        "--include-test",
        action="store_true",
        help="include '**/test_*.py' files in outline.",
    )
    parser.add_argument(
        "--xincl",
        type=str,
        help="""Exclusively include filepaths that match XINCL glob pattern. 
        E.g. '**/dirA/*.py' only include .py files in any directory called 'dirA'.""",
    )
    parser.add_argument(
        "--absolute-path",
        action="store_true",
        help="use absolute (instead of relative) path of each .py file.",
    )
    parser.add_argument(
        "--get-default-styling",
        action="store_true",
        help="Outputs the CSS default styling used for html output.",
    )
    parser.add_argument(
        "--styling-css",
        type=str,
        help="Supply a CSS file that will be used to style the html output instead of the default styling.",
    )
    return parser.parse_args()


def build_output_string(path_and_modules: List, absolute_path: bool, root: Path) -> str:
    s = ""
    for path, module in path_and_modules:
        # TODO: let ModuleLayout handle path string as well
        s += str(path) if absolute_path else str(path.relative_to(root))
        s += "\n" + str(ModuleLayoutText(ModuleData(module), n_indent=0))
    return s


def build_html_tree(
    path_and_modules: List[Tuple[Path, astroid.Module]],
    absolute_path: bool,
    root: Path,
    styling: str,
) -> ET.Element:
    html = ET.Element("html")
    head = ET.Element("head")
    html.append(head)

    # load default css styling as internal css (to avoid dependence on external css file).
    # TODO: allow override with user specified configs
    style = ET.Element("style")
    style.text = styling

    head.append(style)

    body = ET.Element("body")
    html.append(body)

    for path, module in path_and_modules:
        mod = ModuleLayoutHtml(
            filepath=path if absolute_path else path.relative_to(root),
            module=ModuleData(module),
        )
        body.append(mod)

    return html


def main():
    """ """

    css_styling = get_default_styling()

    args: Namespace = parse_args()

    # output default css styling
    if args.get_default_styling:
        print(css_styling)
        return

    if args.styling_css:
        css_path = Path(args.styling_css)
        if not css_path.exists() or css_path.suffix != ".css":
            raise ValueError("CSS file must exist and have .css as extension.")
        with open(css_path) as fh:
            css_styling = fh.read()

    root = Path.cwd() / Path(args.dir)
    if not root.is_dir():
        raise Exception("'dir' must be an existing directory.")

    # find all .py filepaths in root
    filepaths: List[Path] = list(root.rglob("*.py"))

    # TODO: don't traverse directory more than once?
    # filepaths to ignore
    paths_to_ignore = []
    if not args.include_test:
        paths_to_ignore += list(root.rglob("**/test_*.py"))
    if args.xincl:
        # ignore all other filepaths than those found via xincl glob pattern.
        paths_to_ignore += [
            f for f in filepaths if f not in list(root.rglob(args.xincl))
        ]
        if len(paths_to_ignore) == len(filepaths):
            logging.warning(
                f"All filepaths are being ignored with the current XINCL glob pattern: {args.xincl}"
            )

    # combine each python file with its module Abstract Syntax Tree
    path_and_modules: List[Tuple[Path, astroid.Module]] = []
    for filepath in [f for f in filepaths if f not in paths_to_ignore]:
        try:
            with open(filepath) as fh:
                module = astroid.parse(fh.read())
            path_and_modules.append((filepath, module))
        except Exception as e:
            logging.warning(
                f"Ignoring file '{filepath}' because of the following error:"
            )
            logging.warning(e)

    # build html tree
    html: ET.Element = build_html_tree(
        path_and_modules=path_and_modules,
        absolute_path=args.absolute_path,
        root=root,
        styling=css_styling,
    )

    # write HTML to stdout
    ET.ElementTree(html).write(sys.stdout, encoding="unicode", method="html")


if __name__ == "__main__":
    main()

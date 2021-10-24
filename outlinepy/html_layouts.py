from typing import Dict, List, Tuple
from xml.etree import ElementTree as ET
from pathlib import Path

from .data_types import ClassData, FunctionData, ModuleData, ArgumentData


class Element(ET.Element):
    """Override ET.Element in order to pass text via a function."""

    def __init__(self, *args, text: str = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.text = text


class TextElement(ET.Element):
    """Shortcut to creating a span element with text.
    Text is the first positional argument,
    instead of an attribute that has to be defined via assignment.
    """

    def __init__(self, text: str, attrib={}) -> None:
        super().__init__("span", attrib=attrib)
        self.text = text


class ArgumentsInlineLayout(ET.Element):
    """ """

    def __init__(self, arguments: List[ArgumentData]):
        super().__init__("span", attrib={"class": "arguments"})
        self.arguments = arguments

        elems = self._inline_args()

        for elem in elems:
            self.append(elem)

    def _inline_args(self) -> List[ET.Element]:
        elems = []
        for i, arg in enumerate(self.arguments):
            elems += [TextElement(arg.name, attrib={"class": "argument_name"})]
            if arg.type:
                elems += [
                    TextElement(": "),
                    TextElement(arg.type, attrib={"class": "argument_type"}),
                ]
            if i < len(self.arguments) - 1:  # skip comma after last arg
                elems += [TextElement(", ")]
        return elems


class ArgumentsMultilineLayout(ET.Element):
    """ """

    def __init__(self, arguments: List[ArgumentData]):
        super().__init__("ul", attrib={"class": "arguments"})
        self.arguments = arguments

        elems = self._multi_line_args()

        for elem in elems:
            self.append(elem)

    def _multi_line_args(self) -> List[ET.Element]:
        elems = []
        for arg in self.arguments:
            li = ET.Element("li")
            li.append(TextElement(arg.name, attrib={"class": "argument_name"}))
            if arg.type:
                li.append(TextElement(": "))
                li.append(TextElement(arg.type, attrib={"class": "argument_type"}))
            elems.append(li)

        return elems


class DecoratorLayout(ET.Element):
    def __init__(self, decorators: List[str]) -> None:
        super().__init__("div", attrib={"class": "decorators"})

        for deco in decorators:
            self.append(TextElement(f"@{deco}", attrib={"class": "decorator"}))
            self.append(ET.Element("br"))


class ClassVariableLayout(ET.Element):
    def __init__(self, class_var: Tuple[str, str]) -> None:
        super().__init__("div", attrib={"class": "class_variable"})

        self.append(
            TextElement(f"{class_var[0]}", attrib={"class": "class_variable_name"})
        )
        if class_var[1]:
            self.append(TextElement(": "))
            self.append(
                TextElement(f"{class_var[1]}", attrib={"class": "class_variable_type"})
            )


class BasenamesLayout(ET.Element):
    """ """

    def __init__(self, basenames: List[str]) -> None:
        super().__init__("span", attrib={"class": "class_basenames"})
        # TODO: handle multiline basenames, similar to arguments layout
        for i, basename in enumerate(basenames):
            self.append(TextElement(basename, attrib={"class": "class_basename"}))
            if i < len(basenames) - 1:
                self.append(TextElement(", "))


class FunctionLayout(ET.Element):
    def __init__(self, func_data: FunctionData) -> None:
        super().__init__("div", attrib={"class": "function"})

        elems = [
            DecoratorLayout(func_data.decorators),
            TextElement("def", attrib={"class": "function_def"}),
            TextElement(" "),
            TextElement(func_data.name, attrib={"class": "function_name"}),
            TextElement("("),
        ]
        elems += self._arguments_layout(func_data)

        # linebreak after function
        # NOTE: this only works for multiline arguments atm
        # which might be desirable.
        elems += [ET.Element("br")]
        for elem in elems:
            self.append(elem)

    def _arguments_layout(self, func_data: FunctionData) -> List[ET.Element]:
        elems = []
        if len(func_data.arguments) <= 3:
            elems += [ArgumentsInlineLayout(func_data.arguments), TextElement(")")]
            if func_data.return_type:
                elems += [
                    TextElement(" -> "),
                    TextElement(
                        func_data.return_type, attrib={"class": "function_return_type"}
                    ),
                ]
        else:
            multiline_args = ArgumentsMultilineLayout(func_data.arguments)
            li = ET.Element("li")
            li.append(TextElement(")"))
            if func_data.return_type:
                li.append(TextElement(" -> "))
                li.append(
                    TextElement(
                        func_data.return_type, attrib={"class": "function_return_type"}
                    )
                )
            multiline_args.append(li)
            elems += [multiline_args]
        return elems


class ClassLayout(ET.Element):
    """ """

    def __init__(self, class_data: ClassData) -> None:
        super().__init__("div", attrib={"class": "class"})

        # decorators
        elems = [
            DecoratorLayout(class_data.decorators),
            TextElement("class", attrib={"class": "class_def"}),
            TextElement(" "),
            TextElement(class_data.name, attrib={"class": "class_name"}),
            TextElement("("),
            BasenamesLayout(class_data.basenames),
            TextElement(")"),
        ]

        ul = ET.Element("ul")

        # class variables
        for cls_var in class_data.cls_vars:
            li = ET.Element("li")
            ul.append(li)
            li.append(ClassVariableLayout(cls_var))

        # methods
        for method in class_data.methods:
            li = ET.Element("li")
            ul.append(li)
            li.append(FunctionLayout(method))

        for elem in elems:
            self.append(elem)
        self.append(ul)
        # line break after class
        self.append(ET.Element("br"))


class ModuleLayout(ET.Element):
    """ """

    def __init__(self, filepath: Path, module: ModuleData) -> None:
        super().__init__("div", attrib={"class": "module"})

        self.append(TextElement(str(filepath), attrib={"class": "module_path"}))

        ul = ET.Element("ul")

        # TODO: add global module variables

        # functions
        for func in module.functions:
            li = ET.Element("li")
            ul.append(li)
            li.append(FunctionLayout(func))
            li.append(ET.Element("br"))

        # classes
        for cls in module.classes:
            li = ET.Element("li")
            ul.append(li)
            li.append(ClassLayout(cls))
        self.append(ul)

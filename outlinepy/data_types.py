from pathlib import Path
from typing import List, Tuple

import astroid


class ArgumentData:
    def __init__(self, arg_name: str, arg_type: str = None) -> None:
        self.name: str = arg_name
        self.type: str = arg_type if arg_type else ""

    def __repr__(self) -> str:
        return self.name if not self.type else f"{self.name}: {self.type}"


class DecoratorsData:
    def __init__(self, decorators: astroid.Decorators) -> None:
        # TODO: handle decorators better than just as_string()
        # e.g. for an astroid.Callable like @deco_1(param="a")
        self.decorators: List[str] = (
            [] if decorators is None else [dec.as_string() for dec in decorators.nodes]
        )


class FunctionData:
    def __init__(self, func_def: astroid.FunctionDef) -> None:
        self.name: str = func_def.name
        self.return_type: str = (
            "" if not func_def.returns else func_def.returns.as_string()
        )

        # TODO: AnnAssign vs Assign, first is Annotated Assign
        # so we know when there is type annotation available
        self.arguments: List[ArgumentData] = []
        arg: astroid.AssignName
        # arg_type: something-with-a as_string() method
        for arg, arg_type in zip(func_def.args.args, func_def.args.annotations):
            type_name = None if arg_type is None else arg_type.as_string()
            self.arguments.append(ArgumentData(arg_name=arg.name, arg_type=type_name))

        self.decorators: List[str] = DecoratorsData(func_def.decorators).decorators

    def __str__(self) -> str:
        return ""


class ClassData:
    def __init__(self, class_def: astroid.ClassDef) -> None:
        self.name: str = class_def.name
        self.basenames: List[str] = class_def.basenames
        self.methods: List[FunctionData] = [
            FunctionData(f) for f in class_def.mymethods()
        ]
        self.decorators: List[str] = DecoratorsData(class_def.decorators).decorators

        cls_vars = [e for e in class_def.body if isinstance(e, astroid.AnnAssign)]

        # TODO: make cls_var its own type?
        self.cls_vars: List[Tuple[str, str]] = []
        for cls_var in cls_vars:
            target_name = cls_var.target.name
            annotation = cls_var.annotation.as_string() if cls_var.annotation else None
            self.cls_vars.append((target_name, annotation))

    def __str__(self) -> str:
        return f"{self.name}"


class ModuleData:
    def __init__(self, module: astroid.Module) -> None:
        class_defs = [e for e in module.body if isinstance(e, astroid.ClassDef)]
        func_defs = [e for e in module.body if isinstance(e, astroid.FunctionDef)]
        self.classes: List[ClassData] = [ClassData(c) for c in class_defs]
        self.functions: List[FunctionData] = [FunctionData(f) for f in func_defs]

        # TODO: add global variables

    def __str__(self) -> str:
        return ""

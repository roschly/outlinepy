# %%

import astroid


# %%

code = """

some_func: int = 13
bla: str = "bla"
blu = True

@dataclass
class Bla:
    name: str
    num: int

    def post_init(self):
        self.name = "bla"

"""

m = astroid.parse(code)

# %%
cs = [e for e in m.body if isinstance(e, astroid.ClassDef)]
# %%

cls_vars = [e for e in cs[0].body if isinstance(e, astroid.AnnAssign)]

# %%

cls_vars[0].target.name
cls_vars[0].annotation.name
# %%

assigns = [e for e in m.body if isinstance(e, astroid.AnnAssign)]


# %%
assigns[0].target.name
# %%

f = [f for f in cs[0].body if isinstance(f, astroid.FunctionDef)][0]

# %%
# find self attribute
list(f.body[0].get_children())[0].expr.name
# %%

m.body

# %%

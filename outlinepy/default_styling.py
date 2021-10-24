# internal default css styling for html output
css_styling = """
body {
    background-color: #1e1e1e;
    color: white;
    font-family:
    monospace, monaco;
}
ul   {list-style-type: none;}

/* Abstract Syntax Tree related styling. */

/* Module */
.module_path {color: lightgreen;}

/* Function */
.function_def {color: #03a1fc;}
.function_return_type {color: #32cfc9; font-style: italic;}

/* Class */
.class_def {color: #03a1fc;}
.class_variable_type {color: #32cfc9; font-style: italic;}
.class_basename {color: #32cfc9;}

/* Misc */
.decorator {color: yellow;}
.argument_type {color: #32cfc9; font-style: italic;}

"""


def get_default_styling():
    return css_styling

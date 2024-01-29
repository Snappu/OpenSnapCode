import ctypes
import yaml
import re
import os
from tkinter import filedialog
from tkinter import *

with open('settings.yaml', 'r', encoding='utf-8') as read_file:
    contents = yaml.safe_load(read_file)
    font_style = contents['font_style']

filename = ''  # Define filename as a global variable


def open_file(event=None):
    """Функция для открытия файла"""
    global filename  # Declare filename as global
    file_path = filedialog.askopenfilename(filetypes=[("All Files", "*.*"), ("Python Files", "*.py")])
    if file_path:
        with open(file_path, 'r', encoding='utf-8') as file:
            editArea.delete('1.0', END)
            editArea.insert('1.0', file.read())
            filename = os.path.basename(file_path)
            root.title(f"Open Snap Code - {file_path}")
        changes()  # Call the changes() function to update the REPL


def save_file(event=None):
    """Функция для сохранения файла"""
    global filename  # Declare filename as global
    if filename:
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(editArea.get('1.0', END))
    else:
        save_file_as()


def save_file_as(event=None):
    """Функция для сохранения файла как"""
    global filename  # Declare filename as global
    file_path = filedialog.asksaveasfilename(filetypes=[("All Files", "*.*"), ("Python Files", "*.py")])
    if file_path:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(editArea.get('1.0', END))
        filename = os.path.basename(file_path)


def changes(event=None):
    """Функция для обработки подсветки синтаксиса"""
    global previousText
    if editArea.get('1.0', END) == previousText:
        return
    for tag in editArea.tag_names():
        editArea.tag_remove(tag, "1.0", "end")
    i = 0
    for pattern, color in repl:
        for start, end in search_re(pattern, editArea.get('1.0', END)):
            editArea.tag_add(f'{i}', start, end)
            editArea.tag_config(f'{i}', foreground=color)
            i += 1
    previousText = editArea.get('1.0', END)


def search_re(pattern, text):
    matches = []
    text = text.splitlines()
    for i, line in enumerate(text):
        for match in re.finditer(pattern, line):
            matches.append((f"{i + 1}.{match.start()}", f"{i + 1}.{match.end()}"))
    return matches


def rgb(rgb_colors):
    """Функция для определения цветов RGB"""
    return "#%02x%02x%02x" % rgb_colors


ctypes.windll.shcore.SetProcessDpiAwareness(True)

root = Tk()
root.geometry('700x500')
root.title("Open Snap Code")
previousText = ''

normal = rgb((234, 234, 234))
keywords = rgb((234, 95, 95))
comments = rgb((95, 234, 165))
string = rgb((234, 162, 95))
function = rgb((95, 211, 234))
background = rgb((42, 42, 42))
toolbar_background = rgb((30, 30, 30))
red = rgb((234, 95, 95))

menubar = Menu(root)

file_menu = Menu(menubar, tearoff=0)
file_menu.add_command(label="Open", command=open_file)
file_menu.add_command(label="Save", command=save_file)
file_menu.add_command(label="Save As", command=save_file_as)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)
menubar.add_cascade(label="File", menu=file_menu)

toolbar = Frame(root, bd=1, relief=RAISED, bg=toolbar_background)
toolbar.pack(side=TOP, fill=X)

repl = [
    # Keywords
    ['(^| )(False|None|True|and|as|assert|async|await|break|class|continue|def|del|elif|else|except|finally|for|from'
     '|global|if|import|in|is|lambda|nonlocal|not|or|pass|raise|return|try|while|with|yield)($| )', keywords],

    # Comments
    ['#.*?$', comments],  # Fixed missing closing quotes

    # Strings
    ['".*?"', string],
    ['\".*?\"', string],

    # Functions
    ['def [a-zA-Z_][a-zA-Z0-9_]* *\(', function],

    # Classes
    ['class [a-zA-Z_][a-zA-Z0-9_]*:', function],

    # Numbers
    ['\d+\.?\d*', rgb((234, 162, 95))],

    # Operators
    ['[+\-*/%=]', rgb((234, 234, 234))],

    # Punctuation
    ['[\[\]{}(),;:]', rgb((234, 234, 234))],

    # Built-in functions
    ['(print|input)\(.*?\)', red],

    # Strings inside parentheses
    ['\((.*?)\)', string],

    # Comment until end of line
    ['#.*', comments],
]

editArea = Text(
    root, background=background, foreground=normal, insertbackground=normal, relief=FLAT, borderwidth=30,
    font=font_style
)

editArea.pack(fill=BOTH, expand=1)

editArea.insert('1.0', """
print("Hello World")
""")

editArea.bind('<KeyRelease>', changes)

root.bind('<Control-s>', save_file)

changes()

root.config(menu=menubar)
root.mainloop()

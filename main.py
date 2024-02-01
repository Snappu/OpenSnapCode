# libraries imports
import ctypes
import yaml
import re
import os
import keyboard
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk, messagebox

# root configure
root = tk.Tk()
root.geometry('700x500')
root.minsize(400, 200)
root.title("Open Snap Code")
root.iconbitmap('images/icon.ico')
previousText = ''

# import settings from settings.yaml
with open('settings.yaml', 'r', encoding='utf-8') as read_file:
    contents = yaml.safe_load(read_file)
    font_style = contents['font_style']

filename = ''  # Define filename as a global variable
undo_stack = []  # Stack to store previous states of the text


def open_file(event=None):
    """Function for opening a file"""
    global filename  # Declare filename as global
    file_path = filedialog.askopenfilename(
        filetypes=[("All Files", "*.*"), ("Python Files", "*.py")])
    if file_path:
        with open(file_path, 'r', encoding='utf-8') as file:
            text.delete('1.0', tk.END)
            text.insert('1.0', file.read())
            filename = os.path.basename(file_path)
            root.title(f"Open Snap Code - {file_path}")
        changes()  # Call the changes() function to update the REPL


def save_file(event=None):
    """Function for saving a file"""
    global filename  # Declare filename as global
    if filename:
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(text.get('1.0', tk.END))
    else:
        save_file_as()


def save_file_as(event=None):
    """A function to save a file as"""
    global filename  # Declare filename as global
    file_path = filedialog.asksaveasfilename(
        filetypes=[("All Files", "*.*"), ("Python Files", "*.py")])
    if file_path:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(text.get('1.0', tk.END))
        filename = os.path.basename(file_path)


def changes(event=None):
    """A function for processing syntax highlighting"""
    global previousText
    if text.get('1.0', tk.END) == previousText:
        return
    # Save the current state of the text to the undo stack
    undo_stack.append(text.get('1.0', tk.END))
    for tag in text.tag_names():
        text.tag_remove(tag, "1.0", "end")
    i = 0
    for pattern, color in repl:
        for start, end in search_re(pattern, text.get('1.0', tk.END)):
            text.tag_add(f'{i}', start, end)
            text.tag_config(f'{i}', foreground=color)
            i += 1
    previousText = text.get('1.0', tk.END)


def search_re(pattern, text):
    matches = []
    text = text.splitlines()
    for i, line in enumerate(text):
        for match in re.finditer(pattern, line):
            matches.append((f"{i + 1}.{match.start()}",
                           f"{i + 1}.{match.end()}"))
    return matches


def rgb(rgb_colors):
    """Function for detecting RGB colors"""
    return "#%02x%02x%02x" % rgb_colors


ctypes.windll.shcore.SetProcessDpiAwareness(True)

normal = rgb((234, 234, 234))
keywords = rgb((234, 95, 95))
comments = rgb((95, 234, 165))
string = rgb((234, 162, 95))
function = rgb((95, 211, 234))
background = rgb((42, 42, 42))
toolbar_background = rgb((30, 30, 30))
num_color = rgb((100, 100, 100))
red = rgb((234, 95, 95))

repl = [
    # Keywords
    [r'(^| )\b(False|None|True|and|as|assert|async|await|break|class|continue|def|del|elif|else|except|finally|for|from'
     r'|global|if|import|in|is|lambda|nonlocal|not|or|pass|raise|return|try|while|with|yield)\b($| )', '#8be9fd'],

    # Comments
    [r'#.*', '#6272a4'],
    [r'""".*?"""', '#6272a4'],  # Add triple-quoted strings as comments

    # Strings
    [r'".*?"', '#f1fa8c'],
    [r'\'.*?\'', '#f1fa8c'],

    # Functions
    [r'def [a-zA-Z_][a-zA-Z0-9_]* *\(', '#50fa7b'],

    # Classes
    [r'class [a-zA-Z_][a-zA-Z0-9_]*:', '#50fa7b'],

    # Numbers
    [r'\b\d+\.?\d*\b', '#bd93f9'],

    # Operators
    [r'[+\-*/%=]', '#ff79c6'],

    # Punctuation
    [r'[\[\]{}(),;:]', '#ff79c6'],

    # Built-in functions
    [r'\b(print|input)\(.*?\)', '#ffb86c'],

    # Strings inside parentheses
    [r'\((.*?)\)', '#f1fa8c']
]
# Line wrapping is disabled, otherwise the numbering will not work correctly
numbers = tk.Text(root, width=4, bg='lightgray', state=tk.DISABLED,
                  relief=tk.FLAT, fg=num_color, font=font_style, background=background)
numbers.grid(row=0, column=0, sticky='NS')

scroll = ttk.Scrollbar(root)
scroll.grid(row=0, column=2, sticky='NS')


def on_yscrollcommand(*args):
    scroll.set(*args)  # Synchronizing the scrollbar with the text field
    # Synchronizing a field with numbers with a text field
    numbers.yview_moveto(args[0])


text = tk.Text(root, yscrollcommand=on_yscrollcommand, wrap=tk.NONE,
               background=background, fg='white', font=font_style, insertbackground='white')
text.grid(row=0, column=1, sticky='NSWE')


def scroll_command(*args):
    # The scrollbar movement controls the display of text in both text fields
    text.yview(*args)
    numbers.yview(*args)


scroll.config(command=scroll_command)


def insert_numbers():
    count_of_lines = text.get(1.0, tk.END).count('\n') + 1

    numbers.config(state=tk.NORMAL)
    numbers.delete(1.0, tk.END)
    numbers.insert(1.0, '\n'.join(map(str, range(1, count_of_lines))))
    numbers.config(state=tk.DISABLED)


insert_numbers()


def on_edit(event):
    # Triggered by changes in the text field
    insert_numbers()
    text.edit_modified(0)  # Resetting the text field change flag
    changes()  # update syntax highlight


def save_file_hotkey():
    # Check if the tkinter window is focused
    if root.focus_displayof():
        save_file()


def save_file_as_hotkey():
    # Check if the tkinter window is focused
    if root.focus_displayof():
        save_file_as()


def open_file_hotkey():
    # Check if the tkinter window is focused
    if root.focus_displayof():
        open_file()


def update_highlight_hotkey():
    # Check if the tkinter window is focused
    if root.focus_displayof():
        changes()


def main():
    keyboard.add_hotkey('ctrl+s', save_file_hotkey)  # save file hotkey
    # save as file hotkey
    keyboard.add_hotkey('ctrl+shift+s', save_file_as_hotkey)
    keyboard.add_hotkey('ctrl+o', open_file_hotkey)  # open file hotkey
    # update syntax highlight hotkey
    keyboard.add_hotkey('ctrl+shift+p', update_highlight_hotkey)
    text.bind('<<Modified>>', on_edit)

    # Создание тулбара
    menubar = tk.Menu(root)

    # Создание выпадающего меню "File"
    filemenu = tk.Menu(menubar, tearoff=0)
    filemenu.add_command(label="Open", command=open_file, accelerator="Ctrl+O")
    filemenu.add_command(label="Save", command=save_file, accelerator="Ctrl+S")
    filemenu.add_command(label="Save as...",
                         command=save_file_as, accelerator="Ctrl+Shift+S")
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=root.quit)
    menubar.add_cascade(label="File", menu=filemenu)

    # Создание выпадающего меню "Edit"
    editmenu = tk.Menu(menubar, tearoff=0)
    editmenu.add_command(label="Update Highlight",
                         command=changes, accelerator="Ctrl+Shift+P")
    menubar.add_cascade(label="Edit", menu=editmenu)

    # Отображение меню
    root.config(menu=menubar)

    changes()

    # It is necessary that the text field automatically resizes when the window is resized
    root.grid_columnconfigure(1, weight=1)
    root.grid_rowconfigure(0, weight=1)

    root.mainloop()


if __name__ == "__main__":
    main()


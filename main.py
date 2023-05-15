import tkinter
from typing import Any

ROOT_WINDOW_SIZE = "1280x720"


def init_window() -> tkinter.Tk:
    root_window = tkinter.Tk()
    root_window.title("Automata Tools")
    root_window.geometry(ROOT_WINDOW_SIZE)
    return root_window


def destroy_objects(objs: Any) -> None:
    for obj in objs:
        obj.destroy()


def regex_input(root_window: tkinter.Tk) -> str:
    regex_input_var = tkinter.StringVar()
    btn_input_var = tkinter.BooleanVar()
    regex_input_entry = tkinter.Entry(root_window, textvariable=regex_input_var, font=('calibre', 30, 'normal'),)

    sub_btn = tkinter.Button(root_window, text='Submit', command=lambda: btn_input_var.set(True))
    regex_input_entry.pack(pady=50)
    sub_btn.pack()

    sub_btn.wait_variable(btn_input_var)
    destroy_objects(objs=(regex_input_entry, sub_btn))
    return regex_input_var.get()


if __name__ == '__main__':
    root_window: tkinter.Tk = init_window()

    regex = regex_input(root_window=root_window)

    root_window.mainloop()

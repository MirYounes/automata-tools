import tkinter
from typing import Any, List
import tempfile

from PIL import ImageTk, Image

from nfa import Nfa
from dfa import Dfa

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


def image_viewer(root_window: tkinter.Tk, images: List[str]) -> None:
    images = [ImageTk.PhotoImage(Image.open(img)) for img in images]

    image_index = 0

    def _next() -> None:
        nonlocal image_index
        image_index = image_index + 1
        try:
            image_label.config(image=images[image_index])
        except Exception:
            image_index = -1
            _next()

    def back() -> None:
        nonlocal image_index
        image_index = image_index - 1
        try:
            image_label.config(image=images[image_index])
        except Exception:
            image_index = 0
            back()

    tkinter.Button(root_window, text='Back', command=back).pack(side=tkinter.LEFT)
    tkinter.Button(root_window, text='Next', command=_next).pack(side=tkinter.RIGHT)

    image_label = tkinter.Label(root_window, image=images[image_index])

    image_label.pack(pady=150)


if __name__ == '__main__':
    root_window: tkinter.Tk = init_window()

    regex = regex_input(root_window=root_window)

    with tempfile.TemporaryDirectory() as temp_directory:
        nfa = Nfa.regex_to_nfa(regex=regex)
        nfa.normalize()
        nfa_images = nfa.draw(directory=temp_directory)

        dfa = Dfa.nfa_to_dfa(nfa=nfa)
        dfa_images = dfa.draw(directory=temp_directory)

        images = nfa_images + dfa_images
        image_viewer(root_window=root_window, images=images)
    root_window.mainloop()

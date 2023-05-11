import tkinter


ROOT_WINDOW_SIZE = "1280x720"


def init_window() -> tkinter.Tk:
    root_window = tkinter.Tk()
    root_window.title("Automata Tools")
    root_window.geometry(ROOT_WINDOW_SIZE)
    return root_window


def regex_input(root_window: tkinter.Tk) -> None:
    regex_input_var = tkinter.StringVar()
    regex_input_label = tkinter.Label(root_window, text='regex', font=('calibre', 10, 'bold'))
    regex_input_entry = tkinter.Entry(root_window, textvariable=regex_input_var, font=('calibre', 10, 'normal'))
    sub_btn = tkinter.Button(root_window, text='Submit', command=lambda: print(regex_input_var.get()))

    regex_input_label.grid(row=0, column=0)
    regex_input_entry.grid(row=0, column=1)
    sub_btn.grid(row=2, column=1)


if __name__ == '__main__':
    root_window: tkinter.Tk = init_window()

    regex_input(root_window=root_window)

    root_window.mainloop()

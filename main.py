import tkinter


ROOT_WINDOW_SIZE = "1280x720"


def init_window() -> tkinter.Tk:
    root_window = tkinter.Tk()
    root_window.title("Automata Tools")
    root_window.geometry(ROOT_WINDOW_SIZE)
    return root_window


if __name__ == '__main__':
    root_window: tkinter.Tk = init_window()

    root_window.mainloop()

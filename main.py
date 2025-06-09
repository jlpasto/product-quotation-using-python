from tkinter import Tk
from gui import UserFormApp

def main():
    root = Tk()
    app = UserFormApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
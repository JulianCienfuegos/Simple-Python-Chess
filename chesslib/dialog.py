import Tkinter as tk

class MyDialog:
    def __init__(self, parent):
        top = self.top = tk.Toplevel(parent)
        self.myLabel = tk.Label(top, text='Enter your username below')
        self.myLabel.pack()

        self.myEntryBox = tk.Entry(top)
        self.myEntryBox.pack()

        self.mySubmitButton = tk.Button(top, text='Submit', command=self.send)
        self.mySubmitButton.pack()

    def send(self):
        global username
        username = self.myEntryBox.get()
        self.top.destroy()

def onClick():
    inputDialog = MyDialog(root)
    root.wait_window(inputDialog.top)
    print('Username: ', username)

username = 'Empty'
root = tk.Tk()
mainLabel = tk.Label(root, text='Example for pop up input box')
mainLabel.pack()

mainButton = tk.Button(root, text='Click me', command=onClick)
mainButton.pack()

root.mainloop()

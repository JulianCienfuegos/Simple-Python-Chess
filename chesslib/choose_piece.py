import Tkinter as tk
class PieceChooser:
    def __init__(self, parent):
        top = self.top = tk.Toplevel(parent)
        self.myLabel = tk.Label(top, text='Enter your username below')
        self.myLabel.pack()

        self.myEntryBox = tk.Entry(top)
        self.myEntryBox.pack()

        self.mySubmitButton = tk.Button(top, text='Submit', command=self.send)
        self.mySubmitButton.pack()

    def send(self):
        global chosen_piece
        print 'chosen_piece1', chosen_piece
        chosen_piece = self.myEntryBox.get()
        self.top.destroy()
        print 'chosen_piece2', chosen_piece

def onClick(root):
    inputDialog = PieceChooser(root)
    root.wait_window(inputDialog.top)
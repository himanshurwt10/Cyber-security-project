import tkinter as tk

root = tk.Tk()
root.title("Test")
root.geometry("400x300")

label = tk.Label(root, text="Tkinter is working!", font=("Arial", 18))
label.pack(pady=50)

root.mainloop()
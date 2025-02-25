# sensor_gui/gui/notebook_manager.py
from ttkbootstrap import ttk

class NotebookManager:
    def __init__(self, parent):
        self.notebook = ttk.Notebook(parent, style='TNotebook')
        self.notebook.pack(fill='both', expand=True)

    def add_tab(self, frame, title):
        self.notebook.add(frame, text=title)

    def remove_tab_by_title(self, title):
        existing_tabs = {self.notebook.tab(i, "text"): i for i in range(self.notebook.index("end"))}
        if title in existing_tabs:
            self.notebook.forget(existing_tabs[title])

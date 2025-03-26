# gui/notebook_manager.py
"""
@file notebook_manager.py
@brief Einfacher Manager für ein ttk.Notebook, um Tabs hinzuzufügen oder zu entfernen.
"""

from ttkbootstrap import ttk

class NotebookManager:
    """
    @class NotebookManager
    @brief Kapselt ein ttk.Notebook und bietet Methoden zum Hinzufügen/Entfernen von Tabs.
    """
    def __init__(self, parent):
        self.notebook = ttk.Notebook(parent, style='TNotebook')
        self.notebook.pack(fill='both', expand=True)

    def add_tab(self, frame, title):
        """
        @fn add_tab(frame, title)
        @brief Fügt dem Notebook einen neuen Tab hinzu.
        @param frame: das Frame, das in einem Tab angezeigt werden soll
        @param title: Titel des Tabs
        """
        self.notebook.add(frame, text=title)

    def remove_tab_by_title(self, title):
        """
        @fn remove_tab_by_title(title)
        @brief Entfernt einen Tab anhand seines Titels.
        @param title: Titel des zu entfernenden Tabs
        """
        existing_tabs = {self.notebook.tab(i, "text"): i for i in range(self.notebook.index("end"))}
        if title in existing_tabs:
            self.notebook.forget(existing_tabs[title])

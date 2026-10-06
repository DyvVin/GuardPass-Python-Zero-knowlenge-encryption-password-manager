DARK_THEME_STYLE = """
    QMainWindow, QDialog, QMessageBox {
        background-color: #F8F9FA;  /* windows */
    }
    QWidget {
        color: #2B2D42;  /* text */
        font-family: 'Segoe UI', Helvetica, Arial, sans-serif;
        font-size: 14px;
    }
    QLineEdit {
        background-color: #FFFFFF;
        border: 1px solid #C4C8D8;  /* input border */
        border-radius: 6px;
        padding: 8px 12px;
        color: #2B2D42;
    }
    QLineEdit:focus {
        border: 2px solid #726DA8;  /* accent on focus */
    }
    QPushButton {
        background-color: #726DA8;  
        color: #FFFFFF;
        border: none;
        border-radius: 6px;
        padding: 10px 20px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #5F5A93;  
    }
    QPushButton:pressed {
        background-color: #4C487E;
    }
    
    /* small in-list buttons */
    QPushButton#listActionButton {
        background-color: transparent;
        padding: 2px 5px;
        font-size: 16px;
        border-radius: 4px;
        color: #726DA8;
    }
    QPushButton#listActionButton:hover {
        background-color: #EAEBFF;
    }
    QPushButton#listDeleteButton:hover {
        background-color: #FFCCD5;
        color: #FF0055;
    }

    QListWidget {
        background-color: #DCE1F2;
        border: 1px solid #DCE1F2;
        border-radius: 8px;
        padding: 5px;
    }
    QListWidget::item {
        background-color: transparent;
        border-bottom: 1px solid #726DA8;
    }
    QListWidget::item:selected {
        background-color: #7D8CC4;
        color: #FFFFFF;
        border-radius: 4px;
    }
    QProgressBar {
        border: 1px solid #DCE1F2;
        border-radius: 4px;
        text-align: center;
        background-color: #EBEFF9;
        color: #2B2D42;
        font-weight: bold;
    }
    QProgressBar::chunk {
        background-color: #726DA8;
        border-radius: 3px;
    }
    QLabel#titleLabel {
        font-size: 20px;
        font-weight: bold;
        color: #726DA8;
    }
"""

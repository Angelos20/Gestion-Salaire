def getStyleSheet():
    return """
    QLineEdit {
        padding: 10px;
        border-radius: 8px;
        border: 1px solid #ddd;
        color: black;
        font-family: sans-serif;
        background-color: white;
    }

    QLineEdit:focus {
        border: 1px solid #1877f2;
        background-color: #f5faff;
    }

    #titre {
        color: black;
        font-size: 28px;
        font-weight: bold;
        font-family: sans-serif;
    }

    QPushButton {
        background-color: #0A1640;
        color: white;
        font-weight: bold;
        font-size: 15px;
        padding: 10px 20px;
        border-radius: 6px;
        font-family: sans-serif;
        max-width: 120px;
    }

    QPushButton:hover {
        background-color: #1E6FD9;
    }

    QPushButton:pressed {
        background-color: #09122e;
    }

    QPushButton:checked {
        background-color: #0A1640;
    }

    #btn_close {
        background-color: transparent;
        color: red;
        border-radius: 8px;
        font-weight: bold;
        font-size: 22px;
        border: none;
        padding: 6px;
    }

    #btn_close:hover {
        background-color: rgba(255, 0, 0, 0.1);
    }

    QComboBox {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 6px;
        background-color: white;
        color: black;
        font-size: 14px;
        font-family: sans-serif;
    }

    QComboBox:hover {
        border: 1px solid #1877f2;
    }

    QComboBox QAbstractItemView {
        background-color: white;
        color: black;
        selection-background-color: #1877f2;
        selection-color: white;
        border-radius: 6px;
    }

    QComboBox::drop-down {
        border: none;
    }

    QLabel {
        font-family: sans-serif;
    }
    
    QTableWidget {
        background-color: white;
        color: black;
        border: 1px solid #C2D4E8;
    }

    QHeaderView::section {
        background-color: #0A1628;
        color: white;
        /*padding: 8px;*/
        font-weight: bold;
        border: none;
    }

    QTableWidget::item {
        /*padding: 5px;*/
        border: none;
    }

    /* Supprime effet de focus */
    QTableWidget::item:focus {
        outline: none;
    }

    /* Sélection propre */
    QTableWidget::item:selected {
        background-color: #cce5ff;
        color: black;
    }
    """
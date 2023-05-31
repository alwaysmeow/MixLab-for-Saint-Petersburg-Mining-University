from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel

class ReagentDeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Удаление реагента")
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.button(QDialogButtonBox.Ok).setText("Ок")
        button_box.button(QDialogButtonBox.Cancel).setText("Отмена")

        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout = QVBoxLayout()
        label = QLabel("Этот реагент используется в одном или более тесте.\nЕго удаление так же приведет к удалению этих тестов.")
        label.setContentsMargins(10, 10, 10, 10)
        layout.addWidget(label)
        layout.addWidget(button_box)

        self.setLayout(layout)

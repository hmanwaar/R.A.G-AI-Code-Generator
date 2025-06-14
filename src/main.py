import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QTextEdit, QPushButton, QLabel,
                            QTabWidget, QFileDialog, QMessageBox, QProgressBar)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from dotenv import load_dotenv

from rag.rag_manager import RAGManager
from code_analysis.analyzer import CodeAnalyzer
from utils.helpers import format_code_analysis_results, save_to_temp_file

# Load environment variables
load_dotenv()

class WorkerThread(QThread):
    """Worker thread for running long operations."""
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)
    
    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        try:
            result = self.func(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RAG-based AI Code Generator")
        self.setMinimumSize(1200, 800)
        
        # Initialize components
        self.rag_manager = RAGManager()
        self.code_analyzer = CodeAnalyzer()
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Create tab widget
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # Create tabs
        self.code_generation_tab = self.create_code_generation_tab()
        self.code_analysis_tab = self.create_code_analysis_tab()
        
        tabs.addTab(self.code_generation_tab, "Code Generation")
        tabs.addTab(self.code_analysis_tab, "Code Analysis")
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
    def create_code_generation_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Input section
        input_label = QLabel("Enter your requirements:")
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Describe what you want the code to do...")
        
        # Output section
        output_label = QLabel("Generated Code:")
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        
        # Buttons
        button_layout = QHBoxLayout()
        generate_button = QPushButton("Generate Code")
        generate_button.clicked.connect(self.generate_code)
        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self.clear_generation)
        
        button_layout.addWidget(generate_button)
        button_layout.addWidget(clear_button)
        
        # Add widgets to layout
        layout.addWidget(input_label)
        layout.addWidget(self.input_text)
        layout.addLayout(button_layout)
        layout.addWidget(output_label)
        layout.addWidget(self.output_text)
        
        return widget
    
    def create_code_analysis_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # File selection
        file_layout = QHBoxLayout()
        self.file_path_label = QLabel("No file selected")
        select_file_button = QPushButton("Select File")
        select_file_button.clicked.connect(self.select_file)
        
        file_layout.addWidget(self.file_path_label)
        file_layout.addWidget(select_file_button)
        
        # Analysis output
        analysis_label = QLabel("Analysis Results:")
        self.analysis_text = QTextEdit()
        self.analysis_text.setReadOnly(True)
        
        # Analysis buttons
        button_layout = QHBoxLayout()
        analyze_button = QPushButton("Analyze Code")
        analyze_button.clicked.connect(self.analyze_code)
        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self.clear_analysis)
        
        button_layout.addWidget(analyze_button)
        button_layout.addWidget(clear_button)
        
        # Add widgets to layout
        layout.addLayout(file_layout)
        layout.addLayout(button_layout)
        layout.addWidget(analysis_label)
        layout.addWidget(self.analysis_text)
        
        return widget
    
    def generate_code(self):
        requirements = self.input_text.toPlainText().strip()
        if not requirements:
            QMessageBox.warning(self, "Warning", "Please enter your requirements first.")
            return
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.statusBar().showMessage("Generating code...")
        
        # Create worker thread for code generation
        self.worker = WorkerThread(self.rag_manager.generate_code, requirements)
        self.worker.finished.connect(self.handle_generated_code)
        self.worker.error.connect(self.handle_error)
        self.worker.start()
    
    def analyze_code(self):
        file_path = self.file_path_label.text()
        if file_path == "No file selected":
            QMessageBox.warning(self, "Warning", "Please select a file to analyze.")
            return
        
        try:
            with open(file_path, 'r') as f:
                code = f.read()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error reading file: {str(e)}")
            return
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.statusBar().showMessage("Analyzing code...")
        
        # Create worker thread for code analysis
        self.worker = WorkerThread(self.code_analyzer.analyze_code, code, file_path)
        self.worker.finished.connect(self.handle_analysis_results)
        self.worker.error.connect(self.handle_error)
        self.worker.start()
    
    def handle_generated_code(self, code: str):
        self.output_text.setText(code)
        self.progress_bar.setVisible(False)
        self.statusBar().showMessage("Code generated successfully")
        
        # Ask if user wants to analyze the generated code
        reply = QMessageBox.question(
            self,
            "Analyze Generated Code",
            "Would you like to analyze the generated code?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Save to temp file and analyze
            temp_file = save_to_temp_file(code)
            self.file_path_label.setText(temp_file)
            self.analyze_code()
    
    def handle_analysis_results(self, results: dict):
        formatted_results = format_code_analysis_results(results)
        self.analysis_text.setText(formatted_results)
        self.progress_bar.setVisible(False)
        self.statusBar().showMessage("Analysis completed")
    
    def handle_error(self, error_msg: str):
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Error", f"An error occurred: {error_msg}")
        self.statusBar().showMessage("Error occurred")
    
    def select_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select File",
            "",
            "Python Files (*.py);;All Files (*.*)"
        )
        if file_name:
            self.file_path_label.setText(file_name)
    
    def clear_generation(self):
        self.input_text.clear()
        self.output_text.clear()
    
    def clear_analysis(self):
        self.file_path_label.setText("No file selected")
        self.analysis_text.clear()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 
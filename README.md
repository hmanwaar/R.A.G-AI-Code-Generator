# RAG-based AI Code Generator

An intelligent code generation and analysis tool that uses Retrieval Augmented Generation (RAG) to assist developers in writing, analyzing, and improving code.

## Features

- **Code Generation**: Generate code based on natural language requirements
- **Code Analysis**: Scan code for vulnerabilities and potential improvements
- **RAG Integration**: Uses advanced RAG techniques to provide context-aware code generation
- **User-Friendly GUI**: Modern interface built with PyQt6
- **Code Quality Tools**: Integration with pylint, bandit, and black for code quality

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file in the project root with your OpenAI API key:
   ```
   # OpenAI API Key
   # Get your API key from https://platform.openai.com/api-keys
   OPENAI_API_KEY=your_api_key_here

   # Optional: Model settings
   # MODEL_NAME=gpt-4  # or gpt-3.5-turbo
   # TEMPERATURE=0.7
   # MAX_TOKENS=2000
   ```

## Project Structure

```
.
├── src/
│   ├── gui/                 # GUI components
│   ├── rag/                # RAG system components
│   ├── code_analysis/      # Code analysis tools
│   └── utils/              # Utility functions
├── tests/                  # Test files
├── data/                   # Vector database and embeddings
├── requirements.txt        # Project dependencies
└── README.md              # Project documentation
```

## Usage

1. Run the application:
   ```bash
   python src/main.py
   ```
2. Use the GUI to:
   - Input your code requirements
   - Generate code
   - Analyze existing code
   - Get improvement suggestions

## Features in Detail

### Code Generation
- Enter your requirements in natural language
- The RAG system will generate appropriate code
- Generated code can be analyzed immediately
- Code is stored in the vector database for future reference

### Code Analysis
- Analyze Python files for:
  - Security vulnerabilities (using Bandit)
  - Code quality issues (using Pylint)
  - Code style (using Black)
  - Structural analysis (using AST)
- Get detailed improvement suggestions
- View formatted analysis results

### RAG System
- Uses OpenAI's GPT models for code generation
- Maintains a vector database of code snippets
- Provides context-aware code generation
- Learns from analyzed code

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
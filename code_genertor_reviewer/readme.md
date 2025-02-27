# AI-Powered Code Generator & Reviewer

## Overview
This Streamlit application generates code based on user requirements, reviews the generated code for correctness, and provides feedback. If the code is deemed correct, a README documentation in markdown format is also generated.

## Features
- **Code Generation**: Uses an LLM to generate code based on a given requirement.
- **Code Review**: The generated code is reviewed for correctness and feedback is provided if necessary.
- **Feedback Loop**: If the code is incorrect, the user can refine the requirement based on the feedback and regenerate the code.
- **README Generation**: Once the code is reviewed and accepted, a README file is generated to document the functionality.

## Installation

### Prerequisites
Ensure you have Python installed along with the required dependencies.

### Setup
1. Clone the repository or download the script.
2. Install dependencies using:
   ```sh
   pip install streamlit langchain_groq python-dotenv pydantic
   ```
3. Set up environment variables by creating a `.env` file and adding your API key:
   ```
   GROQ_API_KEY=your_api_key_here
   ```

## Usage
Run the application using:
```sh
streamlit run app.py
```

### Steps to Use:
1. Enter your requirement in the provided text area.
2. Click the **Generate Code** button.
3. The application will generate the code and display it.
4. The LLM reviews the code and provides feedback.
5. If the code is correct, a README is generated and displayed.
6. If incorrect, modify your requirement and regenerate the code.

## Example
**Input Requirement:**
```
Write a Python function to check if a given string is a palindrome.
```

**Generated Code:**
```python
def is_palindrome(s):
    s = s.lower().replace(" ", "")
    return s == s[::-1]
```

**Review Result:**
```
The code is reviewed and can be used!
```

**Generated README:**
```
# Palindrome Checker
This script contains a function to check if a given string is a palindrome.
## Function:
```python
def is_palindrome(s):
    s = s.lower().replace(" ", "")
    return s == s[::-1]
```
```

## License
This project is licensed under the MIT License.


import sys
import subprocess
import tempfile
import os
from typing import Dict, Any

def execute_python_code(code: str, timeout: int = 30) -> Dict[str, Any]:
    """
    Executes a block of Python code in a secure temporary file using a subprocess.
    
    Args:
        code (str): The Python code to execute.
        timeout (int): Timeout in seconds.
        
    Returns:
        Dict[str, Any]: A dictionary containing 'success' (bool), 'stdout' (str), 'stderr' (str),
                        and 'exit_code' (int).
    """
    # Create a temporary file to hold the code
    try:
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode='w', encoding='utf-8') as temp_file:
            temp_file.write(code)
            temp_file_path = temp_file.name

        # Determine the correct Python executable
        python_executable = sys.executable or "python"

        # Run the code as a subprocess
        result = subprocess.run(
            [python_executable, temp_file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout
        )

        success = (result.returncode == 0)
        return {
            "success": success,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode
        }

    except subprocess.TimeoutExpired as e:
        return {
            "success": False,
            "stdout": e.stdout if e.stdout else "",
            "stderr": f"Error: Execution timed out after {timeout} seconds.",
            "exit_code": -1
        }
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"System error executing code: {str(e)}",
            "exit_code": -2
        }
    finally:
        # Clean up temporary file safely
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except Exception:
                pass

if __name__ == "__main__":
    # Test execution
    test_code = """
import math
print("Calculating square root of 16...")
print(f"Result: {math.sqrt(16)}")
"""
    print("Executing test code:")
    res = execute_python_code(test_code)
    print(res)

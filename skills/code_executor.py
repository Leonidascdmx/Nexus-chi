import sys
import subprocess
import tempfile
import os
from typing import Dict, Any

def execute(code: str, timeout: int = 20) -> str:
    """
    Executes a block of Python code in a secure temporary file using a subprocess.
    Returns a formatted execution report as a string.
    """
    temp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode='w', encoding='utf-8') as temp_file:
            temp_file.write(code)
            temp_file_path = temp_file.name

        python_executable = sys.executable or "python"

        result = subprocess.run(
            [python_executable, temp_file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout
        )

        success = (result.returncode == 0)
        report = f"--- [HI-NEXUS Subprocess Execution Sandbox] ---\n"
        report += f"Status: {'SUCCESS' if success else 'FAILURE'}\n"
        report += f"Exit Code: {result.returncode}\n"
        report += f"Output (STDOUT):\n{result.stdout.strip() if result.stdout else '[Empty]'}\n"
        if result.stderr:
            report += f"Errors (STDERR):\n{result.stderr.strip()}\n"
        return report

    except subprocess.TimeoutExpired as e:
        return f"--- [HI-NEXUS Subprocess Execution Sandbox] ---\nStatus: TIMEOUT\nError: Execution exceeded {timeout} seconds.\n"
    except Exception as e:
        return f"--- [HI-NEXUS Subprocess Execution Sandbox] ---\nStatus: ERROR\nSystem Error: {str(e)}\n"
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except Exception:
                pass

if __name__ == "__main__":
    print(execute("print('Hello from HI-NEXUS sandbox!')"))

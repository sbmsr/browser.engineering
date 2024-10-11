import pytest
import subprocess
import os

@pytest.fixture
def browser_setup():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    browser_path = os.path.join(current_directory, "browser.py")
    return browser_path

def test_browser_execution_without_url(browser_setup):
    browser_path = browser_setup
    command = f"python {browser_path}"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    assert "it seems you forgot to input a url. try again!" in result.stdout.strip(), "Expected output not found"
    assert result.stderr == "", "Unexpected error output"

def test_browser_execution_file(browser_setup):
    browser_path = browser_setup
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test.txt")
    command = f"python {browser_path} file://{file_path}"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    assert "hi" in result.stdout.strip(), "Expected output not found"
    assert result.stderr == "", "Unexpected error output"

def test_browser_execution_url_https(browser_setup):
    browser_path = browser_setup
    command = f"python {browser_path} https://example.org"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    assert "This domain is for use in illustrative examples in documents" in result.stdout, "Expected output not found"
    assert result.stderr == "", "Unexpected error output"

def test_browser_execution_url_http(browser_setup):
    browser_path = browser_setup
    command = f"python {browser_path} http://example.org"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    assert "This domain is for use in illustrative examples in documents." in result.stdout, "Expected output not found"
    assert result.stderr == "", "Unexpected error output"

def test_browser_execution_data(browser_setup):
    browser_path = browser_setup
    command = f"python {browser_path} data://text/html,Hello\\ World"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    assert "Hello World" in result.stdout, "Expected output not found"
    assert result.stderr == "", "Unexpected error output"

def test_browser_execution_entities_data(browser_setup):
    browser_path = browser_setup
    command = f"python {browser_path} 'data://text/html,&lt;div&gt;'"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    assert "<div>" in result.stdout, "Expected output not found"
    assert result.stderr == "", "Unexpected error output"

def test_browser_execution_entities_html(browser_setup):
    browser_path = browser_setup
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entities.html")
    command = f"python {browser_path} file://{file_path}"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    assert "<div>" in result.stdout, "Expected output not found"
    assert result.stderr == "", "Unexpected error output"

if __name__ == "__main__":
    pytest.main([__file__])



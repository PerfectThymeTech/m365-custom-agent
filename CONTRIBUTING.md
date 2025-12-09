# Contributing to M35 Custom Agent

We welcome contributions to the M35 Custom Agent project! This document provides guidelines for contributing.

## Development Setup

1. Fork the repository

2. Clone your fork:

    ```bash
    git clone https://github.com/PerfectThymeTech/m365-custom-agent.git
    cd m365-custom-agent
    ```

3. Install dependencies using [uv](https://docs.astral.sh/uv/):

    ```bash
    # Open copilot directory
    cd code/copilot

    # Install uv dependencies
    uv sync
    ```

4. Activate virtual environment:

    For Windows:
    ```bash
    venv\Scripts\activate
    ```

    For Linux/MacOS:
    ```bash
    source venv/bin/activate
    ```

5. **Set Environment Variables**: Create a `.env` file in the `code/copilot` directory based on the `.env.TEMPLATE` file and fill in the required values.

6. Run backend service:

    ```bash
    fastapi dev app/main.py
    ```

7. Open docs at `http://localhost:8000/docs`

## Making Changes

1. Create a feature branch:

    ```bash
    git checkout -b feature/your-feature-name
    ```

2. Make your changes following the code style guidelines

    ```bash
    # Run to ensure linting rules are followed
    pre-commit run --all-files
    ```

3. Add tests for new functionality

4. Run tests to ensure everything works

5. Update documentation as needed

## Code Style

- Follow PEP 8 for Python code style
- Use type hints for all function parameters and return values
- Add docstrings for all public functions and classes
- Keep line length to 100 characters maximum

## Testing

Run tests before submitting:

```bash
# Run basic tests
python tests/test_basic.py

# With pytest (if available)
pytest tests/
```

## Submitting Changes

1. Commit your changes with descriptive messages
2. Push to your fork
3. Create a pull request with:
   - Clear description of changes
   - Reference to any related issues
   - Screenshots for UI changes

## Issues

When reporting issues, please include:
- Python version
- Operating system
- Error messages and stack traces
- Steps to reproduce
- Expected vs actual behavior

Thank you for contributing!

# Contributing Guidelines

Thank you for your interest in contributing to the Inclusive Space Index Assessment Tool. This guide will help you get started with development and understand our contribution process.

## Development Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r app/requirements.txt
   ```
3. Create a `.env` file with required variables (see [SETUP.md](SETUP.md))
4. Run the application:
   ```bash
   docker compose up --build
   ```

## Code Style Guidelines

1. **Type Hints**
   - Use type hints for all function parameters and return values
   - Example:
     ```python
     def calculate_score(responses: dict[str, int]) -> int:
         return sum(responses.values())
     ```

2. **Documentation**
   - Include docstrings for all modules, classes, and functions
   - Keep inline comments focused on explaining complex logic
   - Update relevant documentation when making changes

3. **Function Design**
   - Keep functions focused and single-purpose
   - Use descriptive names that indicate the function's purpose
   - Follow the Single Responsibility Principle

4. **Error Handling**
   - Use try/except blocks for external operations (file I/O, database)
   - Provide meaningful error messages
   - Log errors appropriately
   - Validate inputs before processing

## Testing Requirements

1. **Unit Tests**
   - Write tests for new functionality
   - Ensure existing tests pass before submitting changes
   - Include edge cases in test coverage
   - Use pytest for testing

2. **Test Coverage**
   - Aim for high test coverage of business logic
   - Include both success and failure cases
   - Mock external dependencies appropriately

## Pull Request Process

1. Fork the repository
2. Create a feature branch with a descriptive name
3. Make your changes following the guidelines above
4. Ensure all tests pass
5. Update documentation as needed
6. Submit a pull request with:
   - Clear description of changes
   - Any related issue numbers
   - Screenshots for UI changes
   - Notes about testing performed

## Questions or Issues?

Feel free to open an issue for:

- Bug reports
- Feature requests
- Documentation improvements
- General questions

See [TECHNICAL.md](TECHNICAL.md) for detailed information about the project's architecture and implementation details.

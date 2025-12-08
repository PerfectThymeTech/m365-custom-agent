# 🎯 Microsoft 365 Agents SDK Reference Implementation

![Repository Banner](/docs/images/banner.png)

This repository contains a reference implementation which demonstrates how to leverage the Microsoft 365 Agents SDK to build custom agents. The implementation showcases best practices, design patterns, and practical examples to help developers get started with creating their own agents using the SDK.

## ✨ Key Features

- **FastAPI Backend**: The backend is built using FastAPI, providing a high-performance and easy-to-use framework for building APIs.
- **Modular Design**: The implementation follows a modular design approach, allowing developers to easily extend and customize the functionality of their agents.
- **Logging and Monitoring**: Integrated logging and monitoring capabilities using OpenTelemetry to help developers track the performance and behavior of their agents.
- **Authentication**: Built-in support for authentication mechanisms to secure agent interactions.
- **Channel Integration**: Demonstrates how to integrate with various communication channels supported by the Microsoft 365 Agents SDK.
- **Example Agents**: Includes example agents demonstrating various use cases and functionalities.

## Getting Started

To get started with the reference implementation, follow these steps:

1. **Clone the Repository**:

    ```bash
    git clone https://github.com/PerfectThymeTech/m365-custom-agent.git
    cd m365-custom-agent
    ```

2. **Install Dependencies**:

    ```bash
    # Open copilot directory
    cd code/copilot

    # Install uv dependencies
    uv sync
    ```

3. **Run the Backend Application**:

    ```bash
    fastapi dev app/main.py
    ```

4. **Access the API Documentation**:

    Open your browser and navigate to `http://localhost:8000/docs` to access the interactive API documentation.

## 📚 Documentation

Comprehensive documentation is available to help you get started and make the most of the Microsoft 365 Custom Agent project. Visit the Documentation folder for more information.

## Contributing

Contributions are welcome! If you would like to contribute to this repository, please follow the [contribution guidelines](/CONTRIBUTING.md).

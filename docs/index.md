# Aurelian

## Getting Started

### Prerequisites

Ensure you have the following installed:

- [Poetry](https://python-poetry.org/docs/#installation) (for managing dependencies)
- Python 3.11 or later

### Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/your-org/aurelian.git
   cd aurelian
   ```
2. **Install dependencies:**
   ```sh
   poetry install
   ```
3. **Verify installation:**
   ```sh
   poetry run aurelian --help
   ```

### Authentication Setup

Aurelian uses [Logfire](https://logfire.pydantic.dev/docs/why/) for logging (an observability platform that 
provides logging, tracing, and metrics capabilities), which requires 
authentication. If you encounter the following error:

```
No Logfire project credentials found.
You are not authenticated. Please run `logfire auth` to authenticate.
```

Follow these steps:

1. **Authenticate with Logfire:**
   ```sh
   poetry run logfire auth
   ```
2. **(Optional) Set a production token:** If running in a production environment, set the `LOGFIRE_TOKEN` environment variable:
   ```sh
   export LOGFIRE_TOKEN=your_token_here
   ```

### Running Aurelian

Once authenticated, you can use Aurelian's CLI:

1. **Run the mapper tool:**
   ```sh
   poetry run aurelian mapper
   ```
2. **Explore available commands:**
   ```sh
   poetry run aurelian --help
   ```

For more details, refer to the project documentation.


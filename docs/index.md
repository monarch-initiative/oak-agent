# Aurelian

## Getting Started

### Prerequisites

Ensure you have the following installed:

- [Poetry](https://python-poetry.org/docs/#installation) (for managing dependencies)
- Python 3.11 or later

### Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/monarch-initiative/aurelian.git
   cd aurelian
   ```
2. **Install dependencies:**
   ```sh
   poetry install --extras=gradio
   ```
3. **Verify installation:**
   ```sh
   poetry run aurelian --help
   ```

### Setting up up Logfire

Aurelian uses [Logfire](https://logfire.pydantic.dev/docs/why/) for logging (an observability platform that 
provides logging, tracing, and metrics), which requires 
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

### Getting an OpenAI key

In order to use OpenAI models, you'll need an API key. Follow the instructions 
[here](https://platform.openai.com/docs/quickstart). After you have an OpenAI key,
set the environment variable `OPENAI_API_KEY` to this key, for example like this:

```
export OPENAI_API_KEY="your_api_key_here"
```

### Running Aurelian

Once authenticated, you can use Aurelian's CLI:

**Run the mapper tool:**
   ```sh
   poetry run aurelian mapper
   ```

For more details, refer to the project documentation.


### Troubleshooting 



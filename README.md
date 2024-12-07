# LeetCode Solver Bot

An automated bot that solves LeetCode problems using GPT-4 and browser automation. Built with Python, Playwright, and AgentQL.

## Features

- Automated login to LeetCode
- Random problem selection
- Intelligent solution generation using GPT-4
- Automatic code submission
- Persistent login state management
- Detailed logging system

## Prerequisites

- Python 3.12+
- Poetry for dependency management
- OpenAI API key
- AgentQL API key
- LeetCode account

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/leetcode-solver.git
cd leetcode-solver
```

2. Install dependencies using Poetry:
```bash
poetry install
```

3. Install Playwright browsers:
```bash
poetry run playwright install
```

4. Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

5. Add your API keys to `.env`:
```
OPENAI_API_KEY=your_openai_api_key
AGENTQL_API_KEY=your_agentql_api_key
LEETCODE_USERNAME=your_leetcode_username
LEETCODE_PASSWORD=your_leetcode_password
```

## Usage

Run the bot with Poetry:
```bash
poetry run python src/bot.py [number_of_problems]
```

The `number_of_problems` argument is optional and defaults to 1.

## Project Structure

- `src/`
  - `bot.py` - Main entry point
  - `utils/` - Utility functions
    - `login.py` - LeetCode login handling
    - `select_random.py` - Random problem selection
    - `solve_problem.py` - Problem solving logic
- `logs/` - Log files directory
- `.env` - Environment variables
- `leetcode_login.json` - Persistent login state

## Dependencies

- `playwright` - Browser automation
- `agentql` - Web scraping and element selection
- `openai` - GPT-4 API integration
- `python-dotenv` - Environment variable management
- `black` - Code formatting

## License

This project is licensed under the GNU General Public License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Notes

- The bot uses GPT-4 for solution generation, which requires an OpenAI API key with GPT-4 access
- Solutions are formatted with 4-space indentation
- Login state is saved to avoid repeated logins
- Detailed logs are saved in the `logs` directory
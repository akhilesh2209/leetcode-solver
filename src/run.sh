echo "Running the bot..."

# Update package list and install prerequisites
sudo apt update
sudo apt install -y software-properties-common

# Add deadsnakes PPA and install Python 3.12
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3.12-dev

# Ensure pip is installed for Python 3.12
curl -sS https://bootstrap.pypa.io/get-pip.py | sudo python3.12

# Install pipx
python3.12 -m pip install --user pipx
python3.12 -m pipx ensurepath

# Install Poetry using pipx
pipx install poetry

# Install project dependencies using Poetry
poetry install

# Run the bot
poetry run python bot.py
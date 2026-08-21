#!/bin/bash
# Install learning-ai from GitHub
set -e

pip install "git+https://github.com/FlossWare/learning-ai.git"

echo "learning-ai installed successfully"
echo "Verify: python3 -c 'import learning_ai; print(learning_ai.__version__)'"

#!/bin/bash

#Define the script name
SCRIPT_NAME="VersaMesh"
DIST_DIR="dist"
BUILD_JSON="$DIST_DIR/build.json"
README_SOURCE="README.dist.md"
README_DEST="$DIST_DIR/README.md"

# Get the current Git branch
BRANCH_NAME=$(git rev-parse --abbrev-ref HEAD)

# Convert branch name to lowercase and sanitize
BRANCH_SUFFIX=$(echo "$BRANCH_NAME" | tr '[:upper:]' '[:lower:]' | tr -cd '[:alnum:]_-')

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install Python if missing
install_python() {
    echo "Python is not installed. Attempting to install..."

    # Detect OS and install Python
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "Detected Linux system..."
        sudo apt update && sudo apt install -y python3 python3-pip || sudo yum install -y python3 python3-pip
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "Detected macOS system..."
        brew install python3
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        echo "Detected Windows system..."
        echo "Please install Python manually from https://www.python.org/downloads/"
        exit 1
    else
        echo "Unknown OS. Unable to install Python automatically."
        exit 1
    fi
}

# Ensure Python is installed
if command_exists py; then
    PYTHON_CMD="py"
elif command_exists python3; then
    PYTHON_CMD="python3"
elif command_exists python; then
    PYTHON_CMD="python"
else
    install_python
    if command_exists py; then
        PYTHON_CMD="py"
    elif command_exists python3; then
        PYTHON_CMD="python3"
    elif command_exists python; then
        PYTHON_CMD="python"
    else
        echo "Python installation failed. Please install Python manually."
        exit 1
    fi
fi

#Ensure the dist directory exists
mkdir -p "$DIST_DIR"

# Ensure semver is installed
"$PYTHON_CMD" -m ensurepip
"$PYTHON_CMD" -m pip install --quiet semver || { echo "Failed to install semver"; exit 1; }

# Get the latest semantic version tag using Git
LATEST_TAG=$(git tag --sort=-v:refname | grep -E '^v[0-9]+\.[0-9]+\.[0-9]+$' | head -n 1)

# Get the next version using Python script
NEW_VERSION=$("$PYTHON_CMD" - <<EOF
import semver

latest_tag = "$LATEST_TAG".strip() or "v0.0.0"

# Remove 'v' prefix if present
if latest_tag.startswith("v"):
    latest_tag = latest_tag[1:]

# Remove any previous branch suffix
base_version = latest_tag.split('-')[0]

# Parse version and bump the patch version
new_version = semver.Version.parse(base_version).bump_patch()

# Append branch name for non-main branches
branch_suffix = "$BRANCH_SUFFIX"
if branch_suffix and branch_suffix != "main":
    new_version = f"{new_version}-{branch_suffix}"

# Print with 'v' prefix for consistency
print(f"v{new_version}")
EOF
)

# Get the current Git commit hash and timestamp
COMMIT_HASH=$(git rev-parse --short HEAD)
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

pyinstaller --onefile --collect-all=pymeshlab --name "$SCRIPT_NAME" ./source/run.py

# Move the output executable to the dist directory
mv "dist/$SCRIPT_NAME" "$DIST_DIR/$SCRIPT_NAME.exe"

# Create a new Git tag with the updated version
git tag -a "$NEW_VERSION" -m "Build version $NEW_VERSION created on $TIMESTAMP"
git push origin "$NEW_VERSION"

# Generate the build.json file
cat <<EOF > "$BUILD_JSON"
{
    "build_time": "$TIMESTAMP",
    "commit_hash": "$COMMIT_HASH",
    "tag_name": "$NEW_VERSION",
    "__version__": "$NEW_VERSION",
    "executable": "$SCRIPT_NAME.exe"
}
EOF

# Copy and rename the README file
if [[ -f "$README_SOURCE" ]]; then
    cp "$README_SOURCE" "$README_DEST"
    echo "Copied $README_SOURCE to $README_DEST"
else
    echo "Warning: $README_SOURCE not found, skipping."
fi

# Output success message
echo "Build complete. Executable and metadata are in the $DIST_DIR folder."
echo "Git tag '$NEW_VERSION' created and pushed."
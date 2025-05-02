#!/bin/bash
# Script to run tests with coverage report

echo "Running tests with coverage..."

# Create coverage directory if it doesn't exist
mkdir -p coverage

# Run pytest with coverage
python -m pytest tests/ \
    --cov=insightforge \
    --cov-report=term \
    --cov-report=html:coverage/html \
    --cov-report=xml:coverage/coverage.xml \
    -v

# Show coverage report summary
echo -e "\nCoverage Summary:"
if [ -f coverage/coverage.xml ]; then
    COVERAGE=$(python -c "import xml.etree.ElementTree as ET; tree = ET.parse('coverage/coverage.xml'); root = tree.getroot(); print(f\"Overall coverage: {root.attrib.get('line-rate', '0.0')}\")")
    echo $COVERAGE
fi

echo -e "\nDetailed HTML report generated at: coverage/html/index.html"
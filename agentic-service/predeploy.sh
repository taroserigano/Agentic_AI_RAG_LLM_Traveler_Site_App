#!/bin/bash
# Prepare for Lambda deployment
echo "Preparing Lambda deployment..."

# Backup original agents/__init__.py
cp agents/__init__.py agents/__init__.py.bak 2>/dev/null || true

# Use minimal __init__.py for Lambda
echo '"""Agents package for Lambda - simplified."""' > agents/__init__.py

echo "Ready for deployment"

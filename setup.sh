#!/bin/bash

# Adaptive Security Testing Scheduler - Setup Script

echo "🚀 Setting up Adaptive Security Testing Scheduler..."
echo ""

# Check Python version
echo "📌 Checking Python version..."
python --version

if [ $? -ne 0 ]; then
    echo "❌ Python 3 is not installed. Please install Python 3.7 or later."
    exit 1
fi

# Install Python dependencies
echo ""
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "⚠️  Warning: Some dependencies may have failed to install."
else
    echo "✅ Python dependencies installed successfully!"
fi

# Check Semgrep installation
echo ""
echo "🔍 Checking Semgrep installation..."
if command -v semgrep &> /dev/null; then
    echo "✅ Semgrep is already installed!"
    semgrep --version
else
    echo "📥 Installing Semgrep..."
    pip install semgrep
    
    if [ $? -eq 0 ]; then
        echo "✅ Semgrep installed successfully!"
    else
        echo "❌ Failed to install Semgrep. Please install manually:"
        echo "   pip install semgrep"
    fi
fi

# Check OWASP ZAP CLI
echo ""
echo "🕷️  Checking OWASP ZAP CLI installation..."
if command -v zap-cli &> /dev/null; then
    echo "✅ ZAP CLI is already installed!"
    zap-cli --version
else
    echo "📥 Installing ZAP CLI..."
    pip install zapcli
    
    if [ $? -eq 0 ]; then
        echo "✅ ZAP CLI installed successfully!"
        echo "⚠️  Note: For full DAST functionality, you need to install OWASP ZAP:"
        echo "   Download from: https://www.zaproxy.org/download/"
    else
        echo "❌ Failed to install ZAP CLI. Please install manually:"
        echo "   pip install zapcli"
    fi
fi

# Create reports directory
echo ""
echo "📁 Creating reports directory..."
mkdir -p reports
echo "✅ Reports directory created!"

# Make script executable
echo ""
echo "🔧 Making security_scheduler.py executable..."
chmod +x security_scheduler.py
echo "✅ Script is now executable!"

# Final message
echo ""
echo "="*70
echo "✅ Setup complete!"
echo "="*70
echo ""
echo "🎯 Quick Start:"
echo ""
echo "1. Test with simulated scanners:"
echo "   python security_scheduler.py --files 'app.py' --msg 'test commit'"
echo ""
echo "2. Test with real tools (Semgrep):"
echo "   python security_scheduler.py --files 'app.py' --msg 'test' --use-real-tools"
echo ""
echo "3. Run full scan with DAST (requires running application):"
echo "   python security_scheduler.py --files 'app.py' --msg 'test' --use-real-tools --target-url 'http://localhost:5000'"
echo ""
echo "📚 See README.md for detailed documentation and examples!"
echo ""

#!/bin/bash

# Test script for Adaptive Security Testing Scheduler

echo "🧪 Running Security Scanner Tests"
echo "=================================="
echo ""

# Test 1: Basic scan with simulated scanners
echo "Test 1: Basic scan with simulated scanners"
echo "-------------------------------------------"
python security_scheduler.py \
  --files "examples/vulnerable_app.py" \
  --msg "added authentication logic" \
  --no-real-tools

echo ""
echo "Press Enter to continue to next test..."
read

# Test 2: Scan with Semgrep (real SAST)
echo ""
echo "Test 2: Scan with Semgrep SAST"
echo "-------------------------------"
python security_scheduler.py \
  --files "examples/vulnerable_app.py" \
  --msg "security updates" \
  --use-real-tools

echo ""
echo "Press Enter to continue to next test..."
read

# Test 3: Multiple file types
echo ""
echo "Test 3: Infrastructure as Code scan"
echo "------------------------------------"
python security_scheduler.py \
  --files "main.tf,variables.tf,config.yaml" \
  --msg "infrastructure changes" \
  --no-real-tools

echo ""
echo "Press Enter to continue to next test..."
read

# Test 4: Dependency scan
echo ""
echo "Test 4: Dependency vulnerability scan"
echo "--------------------------------------"
python security_scheduler.py \
  --files "Dockerfile,requirements.txt,package.json" \
  --msg "updated dependencies" \
  --no-real-tools

echo ""
echo "Press Enter to continue to next test..."
read

# Test 5: Save JSON report
echo ""
echo "Test 5: Save scan results as JSON"
echo "----------------------------------"
python security_scheduler.py \
  --files "examples/vulnerable_app.py,config.yaml" \
  --msg "critical security fix" \
  --save-json \
  --no-real-tools

echo ""
echo "✅ All tests completed!"
echo ""
echo "📁 Check the reports/ directory for JSON reports"
ls -lh reports/ 2>/dev/null || echo "No reports generated yet"

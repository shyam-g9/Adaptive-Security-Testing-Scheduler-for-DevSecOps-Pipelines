# Quick Reference Guide

## 🚀 Installation

```bash
# Quick setup (recommended)
./setup.sh

# Manual installation
pip install -r requirements.txt
pip install semgrep
pip install zapcli  # Optional for DAST
```

## 📋 Common Commands

### Basic Scans

```bash
# Simulated scan (no tools required)
python security_scheduler.py --files "app.py" --msg "updates" --no-real-tools

# Real SAST with Semgrep
python security_scheduler.py --files "app.py" --msg "updates" --use-real-tools

# Multiple files
python security_scheduler.py --files "app.py,utils.py,config.yaml" --msg "refactor"
```

### Advanced Scans

```bash
# Full scan with DAST (requires running app)
python security_scheduler.py \
  --files "app.py,api.py" \
  --msg "API changes" \
  --use-real-tools \
  --target-url "http://localhost:5000"

# Save JSON report
python security_scheduler.py \
  --files "app.py" \
  --msg "security fix" \
  --save-json

# Custom output location
python security_scheduler.py \
  --files "main.tf" \
  --msg "infra update" \
  --output "custom/path/report.json"
```

## 🎯 File Type Triggers

| File Extension | Triggered Scanners |
|----------------|-------------------|
| `.py`, `.js`, `.java`, `.go`, `.rb` | Semgrep (SAST) + Secrets |
| `.tf`, `.yaml`, `.yml` | IaC + Secrets |
| `Dockerfile`, `requirements.txt`, `package.json` | Dependency + Secrets |
| All files + `--target-url` | DAST (ZAP) |

## ⚡ Quick Examples

### Example 1: Python Application
```bash
python security_scheduler.py \
  --files "app.py,models.py,views.py" \
  --msg "added user authentication" \
  --use-real-tools \
  --save-json
```

### Example 2: Infrastructure Changes
```bash
python security_scheduler.py \
  --files "main.tf,variables.tf,outputs.tf" \
  --msg "updated AWS security groups"
```

### Example 3: Dependency Update
```bash
python security_scheduler.py \
  --files "requirements.txt,package.json" \
  --msg "updated dependencies to latest versions"
```

### Example 4: Web Application DAST
```bash
# Start your app first: flask run
python security_scheduler.py \
  --files "routes.py,templates/login.html" \
  --msg "authentication improvements" \
  --use-real-tools \
  --target-url "http://localhost:5000"
```

## 🔍 Interpreting Results

### Risk Levels
- **HIGH** (Score ≥ 6): Critical changes requiring immediate security review
- **MEDIUM** (Score 3-5): Standard changes with moderate risk
- **LOW** (Score < 3): Low-risk changes

### Severity Levels
- **CRITICAL**: Immediate action required (e.g., exposed secrets)
- **HIGH**: Serious vulnerabilities (e.g., SQL injection)
- **MEDIUM**: Important issues (e.g., weak crypto)
- **LOW**: Best practice violations

### Exit Codes
- `0`: No security issues found
- `1`: Security issues detected (fails CI/CD)

## 🔧 Troubleshooting

### Semgrep not found
```bash
pip install semgrep
semgrep --version
```

### ZAP connection failed
```bash
# Check ZAP status
zap-cli status

# Start ZAP manually
zap.sh -daemon -config api.disablekey=true
```

### Permission denied
```bash
chmod +x security_scheduler.py
chmod +x setup.sh
```

## 🎨 Output Examples

### Console Output
```
🚀 Starting Adaptive Security Testing Scheduler...
📁 Analyzing 2 changed file(s)
🔧 Mode: Real Security Tools (Semgrep + OWASP ZAP)
📋 Scheduled 2 scan(s): semgrep, secret
────────────────────────────────────────────────
🔍 Running Semgrep SAST Scanner...
  ✅ Semgrep scan completed. Found 3 issues.
🔍 Running Secret Scanner...
  ✅ Secret scan completed. Found 0 potential secrets.

════════════════════════════════════════════════
🛡️  ADAPTIVE SECURITY TESTING REPORT
════════════════════════════════════════════════
...
```

## 📚 Integration Examples

### Pre-commit Hook
```bash
# .git/hooks/pre-commit
#!/bin/bash
python security_scheduler.py \
  --files "$(git diff --cached --name-only | tr '\n' ',')" \
  --msg "$(git log -1 --pretty=%B)" \
  --use-real-tools
```

### GitHub Actions
```yaml
- name: Security Scan
  run: |
    python security_scheduler.py \
      --files "${{ steps.changes.outputs.files }}" \
      --msg "${{ github.event.head_commit.message }}" \
      --use-real-tools \
      --save-json
```

## 💡 Pro Tips

1. **Run tests first**: Use `./run_tests.sh` to verify setup
2. **Start with simulated**: Test with `--no-real-tools` before installing Semgrep
3. **Check reports**: JSON reports in `reports/` directory
4. **CI/CD**: Use exit codes to fail builds on security issues
5. **DAST requires app**: Make sure your app is running before ZAP scans

## 🔗 Resources

- Semgrep: https://semgrep.dev/docs/
- OWASP ZAP: https://www.zaproxy.org/docs/
- Full README: `README.md`

## 📞 Getting Help

1. Check this guide
2. Review README.md
3. Check CHANGELOG.md for known issues
4. Review tool documentation

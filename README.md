# Adaptive Security Testing Scheduler

A comprehensive DevSecOps tool that intelligently schedules and executes security scans based on code changes. Integrates with industry-standard tools like **Semgrep** (SAST) and **OWASP ZAP** (DAST).

## 🌟 Features

- ✅ **Intelligent Scan Scheduling**: Automatically determines which security scans to run based on file types and commit messages
- ✅ **Risk Assessment**: Calculates risk scores to prioritize security testing efforts
- ✅ **Real Tool Integration**: Uses Semgrep for SAST and OWASP ZAP for DAST
- ✅ **Multiple Scanner Support**: Secret detection, dependency scanning, IaC scanning
- ✅ **Detailed Reporting**: Console and JSON reports with comprehensive findings
- ✅ **CI/CD Ready**: Returns proper exit codes for pipeline integration

## 🔧 Supported Scanners

| Scanner | Type | Tool | Purpose |
|---------|------|------|---------|
| Semgrep | SAST | [Semgrep](https://semgrep.dev/) | Static code analysis for security vulnerabilities |
| OWASP ZAP | DAST | [ZAP](https://www.zaproxy.org/) | Dynamic application security testing |
| Secret Scanner | Secrets | Simulated | Detect exposed credentials and API keys |
| Dependency Scanner | SCA | Simulated | Find vulnerabilities in dependencies |
| IaC Scanner | IaC | Simulated | Infrastructure as Code security checks |

## 📦 Installation

### Prerequisites

- Python 3.7+
- pip

### Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Install Semgrep (SAST)

```bash
# Install via pip (recommended)
pip install semgrep

# Or install via Homebrew (macOS)
brew install semgrep

# Verify installation
semgrep --version
```

### Step 3: Install OWASP ZAP (DAST) - Optional

**Option A: Install ZAP CLI Only** (Lightweight)

```bash
pip install zapcli
```

**Option B: Full ZAP Installation** (Recommended for DAST)

1. Download from [OWASP ZAP](https://www.zaproxy.org/download/)
2. Install ZAP
3. Add ZAP to your PATH
4. Install ZAP CLI: `pip install zapcli`

**Option C: Docker** (Easy Setup)

```bash
# Pull ZAP Docker image
docker pull owasp/zap2docker-stable

# ZAP CLI will connect to Docker container
```

## 🚀 Usage

### Basic Usage (Simulated Scanners)

```bash
python security_scheduler.py \
  --files "app.py,config.yaml" \
  --msg "updated authentication logic"
```

### Using Real Tools (Semgrep)

```bash
python security_scheduler.py \
  --files "app.py,utils.py,models.py" \
  --msg "security improvements" \
  --use-real-tools
```

### Full Security Scan (SAST + DAST)

```bash
# Start your application first (e.g., flask run on localhost:5000)

python security_scheduler.py \
  --files "app.py,api.py" \
  --msg "API security updates" \
  --use-real-tools \
  --target-url "http://localhost:5000"
```

### Save Results as JSON

```bash
python security_scheduler.py \
  --files "main.tf,variables.tf" \
  --msg "infrastructure changes" \
  --save-json
```

### Custom Output Path

```bash
python security_scheduler.py \
  --files "Dockerfile,requirements.txt" \
  --msg "dependency updates" \
  --output "reports/custom_report.json"
```

### Scan Remote Git Repositories

```bash
# Scan entire repository (auto-detect files)
python security_scheduler.py \
  --repo-url "https://github.com/user/repo.git" \
  --use-real-tools

# Scan specific files from remote repo
python security_scheduler.py \
  --repo-url "https://github.com/user/repo.git" \
  --files "app.py,utils.py" \
  --msg "security fixes" \
  --use-real-tools
```

**Note:** When using `--repo-url`, the tool will:
- Clone the repository to a temporary directory
- Automatically extract the latest commit message if `--msg` is not provided
- Scan the specified files or auto-detect common file types
- Clean up the temporary clone after scanning

## � Git Integration & CI/CD

The security scheduler can be automatically integrated with Git workflows to scan code changes on every commit or pull request.

### Automatic Git Detection

When running in a Git repository without specifying `--files` or `--msg`, the tool will:
- Automatically detect changed files from the last commit
- Extract the commit message from Git history
- Run appropriate security scans based on the changes

```bash
# In a Git repository - automatically detects changes
python security_scheduler.py --use-real-tools
```

### GitHub Actions Integration

The repository includes a GitHub Actions workflow (`.github/workflows/security-scan.yml`) that automatically runs security scans on:

- **Push events** to main/master/develop branches
- **Pull requests** targeting main/master/develop branches

#### Features:
- ✅ Detects changed files automatically
- ✅ Extracts commit messages from Git history
- ✅ Runs Semgrep SAST scanning
- ✅ Generates detailed reports
- ✅ Uploads reports as artifacts
- ✅ Comments on pull requests with scan results

#### Setup Steps:

1. **Ensure the workflow file exists** (it's already included):
   ```
   .github/workflows/security-scan.yml
   ```

2. **Push to GitHub** and enable Actions in your repository settings

3. **Configure branch protection** (optional):
   - Go to Settings → Branches
   - Add rule for main/master branch
   - Require status checks to pass
   - Include the `security-scan` job

4. **Customize the workflow** (optional):
   - Edit `.github/workflows/security-scan.yml`
   - Modify triggers, branches, or scan parameters
   - Add additional security tools

#### Workflow Behavior:

- **On Push**: Scans files changed in the latest commit
- **On PR**: Scans files changed in the PR compared to base branch
- **Reports**: Saved to `reports/` directory and uploaded as artifacts
- **PR Comments**: Automatic summary posted to pull requests

### Git Hooks (Local Development)

For local development, you can set up Git hooks to run scans before commits:

#### Pre-commit Hook Setup:

1. Create the hooks directory:
   ```bash
   mkdir -p .git/hooks
   ```

2. Create `pre-commit` hook:
   ```bash
   cat > .git/hooks/pre-commit << 'EOF'
   #!/bin/bash
   
   echo "🔒 Running security scan..."
   
   # Get staged files
   STAGED_FILES=$(git diff --cached --name-only | tr '\n' ',')
   
   if [ -n "$STAGED_FILES" ]; then
       # Run security scan
       python security_scheduler.py \
           --files "$STAGED_FILES" \
           --msg "Pre-commit scan" \
           --use-real-tools
       
       # Check exit code
       if [ $? -ne 0 ]; then
           echo "❌ Security scan failed! Fix issues before committing."
           exit 1
       fi
   fi
   
   echo "✅ Security scan passed!"
   EOF
   ```

3. Make the hook executable:
   ```bash
   chmod +x .git/hooks/pre-commit
   ```

### Other CI/CD Platforms

#### GitLab CI/CD:

```yaml
# .gitlab-ci.yml
security_scan:
  stage: test
  script:
    - pip install -r requirements.txt
    - pip install semgrep
    - python security_scheduler.py --use-real-tools
  artifacts:
    reports:
      security_scan: reports/
    paths:
      - reports/
  only:
    - merge_requests
    - main
```

#### Jenkins Pipeline:

```groovy
pipeline {
    agent any
    
    stages {
        stage('Security Scan') {
            steps {
                sh '''
                    pip install -r requirements.txt
                    pip install semgrep
                    python security_scheduler.py --use-real-tools
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'reports/**', fingerprint: true
                }
            }
        }
    }
}
```

## �📋 Command-Line Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--files` | ❌* | Comma-separated list of changed files (required unless `--repo-url` provided) |
| `--msg` | ❌* | Commit message (required unless `--repo-url` provided and can be auto-extracted) |
| `--repo-url` | ❌ | Git repository URL to clone and scan (e.g., `https://github.com/user/repo.git`) |
| `--target-url` | ❌ | Target URL for DAST scanning (e.g., `http://localhost:8000`) |
| `--use-real-tools` | ❌ | Use Semgrep and ZAP (default: True) |
| `--no-real-tools` | ❌ | Use simulated scanners only |
| `--save-json` | ❌ | Save report as JSON file |
| `--output` | ❌ | Custom path for JSON report |

*Required when `--repo-url` is not provided

## 🎯 Scan Triggering Logic

The scheduler intelligently determines which scans to run:

| File Type | Triggered Scans |
|-----------|----------------|
| `.py`, `.js`, `.java`, `.go`, `.rb` | Semgrep (SAST), Secret Scanner |
| `Dockerfile`, `requirements.txt`, `package.json` | Dependency Scanner, Secret Scanner |
| `.tf`, `.yaml`, `.yml` | IaC Scanner, Secret Scanner |
| Any file + `--target-url` | OWASP ZAP (DAST) |

## 📊 Risk Assessment

Risk scores are calculated based on:

- **File types** (e.g., Python: +2, Terraform: +3)
- **Commit message keywords** (e.g., "auth", "security": +3)
- **Change patterns** (e.g., "update", "modify": +1)

Risk levels:
- **LOW**: Score < 3
- **MEDIUM**: Score 3-5
- **HIGH**: Score ≥ 6

## 🔍 Example Workflows

### 1. Pre-Commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

CHANGED_FILES=$(git diff --cached --name-only | tr '\n' ',' | sed 's/,$//')
COMMIT_MSG=$(git log -1 --pretty=%B)

python security_scheduler.py \
  --files "$CHANGED_FILES" \
  --msg "$COMMIT_MSG" \
  --use-real-tools

if [ $? -ne 0 ]; then
    echo "❌ Security scan failed! Please fix issues before committing."
    exit 1
fi
```

### 2. GitHub Actions CI/CD

The repository includes a complete GitHub Actions workflow (`.github/workflows/security-scan.yml`) that automatically runs security scans on every push and pull request.

**Features:**
- ✅ Automatic detection of changed files
- ✅ Intelligent commit message extraction
- ✅ Real tool integration (Semgrep + OWASP ZAP)
- ✅ JSON and text report generation
- ✅ PR comments with scan results
- ✅ Artifact upload for reports

**Setup:**
1. The workflow file is already included in the repository
2. Ensure your repository has the necessary secrets/permissions if using private repos
3. Customize the workflow as needed for your specific requirements

**Workflow Overview:**
```yaml
name: Security Scan
on: [push, pull_request]
jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - Checkout code
      - Setup Python and dependencies
      - Install security tools (Semgrep, ZAP CLI)
      - Detect changed files and commit message
      - Run security scan
      - Upload reports as artifacts
      - Comment on PRs with results
```

### 3. GitLab CI/CD

```yaml
security_scan:
  stage: test
  script:
    - pip install -r requirements.txt
    - |
      CHANGED_FILES=$(git diff --name-only $CI_COMMIT_BEFORE_SHA $CI_COMMIT_SHA | tr '\n' ',' | sed 's/,$//')
      python security_scheduler.py \
        --files "$CHANGED_FILES" \
        --msg "$CI_COMMIT_MESSAGE" \
        --use-real-tools \
        --save-json
  artifacts:
    paths:
      - reports/
    when: always
```

## 📄 Sample Output

### Console Report

```
================================================================================
🛡️  ADAPTIVE SECURITY TESTING REPORT
================================================================================
📝 Commit Message: updated authentication logic
📁 Changed Files: app.py, utils.py
⚠️  Risk Level: HIGH (Score: 7)
🕒 Timestamp: 2025-01-31 14:30:45

📊 SCAN RESULTS:
--------------------------------------------------------------------------------

Semgrep SAST Scanner - COMPLETED
  Severity: HIGH
  Findings: 3
    1. [HIGH] Weak cryptographic hash function used
       File: app.py:42
       Rule: python.lang.security.audit.weak-hash.md5-used
    2. [MEDIUM] SQL injection vulnerability detected
       File: utils.py:28
       Rule: python.django.security.injection.sql.sql-injection-db-cursor-execute
    3. [LOW] Hardcoded secret detected
       File: app.py:15
       Rule: python.lang.security.audit.hardcoded-secret

Secret Scanner - COMPLETED
  Severity: LOW
  Findings: 0

🎯 SUMMARY:
  Total Security Issues Found: 3
  Risk Assessment: HIGH
  ⚠️  Security issues require attention!
================================================================================
```

### JSON Report

```json
{
  "timestamp": "2025-01-31T14:30:45.123456",
  "commit_info": {
    "message": "updated authentication logic",
    "changed_files": ["app.py", "utils.py"]
  },
  "risk_assessment": {
    "score": 7,
    "level": "HIGH"
  },
  "scan_results": [
    {
      "scanner": "Semgrep SAST Scanner",
      "status": "completed",
      "findings_count": 3,
      "findings": [...],
      "severity": "HIGH"
    }
  ],
  "summary": {
    "total_findings": 3,
    "scans_executed": 2,
    "scans_successful": 2,
    "scans_failed": 0
  }
}
```

## 🛠️ Troubleshooting

### Semgrep Not Found

```bash
# Install Semgrep
pip install semgrep

# Verify
semgrep --version
```

### OWASP ZAP Connection Issues

```bash
# Check if ZAP is running
zap-cli status

# Start ZAP daemon manually
zap.sh -daemon -config api.disablekey=true
```

### Permission Errors

```bash
# Make script executable
chmod +x security_scheduler.py

# Run with proper permissions
python security_scheduler.py ...
```

## 📚 Advanced Configuration

### Custom Semgrep Rules

```bash
# Use custom rule configuration
python security_scheduler.py \
  --files "app.py" \
  --msg "updates" \
  --use-real-tools
```

Then modify the `SemgrepScanner.scan()` method to use custom config:

```python
cmd = [
    'semgrep',
    '--config=/path/to/custom/rules.yml',
    '--json',
    '--metrics=off'
] + scannable_files
```

### Timeout Configuration

Modify scanner timeout values in the code:

```python
# In SemgrepScanner.scan()
result = subprocess.run(cmd, timeout=300)  # 5 minutes

# In OWASPZAPScanner.scan()
subprocess.run(['zap-cli', 'active-scan', url], timeout=600)  # 10 minutes
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

MIT License - feel free to use this tool in your projects!

## 🔗 Resources

- [Semgrep Documentation](https://semgrep.dev/docs/)
- [OWASP ZAP Documentation](https://www.zaproxy.org/docs/)
- [DevSecOps Best Practices](https://www.devsecops.org/)

## ⚠️ Important Notes

1. **DAST Scanning**: OWASP ZAP requires a running application. Make sure your app is accessible before running DAST scans.
2. **CI/CD Integration**: The tool returns exit code 1 if security issues are found, making it suitable for pipeline integration.
3. **Performance**: Semgrep is fast, but ZAP DAST scans can take several minutes depending on the application size.
4. **False Positives**: Review all findings carefully. Static analysis tools may report false positives.

## 📧 Support

For issues or questions:
- Check the troubleshooting section
- Review Semgrep and ZAP documentation
- Open an issue on the repository


python security_scheduler.py --files "app.py" --msg "updates" --use-real-tools

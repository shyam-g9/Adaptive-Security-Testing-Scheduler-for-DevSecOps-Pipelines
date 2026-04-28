#!/usr/bin/env python3
"""
Adaptive Security Testing Scheduler for DevSecOps Pipelines
A CLI-based tool that analyzes commits and schedules appropriate security scans.
Includes integration with Semgrep (SAST) and OWASP ZAP (DAST).
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
import shutil
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from pathlib import Path


class SecurityScanner:
    """Base class for all security scanners"""
    
    def __init__(self, name: str):
        self.name = name
    
    def scan(self, files: List[str], commit_msg: str) -> Dict:
        """Override this method in subclasses"""
        raise NotImplementedError
    
    def is_tool_available(self, command: str) -> bool:
        """Check if a command-line tool is available"""
        try:
            subprocess.run(
                [command, '--version'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )
            return True
        except FileNotFoundError:
            return False


class SemgrepScanner(SecurityScanner):
    """Semgrep SAST Scanner - Real integration"""
    
    def __init__(self):
        super().__init__("Semgrep SAST Scanner")
        self.available = self.is_tool_available('semgrep')
    
    def scan(self, files: List[str], commit_msg: str) -> Dict:
        """Run Semgrep SAST scanning"""
        print(f"🔍 Running {self.name}...")
        
        if not self.available:
            print(f"  ⚠️  Semgrep not installed. Run: pip install semgrep")
            return {
                'scanner': self.name,
                'status': 'skipped',
                'findings_count': 0,
                'findings': ['Semgrep not installed'],
                'severity': 'INFO',
                'error': 'Tool not available'
            }
        
        findings = []
        
        # Filter for scannable files
        scannable_files = [f for f in files if f.endswith(('.py', '.js', '.java', '.go', '.rb'))]
        
        if not scannable_files:
            print(f"  ℹ️  No scannable files for Semgrep")
            return {
                'scanner': self.name,
                'status': 'skipped',
                'findings_count': 0,
                'findings': [],
                'severity': 'LOW'
            }
        
        try:
            # Run Semgrep with auto config (uses registry rules)
            cmd = [
                'semgrep',
                '--config=auto',
                '--json'
            ] + scannable_files
            
            # Ensure semgrep subprocess runs with UTF-8 enabled on Windows
            env = os.environ.copy()
            # PYTHONUTF8=1 enables UTF-8 mode for Python (helps when semgrep writes files)
            env.setdefault('PYTHONUTF8', '1')

            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=120,
                check=False,
                env=env
            )
            
            if result.returncode in [0, 1]:  # 0 = no findings, 1 = findings found
                output = json.loads(result.stdout.decode('utf-8'))
                
                for finding in output.get('results', []):
                    findings.append({
                        'file': finding.get('path', 'unknown'),
                        'rule': finding.get('check_id', 'unknown'),
                        'severity': finding.get('extra', {}).get('severity', 'MEDIUM'),
                        'message': finding.get('extra', {}).get('message', 'Security issue detected'),
                        'line': finding.get('start', {}).get('line', 0)
                    })
                
                severity = self._calculate_severity(findings)
                
                print(f"  ✅ Semgrep scan completed. Found {len(findings)} issues.")
                
                return {
                    'scanner': self.name,
                    'status': 'completed',
                    'findings_count': len(findings),
                    'findings': findings,
                    'severity': severity
                }
            else:
                error_msg = result.stderr.decode('utf-8')
                print(f"  ❌ Semgrep scan failed: {error_msg}")
                return {
                    'scanner': self.name,
                    'status': 'failed',
                    'findings_count': 0,
                    'findings': [],
                    'severity': 'ERROR',
                    'error': error_msg
                }
                
        except subprocess.TimeoutExpired:
            print(f"  ⏱️  Semgrep scan timed out")
            return {
                'scanner': self.name,
                'status': 'timeout',
                'findings_count': 0,
                'findings': [],
                'severity': 'ERROR',
                'error': 'Scan timeout'
            }
        except Exception as e:
            print(f"  ❌ Error running Semgrep: {str(e)}")
            return {
                'scanner': self.name,
                'status': 'error',
                'findings_count': 0,
                'findings': [],
                'severity': 'ERROR',
                'error': str(e)
            }
    
    def _calculate_severity(self, findings: List[Dict]) -> str:
        """Calculate overall severity from findings"""
        if not findings:
            return 'LOW'
        
        severities = [f.get('severity', 'MEDIUM').upper() for f in findings]
        
        if 'CRITICAL' in severities or 'HIGH' in severities:
            return 'HIGH'
        elif 'MEDIUM' in severities:
            return 'MEDIUM'
        else:
            return 'LOW'


class OWASPZAPScanner(SecurityScanner):
    """OWASP ZAP DAST Scanner - Real integration"""
    
    def __init__(self, target_url: Optional[str] = None):
        super().__init__("OWASP ZAP DAST Scanner")
        self.target_url = target_url
        self.available = self.is_tool_available('zap-cli')
    
    def scan(self, files: List[str], commit_msg: str) -> Dict:
        """Run OWASP ZAP DAST scanning"""
        print(f"🔍 Running {self.name}...")
        
        if not self.available:
            print(f"  ⚠️  OWASP ZAP CLI not installed. Run: pip install zapcli")
            return {
                'scanner': self.name,
                'status': 'skipped',
                'findings_count': 0,
                'findings': ['OWASP ZAP not installed'],
                'severity': 'INFO',
                'error': 'Tool not available'
            }
        
        if not self.target_url:
            print(f"  ℹ️  No target URL specified for DAST scanning")
            return {
                'scanner': self.name,
                'status': 'skipped',
                'findings_count': 0,
                'findings': ['No target URL provided'],
                'severity': 'INFO'
            }
        
        findings = []
        
        try:
            # Start ZAP daemon
            print(f"  🚀 Starting ZAP daemon...")
            subprocess.run(
                ['zap-cli', 'start', '--start-options', '-config api.disablekey=true'],
                timeout=60,
                check=False
            )
            
            # Wait for ZAP to be ready
            subprocess.run(['zap-cli', 'status', '-t', '120'], check=False)
            
            # Open URL
            print(f"  🌐 Scanning {self.target_url}...")
            subprocess.run(['zap-cli', 'open-url', self.target_url], check=False)
            
            # Spider the target
            print(f"  🕷️  Spidering target...")
            subprocess.run(['zap-cli', 'spider', self.target_url], timeout=120, check=False)
            
            # Active scan
            print(f"  🔬 Running active scan...")
            subprocess.run(['zap-cli', 'active-scan', self.target_url], timeout=300, check=False)
            
            # Get alerts
            result = subprocess.run(
                ['zap-cli', 'alerts', '-f', 'json'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )
            
            if result.returncode == 0:
                alerts = json.loads(result.stdout.decode('utf-8'))
                
                for alert in alerts:
                    findings.append({
                        'risk': alert.get('risk', 'Unknown'),
                        'name': alert.get('name', 'Unknown'),
                        'url': alert.get('url', self.target_url),
                        'description': alert.get('description', 'No description'),
                        'solution': alert.get('solution', 'No solution provided')
                    })
                
                severity = self._calculate_severity(findings)
                
                print(f"  ✅ ZAP scan completed. Found {len(findings)} alerts.")
                
                # Shutdown ZAP
                subprocess.run(['zap-cli', 'shutdown'], check=False)
                
                return {
                    'scanner': self.name,
                    'status': 'completed',
                    'findings_count': len(findings),
                    'findings': findings,
                    'severity': severity,
                    'target': self.target_url
                }
            else:
                error_msg = result.stderr.decode('utf-8')
                print(f"  ❌ ZAP scan failed: {error_msg}")
                subprocess.run(['zap-cli', 'shutdown'], check=False)
                return {
                    'scanner': self.name,
                    'status': 'failed',
                    'findings_count': 0,
                    'findings': [],
                    'severity': 'ERROR',
                    'error': error_msg
                }
                
        except subprocess.TimeoutExpired:
            print(f"  ⏱️  ZAP scan timed out")
            subprocess.run(['zap-cli', 'shutdown'], check=False)
            return {
                'scanner': self.name,
                'status': 'timeout',
                'findings_count': 0,
                'findings': [],
                'severity': 'ERROR',
                'error': 'Scan timeout'
            }
        except Exception as e:
            print(f"  ❌ Error running OWASP ZAP: {str(e)}")
            subprocess.run(['zap-cli', 'shutdown'], check=False)
            return {
                'scanner': self.name,
                'status': 'error',
                'findings_count': 0,
                'findings': [],
                'severity': 'ERROR',
                'error': str(e)
            }
    
    def _calculate_severity(self, findings: List[Dict]) -> str:
        """Calculate overall severity from findings"""
        if not findings:
            return 'LOW'
        
        risks = [f.get('risk', 'Medium').lower() for f in findings]
        
        if 'high' in risks:
            return 'HIGH'
        elif 'medium' in risks:
            return 'MEDIUM'
        else:
            return 'LOW'


class SASTScanner(SecurityScanner):
    """Legacy Static Application Security Testing Scanner (Simulated)"""
    
    def __init__(self):
        super().__init__("SAST Scanner (Simulated)")
    
    def scan(self, files: List[str], commit_msg: str) -> Dict:
        """Simulates SAST scanning for Python files"""
        print(f"🔍 Running {self.name}...")
        
        # Simulate findings based on file content patterns
        findings = []
        for file in files:
            if file.endswith('.py'):
                # Simulate some security issues
                if 'auth' in commit_msg.lower():
                    findings.append(f"Potential authentication bypass in {file}")
                if 'config' in commit_msg.lower():
                    findings.append(f"Hardcoded configuration detected in {file}")
        
        result = {
            'scanner': self.name,
            'status': 'completed',
            'findings_count': len(findings),
            'findings': findings,
            'severity': 'HIGH' if findings else 'LOW'
        }
        
        print(f"  ✅ SAST scan completed. Found {len(findings)} issues.")
        return result


class SecretScanner(SecurityScanner):
    """Secret Detection Scanner - Real secret pattern detection"""
    
    def __init__(self):
        super().__init__("Secret Scanner")
        self.patterns = {
            'aws_access_key': r'AKIA[0-9A-Z]{16}',
            'aws_secret_key': r'aws_secret_access_key\s*=\s*["\']?[A-Za-z0-9/+=]{40}["\']?',
            'private_key': r'-----BEGIN (RSA|EC|OPENSSH|PGP) PRIVATE KEY',
            'api_key': r'api[_-]?key["\']?\s*[:=]\s*["\']?[A-Za-z0-9\-_]{20,}["\']?',
            'password': r'password["\']?\s*[:=]\s*["\']([^"\']{8,})["\']',
            'database_url': r'(mysql|postgres|mongodb|redis)://[^\s]+:[^\s]+@[^\s]+',
            'github_token': r'gh[pousr]{1}_[A-Za-z0-9_]{36,255}',
            'slack_token': r'xox[baprs]-[0-9]{10,13}-[0-9]{10,13}-[A-Za-z0-9]{24,32}',
            'jwt_token': r'eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+',
            'generic_secret': r'["\']?(secret|token|api_key|password)["\']?\s*[:=]\s*["\']([A-Za-z0-9\-_=+/]{16,})["\']'
        }
    
    def scan(self, files: List[str], commit_msg: str) -> Dict:
        """Scan files for actual secrets"""
        import re
        
        print(f"🔍 Running {self.name}...")
        
        findings = []
        
        for file_path in files:
            # Skip binary and non-source files
            if file_path.endswith(('.pyc', '.o', '.so', '.exe', '.dll', '.bin', '.zip', '.tar', '.gz')):
                continue
            
            try:
                # Try to read the file
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                except FileNotFoundError:
                    continue
                
                # Scan each line for secrets
                for line_num, line in enumerate(lines, 1):
                    # Skip comments and empty lines
                    stripped = line.strip()
                    if not stripped or stripped.startswith('#'):
                        continue
                    
                    # Check against each secret pattern
                    for secret_type, pattern in self.patterns.items():
                        if re.search(pattern, line, re.IGNORECASE):
                            # Don't expose the actual secret in findings
                            masked_line = re.sub(pattern, '[REDACTED]', line, flags=re.IGNORECASE).strip()
                            
                            findings.append({
                                'file': file_path,
                                'line': line_num,
                                'type': secret_type.replace('_', ' ').title(),
                                'message': f'{secret_type.replace("_", " ").title()} detected',
                                'severity': 'CRITICAL',
                                'context': masked_line[:100]  # Truncate for safety
                            })
            
            except Exception as e:
                # Skip files we can't read
                pass
        
        result = {
            'scanner': self.name,
            'status': 'completed',
            'findings_count': len(findings),
            'findings': findings,
            'severity': 'CRITICAL' if findings else 'LOW'
        }
        
        print(f"  ✅ Secret scan completed. Found {len(findings)} potential secrets.")
        return result


class DependencyScanner(SecurityScanner):
    """Dependency Vulnerability Scanner"""
    
    def __init__(self):
        super().__init__("Dependency Scanner")
    
    def scan(self, files: List[str], commit_msg: str) -> Dict:
        """Simulates dependency vulnerability scanning"""
        print(f"🔍 Running {self.name}...")
        
        # Check for dependency files
        dep_files = [f for f in files if f in ['Dockerfile', 'requirements.txt', 'package.json', 'dependencies.txt']]
        
        findings = []
        if dep_files:
            # Simulate vulnerability findings
            findings = [
                f"Outdated dependency with known CVE in {dep_files[0]}",
                "High severity vulnerability in transitive dependency"
            ]
        
        result = {
            'scanner': self.name,
            'status': 'completed',
            'findings_count': len(findings),
            'findings': findings,
            'severity': 'MEDIUM' if findings else 'LOW'
        }
        
        print(f"  ✅ Dependency scan completed. Found {len(findings)} vulnerabilities.")
        return result


class IaCScanner(SecurityScanner):
    """Infrastructure as Code Scanner"""
    
    def __init__(self):
        super().__init__("IaC Scanner")
    
    def scan(self, files: List[str], commit_msg: str) -> Dict:
        """Simulates Infrastructure as Code security scanning"""
        print(f"🔍 Running {self.name}...")
        
        # Check for IaC files
        iac_files = [f for f in files if f.endswith(('.tf', '.yaml', '.yml', '.json'))]
        
        findings = []
        if iac_files:
            findings = [
                f"Insecure configuration detected in {iac_files[0]}",
                "Missing encryption configuration",
                "Overly permissive access policy"
            ]
        
        result = {
            'scanner': self.name,
            'status': 'completed',
            'findings_count': len(findings),
            'findings': findings,
            'severity': 'HIGH' if len(findings) > 2 else 'MEDIUM' if findings else 'LOW'
        }
        
        print(f"  ✅ IaC scan completed. Found {len(findings)} configuration issues.")
        return result


class RiskAnalyzer:
    """Analyzes commit risk based on files and commit message"""
    
    @staticmethod
    def calculate_risk_score(files: List[str], commit_msg: str) -> Tuple[int, str]:
        """Calculate risk score and classification"""
        score = 0
        
        # File-based risk scoring
        for file in files:
            if file.endswith('.py'):
                score += 2
            elif file.endswith(('.tf', '.yaml', '.yml')):
                score += 3
            elif file in ['Dockerfile', 'requirements.txt', 'package.json']:
                score += 2
            elif file.endswith(('.sh', '.ps1')):
                score += 1
        
        # Commit message-based risk scoring
        high_risk_keywords = ['auth', 'config', 'critical', 'security', 'admin', 'root']
        for keyword in high_risk_keywords:
            if keyword in commit_msg.lower():
                score += 3
                break
        
        medium_risk_keywords = ['update', 'change', 'modify', 'fix']
        for keyword in medium_risk_keywords:
            if keyword in commit_msg.lower():
                score += 1
                break
        
        # Classify risk
        if score >= 6:
            return score, "HIGH"
        elif score >= 3:
            return score, "MEDIUM"
        else:
            return score, "LOW"


class ScanScheduler:
    """Decides which scans to run based on changed files and commit message"""
    
    def __init__(self, target_url: Optional[str] = None, use_real_tools: bool = True):
        """
        Initialize scheduler with optional target URL for DAST
        
        Args:
            target_url: URL for DAST scanning with OWASP ZAP
            use_real_tools: If True, use Semgrep and ZAP; if False, use simulated scanners
        """
        self.target_url = target_url
        self.use_real_tools = use_real_tools
        
        if use_real_tools:
            self.scanners = {
                'semgrep': SemgrepScanner(),
                'zap': OWASPZAPScanner(target_url),
                'secret': SecretScanner(),
                'dependency': DependencyScanner(),
                'iac': IaCScanner()
            }
        else:
            self.scanners = {
                'sast': SASTScanner(),
                'secret': SecretScanner(),
                'dependency': DependencyScanner(),
                'iac': IaCScanner()
            }
    
    def determine_required_scans(self, files: List[str], commit_msg: str) -> List[str]:
        """Determine which scans should run based on the rules"""
        required_scans = []
        
        # Always run secret scan
        required_scans.append('secret')
        
        if self.use_real_tools:
            # Check for Semgrep-compatible files
            if any(f.endswith(('.py', '.js', '.java', '.go', '.rb')) for f in files):
                required_scans.append('semgrep')
            
            # Run DAST if target URL is provided
            if self.target_url:
                required_scans.append('zap')
        else:
            # Check for Python files (legacy SAST)
            if any(f.endswith('.py') for f in files):
                required_scans.append('sast')
        
        # Check for dependency files
        dependency_files = ['Dockerfile', 'requirements.txt', 'package.json', 'dependencies.txt']
        if any(f in dependency_files for f in files):
            required_scans.append('dependency')
        
        # Check for IaC files
        if any(f.endswith(('.tf', '.yaml', '.yml')) for f in files):
            required_scans.append('iac')
        
        return required_scans
    
    def run_scans(self, scan_types: List[str], files: List[str], commit_msg: str) -> List[Dict]:
        """Execute the required scans"""
        results = []
        
        for scan_type in scan_types:
            if scan_type in self.scanners:
                result = self.scanners[scan_type].scan(files, commit_msg)
                results.append(result)
        
        return results


class ReportGenerator:
    """Generates and saves security scan reports"""
    
    @staticmethod
    def generate_text_report(files: List[str], commit_msg: str, risk_score: int, 
                            risk_level: str, scan_results: List[Dict]) -> str:
        """Generate a formatted report as string"""
        report = []
        
        report.append("\n" + "="*80)
        report.append("ADAPTIVE SECURITY TESTING REPORT")
        report.append("="*80)
        
        report.append(f"\nCommit Message: {commit_msg}")
        report.append(f"Changed Files: {', '.join(files)}")
        report.append(f"Risk Level: {risk_level} (Score: {risk_score})")
        report.append(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        report.append("\n\nSCAN RESULTS:")
        report.append("-" * 80)
        
        total_findings = 0
        for result in scan_results:
            total_findings += result['findings_count']
            report.append(f"\n{result['scanner']} - {result['status'].upper()}")
            report.append(f"  Severity: {result['severity']}")
            report.append(f"  Findings: {result['findings_count']}")
            
            if result.get('error'):
                report.append(f"  Error: {result['error']}")
            
            if result['findings']:
                # Handle different finding formats
                for i, finding in enumerate(result['findings'], 1):
                    if isinstance(finding, dict):
                        # Structured finding (from Semgrep or ZAP)
                        if 'rule' in finding:  # Semgrep format
                            report.append(f"    {i}. [{finding.get('severity', 'MEDIUM')}] {finding.get('message', 'N/A')}")
                            report.append(f"       File: {finding.get('file', 'N/A')}:{finding.get('line', 'N/A')}")
                            report.append(f"       Rule: {finding.get('rule', 'N/A')}")
                        elif 'type' in finding:  # Secret Scanner format
                            report.append(f"    {i}. [{finding.get('severity', 'CRITICAL')}] {finding.get('type', 'N/A')}")
                            report.append(f"       File: {finding.get('file', 'N/A')}:{finding.get('line', 'N/A')}")
                            report.append(f"       Context: {finding.get('context', 'N/A')}")
                        elif 'risk' in finding:  # ZAP format
                            report.append(f"    {i}. [{finding.get('risk', 'Unknown')}] {finding.get('name', 'N/A')}")
                            report.append(f"       URL: {finding.get('url', 'N/A')}")
                    else:
                        # Simple string finding
                        report.append(f"    {i}. {finding}")
        
        report.append(f"\n\nSUMMARY:")
        report.append(f"  Total Security Issues Found: {total_findings}")
        report.append(f"  Risk Assessment: {risk_level}")
        
        if total_findings == 0:
            report.append("  No security issues detected!")
        else:
            report.append("  Security issues require attention!")
        
        report.append("\n" + "="*80)
        
        return "\n".join(report)
    
    @staticmethod
    def save_text_report(files: List[str], commit_msg: str, risk_score: int,
                        risk_level: str, scan_results: List[Dict]) -> str:
        """Save report as text file with filename based on scanned files"""
        # Create reports directory if it doesn't exist
        if not os.path.exists('reports'):
            os.makedirs('reports')
        
        # Generate filename based on the first file or combined names
        if len(files) == 1:
            base_name = os.path.splitext(os.path.basename(files[0]))[0]
        else:
            # For multiple files, use first file name or a combined name
            base_name = os.path.splitext(os.path.basename(files[0]))[0]
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"reports/{base_name}_report_{timestamp}.txt"
        
        # Generate the report content
        report_content = ReportGenerator.generate_text_report(
            files, commit_msg, risk_score, risk_level, scan_results
        )
        
        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return output_file
    
    @staticmethod
    def save_json_report(files: List[str], commit_msg: str, risk_score: int,
                        risk_level: str, scan_results: List[Dict], output_file: str = None) -> str:
        """Save report as JSON file"""
        if not os.path.exists('reports'):
            os.makedirs('reports')
        
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"reports/security_report_{timestamp}.json"
        
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'commit_info': {
                'message': commit_msg,
                'changed_files': files
            },
            'risk_assessment': {
                'score': risk_score,
                'level': risk_level
            },
            'scan_results': scan_results,
            'summary': {
                'total_findings': sum(r['findings_count'] for r in scan_results),
                'scans_executed': len(scan_results),
                'scans_successful': len([r for r in scan_results if r['status'] == 'completed']),
                'scans_failed': len([r for r in scan_results if r['status'] in ['failed', 'error']])
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        return output_file


def get_changed_files_from_git(commit_sha: str = None) -> List[str]:
    """Get list of changed files from Git"""
    try:
        if commit_sha:
            # Compare with specific commit
            result = subprocess.run(
                ['git', 'diff', '--name-only', f'{commit_sha}~1', commit_sha],
                capture_output=True, text=True, check=True
            )
        else:
            # Compare with HEAD~1
            result = subprocess.run(
                ['git', 'diff', '--name-only', 'HEAD~1'],
                capture_output=True, text=True, check=True
            )
        
        files = [f.strip() for f in result.stdout.split('\n') if f.strip()]
        return files
    except subprocess.CalledProcessError:
        return []


def get_commit_message_from_git(commit_sha: str = None) -> str:
    """Get commit message from Git"""
    try:
        if commit_sha:
            result = subprocess.run(
                ['git', 'log', '-1', '--pretty=%B', commit_sha],
                capture_output=True, text=True, check=True
            )
        else:
            result = subprocess.run(
                ['git', 'log', '-1', '--pretty=%B'],
                capture_output=True, text=True, check=True
            )
        
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "Automated security scan"


def is_git_repository() -> bool:
    """Check if current directory is a Git repository"""
    try:
        subprocess.run(
            ['git', 'rev-parse', '--git-dir'],
            capture_output=True, check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Adaptive Security Testing Scheduler for DevSecOps Pipelines',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with simulated scanners
  python security_scheduler.py --files "app.py,config.yaml" --msg "updated auth logic"

  # Use real tools (Semgrep + OWASP ZAP)
  python security_scheduler.py --files "app.py,main.py" --msg "auth changes" --use-real-tools

  # Include DAST scanning with target URL
  python security_scheduler.py --files "api.py" --msg "API updates" --use-real-tools --target-url "http://localhost:8000"

  # Scan a Git repository
  python security_scheduler.py --repo-url "https://github.com/user/repo.git" --use-real-tools

  # Scan specific files from a Git repo
  python security_scheduler.py --repo-url "https://github.com/user/repo.git" --files "app.py,utils.py" --msg "security fixes"

  # Save JSON report
  python security_scheduler.py --files "Dockerfile,requirements.txt" --msg "dependency updates" --save-json

  # Use legacy simulated scanners
  python security_scheduler.py --files "main.tf" --msg "infrastructure changes" --no-real-tools
        """
    )

    parser.add_argument(
        '--files',
        help='Comma-separated list of changed files (e.g., "app.py,config.yaml"). If --repo-url is provided, these are relative to the repo root.'
    )

    parser.add_argument(
        '--msg',
        help='Commit message. If not provided and --repo-url is given, will use the latest commit message from the repo.'
    )

    parser.add_argument(
        '--repo-url',
        help='Git repository URL to clone and scan (e.g., "https://github.com/user/repo.git")'
    )

    parser.add_argument(
        '--target-url',
        help='Target URL for DAST scanning with OWASP ZAP (e.g., "http://localhost:8000")'
    )

    parser.add_argument(
        '--use-real-tools',
        action='store_true',
        default=True,
        help='Use real tools (Semgrep, OWASP ZAP) instead of simulated scanners (default: True)'
    )

    parser.add_argument(
        '--no-real-tools',
        action='store_true',
        help='Use simulated scanners instead of real tools'
    )

    parser.add_argument(
        '--save-json',
        action='store_true',
        help='Save report as JSON file in reports/ directory'
    )

    parser.add_argument(
        '--output',
        help='Custom output file path for JSON report'
    )

    args = parser.parse_args()

    # Handle tool selection
    use_real_tools = not args.no_real_tools

    # Handle repository cloning
    temp_dir = None
    original_cwd = os.getcwd()

    if args.repo_url:
        print(f"📥 Cloning repository: {args.repo_url}")
        temp_dir = tempfile.mkdtemp()
        try:
            subprocess.run(['git', 'clone', args.repo_url, temp_dir], check=True, capture_output=True)
            os.chdir(temp_dir)
            print(f"✅ Repository cloned to: {temp_dir}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to clone repository: {e}")
            sys.exit(1)

        # Get commit message from latest commit if not provided
        if not args.msg:
            try:
                result = subprocess.run(['git', 'log', '-1', '--pretty=%B'], 
                                      capture_output=True, text=True, check=True)
                args.msg = result.stdout.strip()
                print(f"📝 Using commit message from repo: {args.msg[:50]}...")
            except subprocess.CalledProcessError:
                args.msg = "Repository scan"
                print("⚠️  Could not get commit message, using default")

    # Auto-detect files and message from Git if not provided
    files = []
    if not args.files and not args.repo_url and is_git_repository():
        print("🔍 Detecting changed files from Git...")
        files = get_changed_files_from_git()
        if files:
            print(f"📁 Found {len(files)} changed files: {', '.join(files[:5])}{'...' if len(files) > 5 else ''}")
        else:
            print("⚠️  No changed files detected, scanning common file types...")
            for root, dirs, filenames in os.walk('.'):
                for filename in filenames:
                    if filename.endswith(('.py', '.js', '.java', '.go', '.rb', '.tf', '.yaml', '.yml', '.json')):
                        files.append(os.path.join(root, filename))
            print(f"📁 Auto-detected {len(files)} files to scan")

    if not args.msg and not args.repo_url and is_git_repository():
        args.msg = get_commit_message_from_git()
        print(f"📝 Using commit message from Git: {args.msg[:50]}...")

    # Validate required arguments
    if not args.files and not args.repo_url and not is_git_repository():
        parser.error("--files is required unless --repo-url is provided or running in a Git repository")
    if not args.msg and not args.repo_url and not is_git_repository():
        parser.error("--msg is required unless --repo-url is provided or running in a Git repository")

    # Parse input files if provided
    if args.files:
        files = [f.strip() for f in args.files.split(',') if f.strip()]
    elif not files:  # If files not set by Git detection or repo clone
        files = []
        for root, dirs, filenames in os.walk('.'):
            for filename in filenames:
                if filename.endswith(('.py', '.js', '.java', '.go', '.rb', '.tf', '.yaml', '.yml', '.json')):
                    files.append(os.path.join(root, filename))
        print(f"📁 Auto-detected {len(files)} files to scan")

    commit_msg = args.msg or "Automated security scan"

    print("🚀 Starting Adaptive Security Testing Scheduler...")
    print(f"📁 Analyzing {len(files)} changed file(s)")

    if use_real_tools:
        print("🔧 Mode: Real Security Tools (Semgrep + OWASP ZAP)")
    else:
        print("🔧 Mode: Simulated Scanners")

    # Step 1: Risk Analysis
    risk_analyzer = RiskAnalyzer()
    risk_score, risk_level = risk_analyzer.calculate_risk_score(files, commit_msg)

    # Step 2: Determine Required Scans
    scheduler = ScanScheduler(target_url=args.target_url, use_real_tools=use_real_tools)
    required_scans = scheduler.determine_required_scans(files, commit_msg)

    print(f"📋 Scheduled {len(required_scans)} scan(s): {', '.join(required_scans)}")
    print("-" * 80)

    # Step 3: Execute Scans
    scan_results = scheduler.run_scans(required_scans, files, commit_msg)

    # Step 4: Generate Reports
    report_generator = ReportGenerator()

    # Text report (default - always save)
    text_file = report_generator.save_text_report(
        files, commit_msg, risk_score, risk_level, scan_results
    )
    print(f"\n💾 Report saved: {text_file}")

    # JSON report (if requested)
    if args.save_json or args.output:
        json_file = report_generator.save_json_report(
            files, commit_msg, risk_score, risk_level, scan_results, args.output
        )
        print(f"💾 JSON report saved: {json_file}")

    # Return exit code based on findings
    total_findings = sum(r['findings_count'] for r in scan_results)

    # Cleanup temp directory
    if temp_dir:
        os.chdir(original_cwd)
        shutil.rmtree(temp_dir)
        print(f"🧹 Cleaned up temporary directory: {temp_dir}")

    if total_findings > 0:
        sys.exit(1)  # Exit with error if findings detected
    else:
        sys.exit(0)  # Success


if __name__ == '__main__':
    main()

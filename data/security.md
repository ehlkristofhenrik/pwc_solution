**Fictive Inc. Security Guidelines**

**Access Control & Authentication**

* **Identity Management:** Multi-Factor Authentication (MFA) is mandatory across all internal tools, repositories, and third-party SaaS applications.
* **Password Policy:** Passwords must be generated via the company-provided password manager, contain at least 16 characters, and never be reused across services.
* **Principle of Least Privilege (PoLP):** Access to systems, databases, and repositories is granted strictly based on role requirements. Access rights are automatically revoked upon offboarding or role transition.

---

**Data Protection & Privacy**

| Data Classification | Handling & Storage | Transfer Protocols |
| --- | --- | --- |
| **Public** (Marketing, Docs) | No encryption required; public hosting allowed. | Standard HTTPS |
| **Internal** (SOPs, Roadmaps) | Require SSO authentication; store in company cloud drive. | TLS 1.3 |
| **Confidential / PII** (User data, HR records) | Enforce Encryption at Rest (AES-256); strictly prohibited on local devices. | TLS 1.3 / End-to-End Encrypted |

---

**Infrastructure & Secrets Management**

* **Zero Hardcoded Secrets:** Credentials, API keys, database URLs, and private keys must never exist in source code or version control. Store secrets in designated vaults (e.g., HashiCorp Vault, AWS Secrets Manager) and inject them via environment variables at runtime.
* **Network Security:** Production environments must sit behind a Web Application Firewall (WAF) and remain inaccessible to the public internet except through reverse proxies or API gateways. Production access requires connecting via the company VPN.
* **Dependency Management:** All software dependencies must pass automated vulnerability scans (Snyk/Dependabot) before merging. Vulnerabilities rated *High* or *Critical* must be patched within 48 hours.

---

**Incident Response & Reporting**

* **Immediate Escalation:** Report any suspected security breach, lost device, unapproved access, or phishing attempt immediately to `#security-alerts` or via security@fictive.com.
* **No Retaliation:** Security issues reported in good faith will not result in disciplinary action, even if caused by user error.
* **Device Security:** All work hardware must run company-managed Endpoint Detection & Response (EDR) software, maintain full-disk encryption (FileVault/BitLocker), and auto-lock after 3 minutes of inactivity.

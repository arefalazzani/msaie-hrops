# VND-HR-008 — Information Security, Data Protection and AI Acceptable Use Policy

| Field | Value |
|---|---|
| Document ID | VND-HR-008 |
| Document type | Policy |
| Version | 2.1 |
| Effective date | 1 January 2026 |
| Next review | 1 January 2027 |
| Owner | Head of People & Culture |
| Approver | CEO |
| Classification | Internal |
| Applies to | All Vendelligent Technologies LLC employees, contractors, interns and third parties who access Company systems or data |

## 1. Purpose

Vendelligent Technologies LLC ("Vendelligent", "the Company") operates Smart Machines in retail locations and an AI-driven marketplace that handles consumer interaction data, payment data and the pricing of brand partners. This policy protects that data, defines how employees may use Company systems and AI tools, and sets the rules for reporting incidents. It supports the values **Respect by default** and **Move fast, with care**.

## 2. Scope

This policy applies to all information in any form held or processed by the Company, to all systems (Google Workspace, Slack, GitHub, VendHub, PeopleDesk, VendPay, SecureVend and Smart Machine back-ends), to all devices used for Company work, and to all locations including Riyadh HQ, the Dubai office, the Remote Engineering Hub and retail sites.

## 3. Definitions

- **Personal data / PII**: information that identifies or can identify an individual, such as face or voice recordings, purchase history and contact details.
- **Pseudonymisation**: replacing direct identifiers with a code so a person cannot be identified without separate additional information.
- **Approved AI tool**: a Company-licensed enterprise AI account listed in SecureVend.
- **Data-protection assessment**: a documented review by Legal & Compliance and IT Security approving a tool for Restricted data.
- **MFA**: multi-factor authentication required by Okta SSO.
- **Security incident**: an actual or suspected breach, loss of data or device, unauthorised access or malware infection.

## 4. Data Classification

| Class | Meaning | Examples |
|---|---|---|
| Public | Approved for release to anyone | Marketing material, published website content, job adverts |
| Internal | For employees only; low impact if disclosed | Policies in VendHub, internal Slack discussions, org charts, meeting notes |
| Confidential | Sensitive business information | Roadmaps, financial forecasts, contracts, aggregated and anonymised machine analytics, non-public source code |
| Restricted | Highest sensitivity; severe harm if disclosed | Smart Machine consumer interaction logs (face and voice interaction logs, purchase history), payment data, brand-partner pricing, model weights and training data, employee records |

Unlabelled data should be treated as Internal until classified. If in doubt, treat data as the higher class and ask Legal & Compliance.

## 5. Handling Rules by Class

| Rule | Public | Internal | Confidential | Restricted |
|---|---|---|---|---|
| Storage | Anywhere | Company Google Workspace | Company Google Workspace with restricted sharing | Approved Company systems only, encrypted |
| Personal email or personal cloud | Permitted | Not permitted | Not permitted | Never permitted |
| Sharing outside the Company | Permitted | Only with business need | NDA and manager approval | Only with Legal & Compliance approval |
| Printing | Permitted | Permitted | Avoid; secure disposal | Not permitted |
| AI tools | Any | Approved tools only | Approved tools only | Only tools approved per data-protection assessment |
| Access | All | All employees | Need-to-know | Named individuals, need-to-know |

## 6. Consumer Data Lifecycle

- **Collection**: Smart Machines display clear consent signage at every machine explaining what is captured, and consumers can decline interaction with cameras and microphones where the machine offers an alternative.
- **Pseudonymisation**: consumer data captured by Smart Machines must be pseudonymised within **24 hours** of capture.
- **Retention**: raw interaction audio and video is retained for a maximum of **30 days**, after which it is deleted automatically. Employees must not extend or copy raw recordings.
- **Access**: access to consumer data is restricted to employees with a documented need-to-know. Access is granted through SecureVend with the data owner's approval.
- **Use**: consumer data may be used only for the purposes stated in the consent notice, such as personalising product discovery and improving the service.
- **Deletion requests**: consumer requests for access or deletion are sent to Legal & Compliance immediately and handled within the applicable legal timeframe.

## 7. Employee Data Privacy

- Employee records (contracts, salary, medical certificates, performance and disciplinary records) are Restricted and held in VendHub and PeopleDesk.
- Access to employee records is limited to People & Culture, Finance for payroll and the employee's line management where relevant.
- Employees may view their own records in VendHub and request corrections through PeopleDesk.
- Sensitive HR cases such as harassment and discrimination are auto-restricted in PeopleDesk.
- Employees must not disclose another person's personal data without a business need.

## 8. Access Control

- All systems require **Okta SSO with MFA**. Passwords and MFA codes must never be shared.
- Access follows the **least privilege** principle: employees receive only the access needed for their role.
- Access requests go through SecureVend and require line manager approval, and the data owner's approval for Restricted data.
- **Quarterly access reviews** are performed by system owners and managers; unneeded access is removed within 5 working days.
- Access is removed at the end of the last day of employment, and updated on role changes.

## 9. Devices and Networks

- Work must be done on Company-managed devices (see VND-HR-007). No consumer data on personal devices.
- **Screen lock** must activate after no more than **5 minutes** of inactivity.
- Disk **encryption** must be enabled. Updates must be installed within **7 days**.
- Use the Company **VPN** for internal systems when outside the office. **Public Wi-Fi** may be used only with VPN active.
- Smart Machine production data must not be accessed from restricted locations (see VND-HR-005).
- Removable storage devices are not permitted for Confidential or Restricted data.

## 10. Email and Phishing

- Be suspicious of unexpected links, attachments, urgent payment requests and requests for credentials.
- Report suspicious emails using the report-phishing button in Google Workspace or to SecureVend.
- Never forward Confidential or Restricted data to personal email.
- Verify any request to change bank details or make an urgent payment by calling a known number.
- If an employee clicks a suspicious link or enters credentials, they must report it as an incident within 1 hour.

## 11. Clean Desk and Visitors

- Clear desks and lock screens before leaving. Confidential papers must be locked away or securely shredded.
- Visitors must sign in, wear a **visitor badge** and be accompanied at all times.
- Employees must not allow **tailgating**: each person must badge in themselves, and unknown persons without badges should be challenged politely and reported.
- Whiteboards containing Confidential information must be erased after meetings.

## 12. AI Tools Acceptable Use

### 12.1 Approved tools

Only Company-licensed enterprise AI accounts listed in SecureVend ("approved AI tools") may be used for Company work. The list is maintained by IT Security and reviewed quarterly. Free or personal accounts on public AI tools are not approved.

### 12.2 Which data may go into which tool

| Data class | Approved AI tool | Unapproved or public AI tool |
|---|---|---|
| Public | Permitted | Permitted |
| Internal | Permitted | Not permitted |
| Confidential | Permitted | Not permitted |
| Restricted | Only if the tool is approved per a data-protection assessment | Never permitted |

### 12.3 Prohibited inputs

Employees must **never paste** into any unapproved tool: consumer PII, the source code of core models, brand-partner contracts or pricing, payment data, credentials or employee records.

### 12.4 Responsible use of outputs

- Employees remain accountable for work produced with AI. Outputs must be reviewed for accuracy, bias, confidentiality and intellectual property before use.
- Do not present AI output as verified fact without checking it.
- Where AI-generated content is shown to customers or consumers and disclosure is required by law or contract, it must be disclosed as AI-generated. Smart Machine assistants must make clear to consumers that they are AI.
- New AI tools or use cases must be requested through SecureVend and may require a data-protection assessment.

## 13. The Internal AI HR Assistant

The Company's AI HR Assistant is a Tier-0 channel for policy questions. Its data rules are:

- It reads only the HR **policy corpus** and the asking employee's **own mock employee records**; it cannot read other employees' records.
- It **cannot change records**, approve leave or expenses, or close cases. It may prepare draft tickets and emails for the employee to review.
- Sensitive matters (harassment, discrimination, medical details, legal threats) are routed to a human through a P1 or P2 PeopleDesk ticket.
- Employees should not enter Restricted data about colleagues into the Assistant; conversations are logged for quality and security.

## 14. Incident Reporting

A suspected breach, lost or stolen device, compromised account or phishing click must be reported **within 1 hour of discovery** by:

1. raising a ticket in the SecureVend **`security`** queue; and
2. posting in the Slack channel **#security-incidents**.

Employees must not attempt to investigate on their own or delete evidence. Lost devices must also be reported under VND-HR-007 within 24 hours, with a police report for theft.

### 14.1 Incident severity

| Severity | Description | Example | Response target |
|---|---|---|---|
| Critical | Confirmed exposure of Restricted data or system compromise | Leak of consumer interaction logs or payment data | Immediate response; CEO, CTO and Legal & Compliance informed |
| High | Likely exposure of Confidential data or loss of a device holding data | Stolen laptop | Response within 1 hour |
| Medium | Policy breach with limited exposure | Internal data sent to the wrong colleague | Response within 1 working day |
| Low | Near miss or suspicious activity with no exposure | Reported phishing email, nothing clicked | Response within 2 working days |

Legal & Compliance decides on notifications to regulators and affected persons.

## 15. Mandatory Training

- All employees must complete annual security awareness training by **31 March**.
- New joiners complete Security Awareness, Code of Conduct and Data Protection on day 1 (Field Operations add Site Safety).
- Employees who have not completed the training by 31 March have their **access suspended** until completion is confirmed.

## 16. Third Parties and Vendors

- Third parties may access Company data only under a signed contract with confidentiality and data-protection terms, approved by Legal & Compliance.
- Vendor access is limited, time-bound and logged; vendor accounts are removed when the work ends.
- Brand partners' data may be shared only as agreed in the partner contract.

## 17. Consequences of Breach

Breaches may lead to access suspension, retraining and disciplinary action under VND-HR-011 Disciplinary Policy and Procedure. Unauthorised data disclosure is **zero-tolerance** conduct and may result in dismissal for gross misconduct, and may also lead to legal action. Good-faith reporting of incidents or concerns is protected; reports can also be made anonymously through SpeakUp.

## 18. Frequently Asked Questions

**Q1. Can I paste a customer complaint into a public AI chatbot to summarise it?** No, if it contains consumer personal data. Use an approved AI tool for Internal and Confidential data, and never put consumer PII into an unapproved tool.

**Q2. How long is raw machine audio kept?** A maximum of 30 days. Data is pseudonymised within 24 hours of capture.

**Q3. I lost my phone on a flight. What do I do?** Report it within 1 hour to the SecureVend security queue and #security-incidents, then within 24 hours as lost equipment.

**Q4. What happens if I miss the annual training?** If it is not completed by 31 March, your access will be suspended until you complete it.

**Q5. Can the AI HR Assistant see my colleague's leave balance?** No. It reads only the policy corpus and your own records, and it cannot change records.

**Q6. May I use public Wi-Fi at a café?** Only with the Company VPN on, and never for consumer data on a personal device.

## 19. Roles and Responsibilities

- **All employees**: follow this policy, complete training, report incidents within 1 hour.
- **Line managers**: ensure team access is appropriate and reviewed quarterly.
- **IT Security / SecureVend team**: maintain controls, the approved AI tool list and incident response.
- **Legal & Compliance**: run data-protection assessments, handle regulatory matters and consumer requests.
- **People & Culture**: protect employee records and coordinate training and consequences.
- **CTO**: accountable for the technical security of Smart Machines and platforms.

## 20. Exceptions and Escalation

Exceptions require written approval from the CTO and Legal & Compliance and are time-limited and recorded in SecureVend. Questions are raised in SecureVend (security) or PeopleDesk (Policy Question). Escalations go to the Head of People & Culture and, for serious incidents, the CEO.

## 21. Related Documents

- VND-HR-001 Code of Conduct and Workplace Behaviour
- VND-HR-005 Remote, Hybrid and Work-from-Anywhere Policy
- VND-HR-007 Equipment, IT Assets and Home Office Policy
- VND-HR-011 Disciplinary Policy and Procedure
- VND-SOP-101 Employee Onboarding SOP
- VND-SOP-102 Employee Offboarding SOP

## Revision History

| Version | Date | Author | Summary |
|---|---|---|---|
| 1.0 | 1 January 2024 | People & Culture | Initial issue |
| 2.0 | 1 January 2025 | People & Culture | Added data classification and incident reporting |
| 2.1 | 1 January 2026 | People & Culture | Added AI acceptable use and AI HR Assistant rules |

*This document is synthetic, created for the Quantic AI Engineering Techniques & Architectures project, and does not constitute legal advice.*

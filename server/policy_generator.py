#!/usr/bin/env python3
"""
Privacy Policy Generator for MSMEs
Generates legally compliant privacy policies, terms & conditions, and other legal documents
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class BusinessDetails(BaseModel):
    business_name: str = Field(..., min_length=1, max_length=255)
    business_type: str = Field(..., pattern="^(retail|service|manufacturing|e-commerce|saas|consulting|restaurant|healthcare|education|other)$")
    industry: str = Field(..., min_length=1, max_length=100)
    location_country: str = Field(..., min_length=1, max_length=100)
    location_state: Optional[str] = Field(None, max_length=100)
    location_city: Optional[str] = Field(None, max_length=100)
    website_url: Optional[str] = Field(None, max_length=500)
    has_online_presence: bool = Field(default=False)
    has_physical_store: bool = Field(default=False)
    collects_personal_data: bool = Field(default=True)
    processes_payments: bool = Field(default=False)
    uses_cookies: bool = Field(default=False)
    has_newsletter: bool = Field(default=False)
    target_audience: str = Field(default="B2C", pattern="^(B2B|B2C|Both)$")
    data_retention_period: int = Field(default=365, ge=30, le=3650)  # 30 days to 10 years

class PolicyGenerateRequest(BaseModel):
    business_details: BusinessDetails
    policy_types: List[str] = Field(..., min_items=1)  # ['privacy_policy', 'terms_conditions', 'refund_policy', 'cookie_policy']
    language: str = Field(default="en", pattern="^(en|hi|es|fr)$")

def determine_compliance_regions(country: str) -> List[str]:
    """Determine which legal compliance frameworks apply based on business location"""
    regions = []
    
    if country.lower() in ['india', 'in']:
        regions.extend(['Indian_IT_Act', 'Indian_Consumer_Protection_Act'])
    
    if country.lower() in ['germany', 'france', 'italy', 'spain', 'netherlands', 'belgium', 'austria', 'poland', 
                          'czech republic', 'hungary', 'romania', 'bulgaria', 'croatia', 'slovakia', 'slovenia',
                          'estonia', 'latvia', 'lithuania', 'luxembourg', 'malta', 'cyprus', 'denmark', 'sweden',
                          'finland', 'ireland', 'portugal', 'greece']:
        regions.append('GDPR')
    
    if country.lower() in ['united states', 'usa', 'us']:
        regions.extend(['CCPA', 'COPPA', 'US_FTC'])
    
    if country.lower() in ['canada', 'ca']:
        regions.append('PIPEDA')
    
    if country.lower() in ['united kingdom', 'uk', 'gb']:
        regions.extend(['UK_GDPR', 'UK_DPA'])
    
    if country.lower() in ['australia', 'au']:
        regions.append('Australian_Privacy_Act')
    
    # Default international compliance
    if not regions:
        regions.append('International_Best_Practices')
    
    return regions

def generate_privacy_policy(business: BusinessDetails, compliance_regions: List[str]) -> str:
    """Generate a comprehensive privacy policy"""
    
    current_date = datetime.now().strftime("%B %d, %Y")
    
    # Determine contact information section
    contact_section = f"""
## Contact Information

**Business Name:** {business.business_name}
**Business Type:** {business.business_type.title()}
**Location:** {business.location_city or ''}, {business.location_state or ''}, {business.location_country}
{f"**Website:** {business.website_url}" if business.website_url else ""}

For any questions about this Privacy Policy, please contact us through the contact information provided above.
"""

    # Data collection section based on business type
    data_collection_section = """
## Information We Collect

We collect information you provide directly to us, such as:

- **Personal Information:** Name, email address, phone number, and mailing address
- **Account Information:** Username, password, and preferences
"""
    
    if business.processes_payments:
        data_collection_section += "- **Payment Information:** Billing address and payment method details (processed securely through third-party payment processors)\n"
    
    if business.has_online_presence:
        data_collection_section += "- **Usage Information:** How you interact with our website and services\n"
        
    if business.uses_cookies:
        data_collection_section += "- **Cookies and Tracking:** Information collected through cookies and similar technologies\n"

    # Legal basis section (GDPR compliance)
    legal_basis_section = ""
    if 'GDPR' in compliance_regions or 'UK_GDPR' in compliance_regions:
        legal_basis_section = """
## Legal Basis for Processing (GDPR Compliance)

We process your personal data based on the following legal grounds:

- **Consent:** When you have given clear consent for specific processing activities
- **Contract Performance:** To fulfill our contractual obligations to you
- **Legal Obligation:** To comply with applicable laws and regulations
- **Legitimate Interest:** For our legitimate business interests, provided they don't override your rights
"""

    # Data usage section
    data_usage_section = f"""
## How We Use Your Information

We use the collected information for:

- Providing and maintaining our {business.business_type} services
- Processing transactions and sending related information
- Communicating with you about our products and services
- Improving our services and customer experience
- Complying with legal obligations and protecting our rights
"""

    if business.has_newsletter:
        data_usage_section += "- Sending marketing communications (with your consent)\n"

    # Data sharing section
    data_sharing_section = """
## Information Sharing

We do not sell, trade, or rent your personal information to third parties. We may share information in these limited circumstances:

- **Service Providers:** With trusted third-party service providers who assist in our operations
- **Legal Requirements:** When required by law or to protect our rights and safety
- **Business Transfers:** In connection with a merger, acquisition, or sale of assets
"""

    # Data retention section
    data_retention_section = f"""
## Data Retention

We retain your personal information for {business.data_retention_period} days from your last interaction with us, or as long as necessary to:

- Provide our services to you
- Comply with legal obligations
- Resolve disputes and enforce our agreements
- Maintain accurate business records
"""

    # Rights section (varies by compliance region)
    rights_section = """
## Your Rights

Depending on your location, you may have the following rights:

- **Access:** Request information about the personal data we hold about you
- **Correction:** Request correction of inaccurate or incomplete information
- **Deletion:** Request deletion of your personal data (subject to legal requirements)
- **Portability:** Request transfer of your data to another service provider
"""

    if 'GDPR' in compliance_regions or 'UK_GDPR' in compliance_regions:
        rights_section += "- **Withdraw Consent:** Withdraw consent for processing based on consent\n"
        rights_section += "- **Object to Processing:** Object to processing based on legitimate interests\n"
        rights_section += "- **Restrict Processing:** Request restriction of processing in certain circumstances\n"

    if 'CCPA' in compliance_regions:
        rights_section += "- **California Rights:** Additional rights under the California Consumer Privacy Act\n"

    # Security section
    security_section = """
## Data Security

We implement appropriate technical and organizational security measures to protect your personal information, including:

- Encryption of data in transit and at rest
- Regular security assessments and updates
- Access controls and employee training
- Secure payment processing (if applicable)

However, no method of transmission over the Internet is 100% secure.
"""

    # International transfers (if applicable)
    international_section = ""
    if business.location_country.lower() not in ['united states', 'usa', 'us'] and business.has_online_presence:
        international_section = """
## International Data Transfers

Your information may be transferred to and processed in countries other than your country of residence. We ensure appropriate safeguards are in place for such transfers in compliance with applicable data protection laws.
"""

    # Children's privacy section
    children_section = """
## Children's Privacy

Our services are not intended for children under 13 (or 16 in the EU). We do not knowingly collect personal information from children. If we become aware that we have collected information from a child, we will delete it promptly.
"""

    # Updates section
    updates_section = f"""
## Policy Updates

We may update this Privacy Policy from time to time. We will notify you of significant changes by posting the new policy on our website and updating the "Last Updated" date below.

**Last Updated:** {current_date}
"""

    # Compliance footer
    compliance_footer = f"""
---

This Privacy Policy is designed to comply with: {', '.join(compliance_regions)}

This policy is written in plain language to ensure transparency and understanding. It constitutes a legally binding agreement between {business.business_name} and its customers.
"""

    # Combine all sections
    policy_content = f"""# Privacy Policy

{contact_section}

{data_collection_section}

{legal_basis_section}

{data_usage_section}

{data_sharing_section}

{data_retention_section}

{rights_section}

{security_section}

{international_section}

{children_section}

{updates_section}

{compliance_footer}
"""

    return policy_content.strip()

def generate_terms_conditions(business: BusinessDetails, compliance_regions: List[str]) -> str:
    """Generate terms and conditions"""
    
    current_date = datetime.now().strftime("%B %d, %Y")
    
    terms_content = f"""# Terms and Conditions

**Effective Date:** {current_date}

## Agreement to Terms

By accessing and using the services of {business.business_name}, you agree to be bound by these Terms and Conditions.

## Description of Service

{business.business_name} operates as a {business.business_type} business in the {business.industry} industry, providing services to {business.target_audience.lower()} customers.

## User Responsibilities

You agree to:
- Provide accurate and current information
- Use our services lawfully and respectfully
- Respect intellectual property rights
- Not interfere with the security or functionality of our services

## Payment Terms

{f"- All payments are processed securely through third-party payment processors" if business.processes_payments else "- Payment terms will be communicated separately for applicable services"}
- Prices are subject to change with notice
- Refunds are handled according to our Refund Policy

## Intellectual Property

All content, trademarks, and intellectual property remain the property of {business.business_name} or respective owners.

## Limitation of Liability

To the maximum extent permitted by law, {business.business_name} shall not be liable for any indirect, incidental, or consequential damages.

## Governing Law

These terms are governed by the laws of {business.location_country}{f", {business.location_state}" if business.location_state else ""}.

## Contact Information

For questions about these terms, contact {business.business_name} through our provided contact channels.

---

This document complies with: {', '.join(compliance_regions)}
"""

    return terms_content

def generate_refund_policy(business: BusinessDetails, compliance_regions: List[str]) -> str:
    """Generate refund policy"""
    
    current_date = datetime.now().strftime("%B %d, %Y")
    
    # Refund periods based on business type
    refund_period = {
        'e-commerce': '30 days',
        'saas': '14 days',
        'service': '48 hours',
        'retail': '15 days',
        'consulting': '24 hours'
    }.get(business.business_type, '14 days')
    
    refund_content = f"""# Refund Policy

**Effective Date:** {current_date}

## Refund Eligibility

{business.business_name} offers refunds under the following conditions:

- Requests must be made within {refund_period} of purchase
- Items/services must be in original condition (if applicable)
- Valid proof of purchase is required

## Refund Process

1. Contact us with your refund request
2. Provide order details and reason for refund
3. We will review and process eligible refunds within 5-10 business days
4. Refunds will be processed to the original payment method

## Non-Refundable Items

- Digital products after download (unless defective)
- Customized or personalized services
- Services already completed

## Processing Time

- Credit card refunds: 5-10 business days
- Bank transfers: 7-14 business days
- Digital wallet refunds: 1-3 business days

## Contact Us

For refund requests, contact {business.business_name} through our customer service channels.

---

This policy complies with consumer protection laws in: {', '.join(compliance_regions)}
"""

    return refund_content

def generate_cookie_policy(business: BusinessDetails, compliance_regions: List[str]) -> str:
    """Generate cookie policy"""
    
    if not business.uses_cookies or not business.has_online_presence:
        return ""
    
    current_date = datetime.now().strftime("%B %d, %Y")
    
    cookie_content = f"""# Cookie Policy

**Effective Date:** {current_date}

## What Are Cookies

Cookies are small text files stored on your device when you visit our website. They help us provide a better user experience.

## Types of Cookies We Use

### Essential Cookies
- Required for basic website functionality
- Cannot be disabled without affecting site performance

### Analytics Cookies
- Help us understand how visitors interact with our website
- Used to improve our services and user experience

### Marketing Cookies
- Used to deliver relevant advertisements
- Help measure the effectiveness of advertising campaigns

## Managing Cookies

You can control cookies through your browser settings:
- **Chrome:** Settings > Privacy and Security > Cookies
- **Firefox:** Settings > Privacy & Security > Cookies and Site Data
- **Safari:** Preferences > Privacy > Cookies and Website Data

## Third-Party Cookies

We may use third-party services that set their own cookies:
- Google Analytics (for website analytics)
- Payment processors (for transaction security)

## Cookie Retention

- Session cookies: Deleted when you close your browser
- Persistent cookies: Stored for up to {business.data_retention_period} days

## Contact Us

For questions about our cookie policy, contact {business.business_name}.

---

This policy complies with: {', '.join(compliance_regions)}
"""

    return cookie_content

def generate_policies(business_details: BusinessDetails, policy_types: List[str], language: str = "en") -> Dict[str, str]:
    """Generate multiple policies based on business details"""
    
    compliance_regions = determine_compliance_regions(business_details.location_country)
    policies = {}
    
    if 'privacy_policy' in policy_types:
        policies['privacy_policy'] = generate_privacy_policy(business_details, compliance_regions)
    
    if 'terms_conditions' in policy_types:
        policies['terms_conditions'] = generate_terms_conditions(business_details, compliance_regions)
    
    if 'refund_policy' in policy_types:
        policies['refund_policy'] = generate_refund_policy(business_details, compliance_regions)
    
    if 'cookie_policy' in policy_types and business_details.uses_cookies:
        policies['cookie_policy'] = generate_cookie_policy(business_details, compliance_regions)
    
    return policies

# Policy templates for different languages (basic implementation)
POLICY_TEMPLATES = {
    "en": {
        "privacy_policy": "Privacy Policy",
        "terms_conditions": "Terms and Conditions", 
        "refund_policy": "Refund Policy",
        "cookie_policy": "Cookie Policy"
    },
    "hi": {
        "privacy_policy": "गोपनीयता नीति",
        "terms_conditions": "नियम और शर्तें",
        "refund_policy": "रिफंड नीति", 
        "cookie_policy": "कुकी नीति"
    }
}

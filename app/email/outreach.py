# email/outreach.py

def generate_outreach_email(brand, niche, influencer_handle, offer):
    subject = f"Collaboration Opportunity with {brand}"

    body = f"""
Hi {influencer_handle},

My name is {brand}, and we came across your content in the {niche} space.
We really like your style and audience.

We’d love to explore a collaboration with you.
Offer details:
• {offer}
• Flexible timeline
• Paid opportunity

Let us know if you’re interested and we can share more details.

Best,
{brand}
"""

    return {
        "subject": subject.strip(),
        "body": body.strip()
    }
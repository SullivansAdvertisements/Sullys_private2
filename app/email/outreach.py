def generate_outreach_email(
    brand: str,
    niche: str,
    influencer_handle: str,
    offer: str,
):
    subject = f"Collab Opportunity with {brand}"

    body = f"""
Hi {influencer_handle},

I’m reaching out from {brand}. We’re working on a new {niche} campaign and love your content.

We’d love to collaborate with you on a paid feature / promo.
Offer: {offer}

If this sounds interesting, let me know and I’ll share details.

Best,
{brand} Team
    """.strip()

    return {"subject": subject, "body": body}


def generate_followup_email(brand: str, influencer_handle: str):
    return f"""
Hey {influencer_handle},

Just following up on my last message — would love to collaborate if you’re open to it.

Thanks!
{brand}
""".strip()
import os
import time
import smtplib
from email.message import EmailMessage
from duckduckgo_search import DDGS
from groq import Groq
from datetime import datetime

# 1. Setup Groq
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY environment variable not set!")
client = Groq(api_key=api_key)

def search_news():
    queries = [
        "Shariah compliant wealth management ethical trends",
        "Islamic finance ESG investment news",
        "green sukuk ethical investing wealth management",
        "Islamic finance infrastructure real assets trends",
        "halal investing market outlook 2026"
    ]
    all_news = []
    with DDGS() as ddgs:
        for query in queries:
            try:
                results = list(ddgs.news(query, max_results=4))
                for r in results:
                    all_news.append(f"- {r['title']} ({r['date']}): {r['body']}")
                time.sleep(2) 
            except Exception as e:
                print(f"Search error for {query}: {e}")
    return "\n".join(all_news)

def generate_article(trends_data):
    today = datetime.now().strftime('%B %d, %Y')
    year = datetime.now().strftime('%Y')
    
    prompt = f"""
You are the Chief Content Strategist for WeiseWealth / WeiseCompass, a premium wealth management startup specializing in Shariah-compliant and ethical investing. Your writing is known for being intellectually rigorous, data-rich, metaphor-driven, and brutally honest about limitations.

Today's date is {today}.

Based on the following recent news data, write a long-form LinkedIn article (1000-1400 words) that EXACTLY follows the structure and style of the template below.

=== TEMPLATE STRUCTURE (FOLLOW THIS EXACTLY) ===

LinkedIn Post (Ready to Publish)

#WeiseCompass: {year} Trends — [METAPHORICAL TITLE]: [DESCRIPTIVE SUBTITLE]

[One-line hook summarizing the core insight]

[CULTURAL/LITERARY OPENING: 1-2 sentences using a powerful metaphor from literature, history, or nature — like Frank Herbert's Dune, Sun Tzu, Ibn Khaldun, or a historical trade route. This metaphor must connect to the financial theme.]

Why: The [Problem/Exposure Name]
[2-3 paragraphs explaining the core problem. MUST include specific data points and cite sources inline like "according to X" or "X reported that...". Be precise with numbers.]

How: [The Solutions] and Their Limits
[2-3 paragraphs explaining the market's response/solutions. MUST include:
- Specific data points with sources
- A critical subsection explaining 3+ LIMITS or hidden risks of these solutions
- Be intellectually honest — do not oversell]

The Power of [Theme]: The Sectors Capturing the Shift
[Intro paragraph explaining where institutional capital is flowing]
Then use this exact sub-structure with 3-4 bullet points:
• [Sector 1]: [Specific description of what's happening]
• [Sector 2]: [Specific description]
• [Sector 3]: [Specific description]

The Insight: [One sentence acknowledging these sectors face their own risks — permitting, financing, political risk, etc.]

To What Extent: The Limits of the Thesis & Shariah Screening Nuances
[This is the MOST IMPORTANT section. It must contain TWO parts:]

Part 1 — Honest Limits: 1-2 paragraphs explaining why the thesis is NOT a one-way bet. What could go wrong? What is being overpriced?

Part 2 — Shariah Screening Nuances: 2-3 bullet points with DEEP technical Shariah analysis. You MUST reference specific concepts like:
- AAOIFI standards and specific thresholds (e.g., 33% debt-to-market-cap)
- Specific Islamic finance instruments (ijara, murabaha, musharaka, sukuk structures)
- Technical traps (e.g., how market-cap fluctuations can cause a previously-compliant company to fail screening)
- The difference between real-asset backing vs. "ghost stocks"
- The need for case-by-case scholarly review

Do NOT be generic here. This section must demonstrate real Shariah compliance expertise.

WeiseWealth Wisdom for Wealth Managers
[1-2 sentences of closing wisdom, ideally tying back to the opening metaphor. Make it memorable and quotable.]

Disclaimer: This is analysis, not investment advice. Anyone acting on it should consult a qualified adviser and review the screening methodology for the specific fund or company.

[ENGAGEMENT QUESTION: One specific, thought-provoking question that invites comments. Example: "Which indicator would you watch first to judge whether these routes are working: tanker transits, pipeline utilization, or insurance rates?"]

#WeiseCompass #[8-12 highly relevant hashtags, mixing broad (#WealthManagement #ShariahCompliant) and specific (#GreenSukuk #AAOIFI #InfrastructureInvesting)]

=== STRICT STYLE RULES ===
1. Use the news data as your source material. Cite sources inline (Bloomberg, Reuters, EIA, IMF, etc.) even if you have to paraphrase.
2. Be intellectually honest. Every bull case must have a bear case. Never oversell.
3. The Shariah section must be TECHNICAL, not generic. Reference AAOIFI, specific ratios, specific instruments.
4. The metaphor must appear in the opening AND be referenced again in the closing wisdom.
5. Use clean paragraphs. No emojis. Professional, authoritative tone — like a senior strategist writing for institutional clients.
6. Total length: 1000-1400 words.

=== NEWS DATA ===
{trends_data}
"""
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content

def send_email(subject, body):
    sender_email = os.environ.get("EMAIL_SENDER")
    sender_password = os.environ.get("EMAIL_PASSWORD") 
    receiver_email = os.environ.get("EMAIL_RECEIVER")

    if not all([sender_email, sender_password, receiver_email]):
        print("⚠️ Email credentials not fully set. Skipping email.")
        return

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver_email
    
    header = f"Hi there,\n\nYour weekly WeiseCompass article is ready for LinkedIn. Just copy the text below and paste it directly.\n\n{'='*60}\n\n"
    footer = f"\n\n{'='*60}\n\nReminder before posting:\n• Review the Shariah technical section for accuracy\n• Consider tagging relevant partners or scholars\n• Engage with early comments within the first hour for algorithm boost\n"
    
    msg.set_content(header + body + footer)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)
        print(f"✅ Email successfully sent to {receiver_email}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

if __name__ == "__main__":
    print("🔍 Screening news...")
    news_data = search_news()
    
    if not news_data:
        print("No news found. Exiting.")
        exit()
        
    print("✍️ Writing WeiseCompass article...")
    article = generate_article(news_data)
    
    os.makedirs("articles", exist_ok=True)
    today_str = datetime.now().strftime('%Y-%m-%d')
    filename = f"articles/article_{today_str}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(article)
    print(f"✅ Article saved to {filename}")

    email_subject = f"🚀 Ready for LinkedIn: WeiseCompass Weekly - {today_str}"
    send_email(email_subject, article)

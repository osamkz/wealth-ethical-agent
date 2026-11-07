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
    # Broad queries to capture significant economic/energy stories
    queries = [
        "global energy markets economic news",
        "infrastructure supply chain metals commodities",
        "geopolitical energy security trade routes",
        "Islamic finance ESG sustainable investing",
        "macroeconomic trends infrastructure investment"
    ]
    all_news = []
    with DDGS() as ddgs:
        for query in queries:
            try:
                results = list(ddgs.news(query, max_results=5))
                for r in results:
                    all_news.append(f"- {r['title']} ({r['date']}): {r['body']}")
                time.sleep(2) 
            except Exception as e:
                print(f"Search error for {query}: {e}")
    return "\n".join(all_news)

def generate_editorial_workflow(trends_data):
    today = datetime.now().strftime('%B %d, %Y')
    
    prompt = f"""
You are a senior economic analyst and editorial strategist. Today's date is {today}.

=== STEP 1: CHOOSE THE TOPIC ===
Search for the most significant economic or energy stories from the past two weeks, focusing on energy, infrastructure, supply chains, metals, and geopolitical trade routes.

Propose three candidate topics. For each, provide:
- Topic name
- One line on why it matters now
- Main sources covering it (from the news data below)

Then pick the strongest one and explain your choice in two sentences.

=== STEP 2: CHOOSE THE FILM ===
Select a film whose central dilemma matches the chosen topic's structure (e.g., single point of failure, scarce resource, contested route, struggle over power and supply). Do not choose a film just because it shares a setting or genre.

Explain the match in one sentence.

=== STEP 3: WRITE THE ARTICLE ===
Write about 900 to 1,000 words in the voice of an economic analyst: measured, analytical, and informative. It is commentary, not investment advice.

Open and close with a brief reference to the film. Use one or two further references in the body where they clarify a specific point. The film should illustrate the analysis, not replace it. Do not retell the plot, do not quote dialogue beyond a short phrase, and do not use film stills or copyrighted artwork.

Organize the article around three questions, with a bold heading for each:

**Why:** What is the exposure, and why does it matter now?
**How:** What responses exist, and what are their concrete capacities and limits?
**To what extent:** How far do these responses reduce the risk, and what are the timelines, costs, and open uncertainties?

**The Sectors Capturing the Shift:**
Identify three asset-backed sectors or industries that will structurally benefit from the situation described in the news. For each sector:
- Name the sector/industry (e.g., "Pipeline Engineering & Grid Construction," "Specialized Metallurgy & Steel Tubing," "Intermodal Logistics & Storage Terminals")
- Explain in 2-3 sentences how this sector benefits from the structural shift
- Name 2-3 representative companies or listed stocks within that sector as concrete examples (with ticker symbols where relevant) to illustrate the type of business exposed to this trend
- Focus on real-economy, asset-backed businesses (physical infrastructure, commodities, industrial production) rather than speculative or purely financial plays
- Note any risks or limitations these sectors face (permitting, financing, political risk, etc.)

**Shariah Screening Note for the Sectors:**
For each of the three sectors identified above, add a brief note (2-3 sentences) addressing Shariah compliance considerations:
- Whether the sector is generally permissible in principle (e.g., asset-backed industrial businesses are typically favored over purely speculative or interest-based businesses)
- Common screening issues investors should watch (e.g., interest-bearing debt ratios under AAOIFI's 33% threshold, impermissible revenue streams, the market-cap denominator trap where a compliant company can fail screening during a market downturn without taking on new debt)
- A clear reminder that permissibility is judged company by company by qualified Shariah scholars, and that structures like ijara, murabaha, or sukuk must be reviewed case by case

STRICT RULES:
- Ground every figure in a named source with its date, and say when a figure is an estimate.
- Where sources disagree or reporting is unclear, say so.
- If you name a company, frame it as an illustrative example of the sector, not as a recommendation or position.
- Mark anything that depends on recent developments as "as of {today}."
- Close with one question for readers.

=== STEP 4: FACT-CHECK LIST ===
Create a list of every figure, company name, and film reference with its source or basis for checking.

=== OUTPUT FORMAT ===
Output the following in this exact order:

## CANDIDATE TOPICS
[Topic 1 with sources and why it matters]
[Topic 2 with sources and why it matters]
[Topic 3 with sources and why it matters]

## CHOSEN TOPIC
[Topic name]
[Two-sentence justification]

## CHOSEN FILM
[Film title]
[One-sentence explanation of the match]

## ARTICLE
[The full 900-1,000 word article with the five sections: Why, How, To what extent, The Sectors Capturing the Shift, Shariah Screening Note]

## FACT-CHECK LIST
[Every figure, company name, and film reference with source]

=== SOURCE MATERIAL ===
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
    
    header = f"Hi there,\n\nYour weekly editorial workflow is complete. Below you'll find:\n• 3 candidate topics with sources\n• The chosen topic and film\n• The full article (ready for LinkedIn) including sector analysis and Shariah screening notes\n• A fact-check list for verification\n\n{'='*60}\n\n"
    footer = f"\n\n{'='*60}\n\nReminder before posting:\n• Copy only the ARTICLE section for LinkedIn\n• Verify key figures and company names using the fact-check list\n• Review the Shariah screening notes with a qualified scholar if publishing under your brand\n• Engage with early comments within the first hour\n"
    
    msg.set_content(header + body + footer)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)
        print(f"✅ Email successfully sent to {receiver_email}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

if __name__ == "__main__":
    print("🔍 Screening news for significant economic/energy stories...")
    news_data = search_news()
    
    if not news_data:
        print("No news found. Exiting.")
        exit()
        
    print("✍️ Running editorial workflow (topic selection, film matching, article writing, sector analysis, Shariah notes)...")
    editorial_output = generate_editorial_workflow(news_data)
    
    os.makedirs("articles", exist_ok=True)
    today_str = datetime.now().strftime('%Y-%m-%d')
    filename = f"articles/article_{today_str}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(editorial_output)
    print(f"✅ Editorial workflow saved to {filename}")

    email_subject = f"🚀 Weekly Editorial Ready - {today_str}"
    send_email(email_subject, editorial_output)

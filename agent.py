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

STRICT RULES:
- Ground every figure in a named source with its date, and say when a figure is an estimate.
- Where sources disagree or reporting is unclear, say so.
- Do not name specific stocks, recommend positions, or present any sector as a good investment.
- If you discuss Islamic finance screening, describe general principles and note that compliance is judged company by company by qualified Shariah scholars.
- Mark anything that depends on recent developments as "as of {today}."
- Close with one question for readers.

=== STEP 4: FACT-CHECK LIST ===
Create a list of every figure and film reference with its source or basis for checking.

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
[The full 900-1,000 word article]

## FACT-CHECK LIST
[Every figure and film reference with source]

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
    
    header = f"Hi there,\n\nYour weekly editorial workflow is complete. Below you'll find:\n• 3 candidate topics with sources\n• The chosen topic and film\n• The full article (ready for LinkedIn)\n• A fact-check list for verification\n\n{'='*60}\n\n"
    footer = f"\n\n{'='*60}\n\nReminder before posting:\n• Copy only the ARTICLE section for LinkedIn\n• Verify key figures using the fact-check list\n• Engage with early comments within the first hour\n"
    
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
        
    print("✍️ Running editorial workflow (topic selection, film matching, article writing)...")
    editorial_output = generate_editorial_workflow(news_data)
    
    os.makedirs("articles", exist_ok=True)
    today_str = datetime.now().strftime('%Y-%m-%d')
    filename = f"articles/article_{today_str}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(editorial_output)
    print(f"✅ Editorial workflow saved to {filename}")

    email_subject = f"🚀 Weekly Editorial Ready - {today_str}"
    send_email(email_subject, editorial_output)

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
        "Islamic finance infrastructure real assets trends"
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
    
    prompt = f"""
Write a LinkedIn article of about 900 to 1,000 words on the topic derived from the source material below. 

Voice: Write in the voice of an economic analyst: measured, analytical, and informative. It is commentary, not investment advice.

Framing Device: Frame the article with a film chosen for its fit with the topic. Choose a film whose central dilemma matches the topic, and explain why you chose it in one sentence. Open and close with a brief reference to it, and use one or two further references in the body where they clarify a specific point. The film should illustrate the analysis, not replace it. Do not retell the plot, do not quote dialogue beyond a short phrase, and do not mention film stills or copyrighted artwork.

Organize the article around three questions, with a bold heading for each:

**Why:** What is the exposure, and why does it matter now?
**How:** What responses exist, and what are their concrete capacities and limits?
**To what extent:** How far do these responses reduce the risk, and what are the timelines, costs, and open uncertainties?

STRICT RULES:
1. Ground every figure in a named source, and say when a figure is an estimate.
2. Where sources disagree or reporting is unclear, say so.
3. Do not name specific stocks, recommend positions, or present any sector as a "good investment."
4. If you discuss Islamic finance screening, describe general principles and explicitly note that compliance is judged company by company by qualified Shariah scholars.
5. Mark anything that depends on recent developments as "as of {today}".
6. Close with exactly one thought-provoking question for readers.
7. Do not use emojis. Keep the formatting clean and professional.

Source material (facts, figures, and links, with dates):
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
    
    header = f"Hi there,\n\nYour weekly economic analysis article is ready for LinkedIn. Just copy the text below and paste it directly.\n\n{'='*60}\n\n"
    footer = f"\n\n{'='*60}\n\nReminder before posting:\n• Verify any specific figures or dates\n• Ensure the film metaphor lands well for your audience\n• Engage with early comments within the first hour\n"
    
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
        
    print("✍️ Writing economic analysis article...")
    article = generate_article(news_data)
    
    os.makedirs("articles", exist_ok=True)
    today_str = datetime.now().strftime('%Y-%m-%d')
    filename = f"articles/article_{today_str}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(article)
    print(f"✅ Article saved to {filename}")

    email_subject = f"🚀 Ready for LinkedIn: Weekly Economic Analysis - {today_str}"
    send_email(email_subject, article)

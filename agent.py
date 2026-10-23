import os
import time
import smtplib
from email.message import EmailMessage
from duckduckgo_search import DDGS
from openai import OpenAI
from datetime import datetime

# 1. Setup OpenAI
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set!")
client = OpenAI(api_key=api_key)

def search_news():
    queries = [
        "Shariah compliant wealth management ethical trends",
        "Islamic finance ESG investment news",
        "green sukuk ethical investing wealth management"
    ]
    all_news = []
    with DDGS() as ddgs:
        for query in queries:
            try:
                results = list(ddgs.news(query, max_results=3))
                for r in results:
                    all_news.append(f"- {r['title']} ({r['date']}): {r['body']}")
                time.sleep(2) 
            except Exception as e:
                print(f"Search error for {query}: {e}")
    return "\n".join(all_news)

def generate_article(trends_data):
    today = datetime.now().strftime('%B %d, %Y')
    prompt = f"""
    You are an expert content strategist for a Wealth Management startup specializing in Shariah-compliant and ethical investing. 
    Today's date is {today}.
    Based on the following recent news data, write a 600-800 word weekly article titled "Weekly Ethical Wealth Trends".
    
    STRICT GUIDELINES:
    1. Shariah Compliance: Align with Islamic finance. Do not promote riba (interest), gharar (excessive uncertainty), or haram industries.
    2. ESG Alignment: Highlight the synergy between Islamic finance and ESG (e.g., real-economy asset backing, social stewardship).
    3. Structure: Catchy Title, Executive Summary, Top 3 Ethical Trends, Actionable Takeaway, and a Disclaimer.
    4. Tone: Professional, insightful, and accessible.
    5. LinkedIn Formatting: Use clean paragraphs, bullet points, and relevant emojis sparingly to make it highly readable on LinkedIn.
    
    NEWS DATA:
    {trends_data}
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini", 
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
    
    header = f"Hi there,\n\nYour weekly Shariah-compliant wealth article is ready! Just copy the text below and paste it directly into LinkedIn.\n\n{'='*50}\n\n"
    footer = f"\n\n{'='*50}\n\nDon't forget to add 3-5 relevant hashtags (e.g., #IslamicFinance #ESG #WealthManagement) and tag relevant partners before posting!"
    
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
        
    print("✍️ Writing article...")
    article = generate_article(news_data)
    
    os.makedirs("articles", exist_ok=True)
    today_str = datetime.now().strftime('%Y-%m-%d')
    filename = f"articles/article_{today_str}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(article)
    print(f"✅ Article saved to {filename}")

    email_subject = f"🚀 Ready for LinkedIn: Weekly Ethical Wealth Trends - {today_str}"
    send_email(email_subject, article)

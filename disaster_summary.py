import anthropic
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

def create_disaster_summary():
    """Create a weekly summary of natural disasters in Southeast Asia"""
    
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    
    # Calculate date range
    today = datetime.now()
    week_ago = today - timedelta(days=7)
    
    print(f"Generating disaster summary for {week_ago.strftime('%B %d')} - {today.strftime('%B %d, %Y')}")
    
    # Create the request
    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=4000,
        messages=[{
            "role": "user",
            "content": f"""Search for and create a comprehensive summary of all natural disasters in Southeast Asia from {week_ago.strftime('%B %d')} to {today.strftime('%B %d, %Y')}.

Southeast Asia includes: Philippines, Indonesia, Vietnam, Thailand, Myanmar, Malaysia, Singapore, Cambodia, Laos, Brunei, and Timor-Leste.

Cover these types of events:
- Earthquakes and aftershocks
- Typhoons, cyclones, and tropical storms
- Floods and flash floods
- Volcanic eruptions and activity
- Landslides and mudslides
- Tsunamis
- Droughts (if severe)

For each event, include:
- Type of disaster
- Location (country and region)
- Date
- Severity/magnitude
- Impact (casualties, displaced people, damage if available)
- Current status

Format the summary clearly with sections for each type of disaster. Add the sources of the information."""
        }],
        tools=[{"type": "web_search_20250305", "name": "web_search"}]
    )
    
    # Extract the summary
    summary = ""
    for block in message.content:
        if block.type == "text":
            summary += block.text + "\n"
    
    return summary

def save_summary(summary):
    """Save the summary to a file"""
    timestamp = datetime.now().strftime('%Y-%m-%d')
    filename = f"summaries/summary_{timestamp}.md"
    
    # Create summaries directory if it doesn't exist
    os.makedirs("summaries", exist_ok=True)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"# Southeast Asia Natural Disaster Summary\n")
        f.write(f"**Week ending:** {datetime.now().strftime('%B %d, %Y')}\n\n")
        f.write(summary)
    
    print(f"Summary saved to {filename}")
    return filename

def send_email(summary):
    """Send summary via email"""
    sender = os.environ.get("omar.bellprat@gmail.com")
    password = os.environ.get("jbyw arol vwex ztgi")
    recipient = os.environ.get("omar.bellprat@gmail.com")
    
    if not all([sender, password, recipient]):
        print("Email credentials not configured, skipping email send")
        return
    
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = f'SE Asia Disaster Summary - {datetime.now().strftime("%B %d, %Y")}'
    
    msg.attach(MIMEText(summary, 'plain'))
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender, password)
            smtp.send_message(msg)
        print(f"Email sent successfully to {recipient}")
    except Exception as e:
        print(f"Failed to send email: {e}")

def main():
    try:
        print("Starting disaster summary generation...")
        summary = create_disaster_summary()
        filename = save_summary(summary)
        
        print("\n" + "="*50)
        print("SUMMARY PREVIEW:")
        print("="*50)
        print(summary[:500] + "...\n")
        print(f"Full summary saved to: {filename}")
        
        # Send email if configured
        send_email(summary)
        
    except Exception as e:
        print(f"Error generating summary: {e}")
        raise

if __name__ == "__main__":
    main()

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
    """Send summary via email with HTML formatting"""
    sender = os.environ.get("EMAIL_SENDER")
    password = os.environ.get("EMAIL_PASSWORD")
    recipient = os.environ.get("EMAIL_RECIPIENT")
    
    print(f"Email config check:")
    print(f"  Sender configured: {bool(sender)}")
    print(f"  Password configured: {bool(password)}")
    print(f"  Recipient configured: {bool(recipient)}")
    
    if not all([sender, password, recipient]):
        print("❌ Email credentials not configured, skipping email send")
        return
    
    print(f"Attempting to send email from {sender} to {recipient}")
    
    # Convert Markdown to HTML
    html_content = markdown_to_html(summary)
    
    # Create message with both plain text and HTML
    msg = MIMEMultipart('alternative')
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = f'🌏 SE Asia Disaster Summary - {datetime.now().strftime("%B %d, %Y")}'
    
    # Attach both plain text and HTML versions
    part1 = MIMEText(summary, 'plain')
    part2 = MIMEText(html_content, 'html')
    
    msg.attach(part1)
    msg.attach(part2)
    
    try:
        print("Connecting to Gmail SMTP server...")
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            print("Logging in...")
            smtp.login(sender, password)
            print("Sending message...")
            smtp.send_message(msg)
        print(f"✅ Email sent successfully to {recipient}")
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        print("Make sure you're using an App Password, not your regular Gmail password")
    except Exception as e:
        print(f"❌ Failed to send email: {type(e).__name__}: {e}")

def markdown_to_html(markdown_text):
    """Convert Markdown to formatted HTML email"""
    
    # Start with a nice email template
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background-color: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            h1 {
                color: #d32f2f;
                border-bottom: 3px solid #d32f2f;
                padding-bottom: 10px;
            }
            h2 {
                color: #1976d2;
                margin-top: 30px;
                border-left: 4px solid #1976d2;
                padding-left: 15px;
            }
            h3 {
                color: #388e3c;
                margin-top: 20px;
            }
            ul {
                padding-left: 20px;
            }
            li {
                margin-bottom: 8px;
            }
            strong {
                color: #d32f2f;
            }
            .footer {
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
                font-size: 0.9em;
                color: #666;
                text-align: center;
            }
            .highlight {
                background-color: #fff3cd;
                padding: 2px 6px;
                border-radius: 3px;
            }
        </style>
    </head>
    <body>
        <div class="container">
    """
    
    # Simple Markdown to HTML conversion
    lines = markdown_text.split('\n')
    in_list = False
    
    for line in lines:
        line = line.strip()
        
        if not line:
            if in_list:
                html += "</ul>\n"
                in_list = False
            html += "<br>\n"
            continue
        
        # Headers
        if line.startswith('# '):
            if in_list:
                html += "</ul>\n"
                in_list = False
            html += f"<h1>{line[2:]}</h1>\n"
        elif line.startswith('## '):
            if in_list:
                html += "</ul>\n"
                in_list = False
            html += f"<h2>{line[3:]}</h2>\n"
        elif line.startswith('### '):
            if in_list:
                html += "</ul>\n"
                in_list = False
            html += f"<h3>{line[4:]}</h3>\n"
        
        # Bold text with **
        elif '**' in line:
            if in_list:
                html += "</ul>\n"
                in_list = False
            line = line.replace('**', '<strong>', 1)
            line = line.replace('**', '</strong>', 1)
            html += f"<p>{line}</p>\n"
        
        # Bullet points
        elif line.startswith('- ') or line.startswith('* '):
            if not in_list:
                html += "<ul>\n"
                in_list = True
            item = line[2:]
            # Handle bold within list items
            while '**' in item:
                item = item.replace('**', '<strong>', 1)
                item = item.replace('**', '</strong>', 1)
            html += f"<li>{item}</li>\n"
        
        # Horizontal rule
        elif line.startswith('---'):
            if in_list:
                html += "</ul>\n"
                in_list = False
            html += "<hr>\n"
        
        # Regular paragraph
        else:
            if in_list:
                html += "</ul>\n"
                in_list = False
            # Handle bold in paragraphs
            while '**' in line:
                line = line.replace('**', '<strong>', 1)
                line = line.replace('**', '</strong>', 1)
            html += f"<p>{line}</p>\n"
    
    if in_list:
        html += "</ul>\n"
    
    # Close the HTML
    html += """
        <div class="footer">
            <p>Generated automatically by Disaster Summary Agent</p>
            <p>Powered by Claude AI | Data from web sources</p>
        </div>
        </div>
    </body>
    </html>
    """
    
    return html

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

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
                color: #2c3e50;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f8f9fa;
            }
            .container {
                background-color: white;
                padding: 40px;
                border-radius: 12px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            h1 {
                color: #c0392b;
                border-bottom: 4px solid #c0392b;
                padding-bottom: 15px;
                margin-bottom: 30px;
                font-size: 28px;
            }
            h2 {
                color: #2980b9;
                margin-top: 35px;
                margin-bottom: 20px;
                border-left: 5px solid #2980b9;
                padding-left: 20px;
                font-size: 24px;
                background-color: #ebf5fb;
                padding-top: 10px;
                padding-bottom: 10px;
            }
            h3 {
                color: #27ae60;
                margin-top: 25px;
                margin-bottom: 15px;
                font-size: 20px;
            }
            p {
                margin: 10px 0;
                line-height: 1.8;
            }
            ul {
                padding-left: 25px;
                margin: 15px 0;
            }
            li {
                margin-bottom: 10px;
                line-height: 1.7;
            }
            .label {
                color: #c0392b;
                font-weight: bold;
            }
            hr {
                border: none;
                border-top: 2px solid #ecf0f1;
                margin: 30px 0;
            }
            .footer {
                margin-top: 50px;
                padding-top: 25px;
                border-top: 2px solid #ecf0f1;
                font-size: 14px;
                color: #7f8c8d;
                text-align: center;
            }
            .date-range {
                background-color: #fff3cd;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 25px;
                border-left: 4px solid #ffc107;
                font-size: 16px;
            }
        </style>
    </head>
    <body>
        <div class="container">
    """
    
    # Clean up the markdown text
    lines = markdown_text.split('\n')
    in_list = False
    
    for line in lines:
        original_line = line
        line = line.strip()
        
        if not line:
            if in_list:
                html += "</ul>\n"
                in_list = False
            continue
        
        # Remove all ** from the line first for processing
        display_line = line.replace('**', '')
        
        # Headers
        if line.startswith('# '):
            if in_list:
                html += "</ul>\n"
                in_list = False
            html += f"<h1>{display_line[2:]}</h1>\n"
        
        elif line.startswith('## '):
            if in_list:
                html += "</ul>\n"
                in_list = False
            html += f"<h2>{display_line[3:]}</h2>\n"
        
        elif line.startswith('### '):
            if in_list:
                html += "</ul>\n"
                in_list = False
            html += f"<h3>{display_line[4:]}</h3>\n"
        
        # Bullet points (handle both - and *)
        elif line.startswith('- ') or line.startswith('* '):
            if not in_list:
                html += "<ul>\n"
                in_list = True
            
            item = display_line[2:]
            
            # Check if line contains labels like "Type:", "Location:", etc.
            if ':' in item:
                parts = item.split(':', 1)
                if len(parts) == 2:
                    label = parts[0].strip()
                    value = parts[1].strip()
                    html += f'<li><span class="label">{label}:</span> {value}</li>\n'
                else:
                    html += f"<li>{item}</li>\n"
            else:
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
            
            # Check if it's a label line (like "Type: something")
            if ':' in display_line and not display_line.startswith('http'):
                parts = display_line.split(':', 1)
                if len(parts) == 2 and len(parts[0]) < 30:  # Likely a label
                    label = parts[0].strip()
                    value = parts[1].strip()
                    html += f'<p><span class="label">{label}:</span> {value}</p>\n'
                else:
                    html += f"<p>{display_line}</p>\n"
            else:
                html += f"<p>{display_line}</p>\n"
    
    if in_list:
        html += "</ul>\n"
    
    # Close the HTML
    html += """
        <div class="footer">
            <p><strong>📊 Automated Weekly Report</strong></p>
            <p>Generated by Disaster Summary Agent • Powered by Claude AI</p>
            <p style="font-size: 12px; margin-top: 10px;">Data compiled from multiple news and disaster monitoring sources</p>
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

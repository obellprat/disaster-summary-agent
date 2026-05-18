import openai
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

def create_disaster_summary():
    """Create a weekly summary of natural disasters in Southeast Asia and the Pacific"""
    
    client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    # Calculate date range
    today = datetime.now()
    week_ago = today - timedelta(days=7)
    
    print(f"Generating disaster summary for {week_ago.strftime('%B %d')} - {today.strftime('%B %d, %Y')}")
    
    # Create the request
    response = client.chat.completions.create(
        model="gpt-4o",  # Latest GPT-4 model with web search capability
        messages=[{
            "role": "user",
            "content": f"""Search for and create a comprehensive summary of all natural disasters in Southeast Asia and the Pacific from {week_ago.strftime('%B %d')} to {today.strftime('%B %d, %Y')}.

**REGIONS TO COVER:**

Southeast Asia: Philippines, Indonesia, Vietnam, Thailand, Myanmar, Malaysia, Singapore, Cambodia, Laos, Brunei, and Timor-Leste.

Pacific: Papua New Guinea, Solomon Islands, Vanuatu, Fiji, Samoa, Tonga, Kiribati, Marshall Islands, Micronesia, Palau, Nauru, Tuvalu, French Polynesia, New Caledonia, Cook Islands, and other Pacific island nations.

**DISASTER TYPES:**
- Earthquakes and aftershocks
- Typhoons, cyclones, and tropical storms
- Floods and flash floods
- Volcanic eruptions and activity
- Landslides and mudslides
- Tsunamis
- Droughts (if severe)

**FOR EACH EVENT, INCLUDE:**
- Type of disaster
- Location (country and region)
- Date
- Severity/magnitude
- Impact (casualties, displaced people, damage if available)
- Current status

**IMPORTANT:** 
- Do NOT include any introductory phrases like "I'll search for" or "Let me search"
- Start directly with the disaster summary
- Organize by disaster type
- Use clear section headers
- Format with markdown"""
        }]
    )
    
    # Extract the summary
    summary = response.choices[0].message.content
    
    # Remove common introductory phrases that GPT might add
    intro_phrases = [
        "I'll search for",
        "Let me search for",
        "I'll look for",
        "Let me look for",
        "I will search",
        "Let me find",
        "I'll gather",
        "Based on my search",
        "After searching",
        "Here is",
        "Here's"
    ]
    
    lines = summary.split('\n')
    cleaned_lines = []
    skip_line = False
    
    for line in lines:
        # Skip lines that start with common intro phrases
        line_lower = line.lower().strip()
        if any(line_lower.startswith(phrase.lower()) for phrase in intro_phrases):
            skip_line = True
            continue
        
        # Once we hit actual content (headers or substantial text), stop skipping
        if line.strip().startswith('#') or (len(line.strip()) > 50 and skip_line):
            skip_line = False
        
        if not skip_line:
            cleaned_lines.append(line)
    
    summary = '\n'.join(cleaned_lines).strip()
    
    # Add custom header
    custom_header = f"""# SDC Hub Bangkok: Disasters in Southeast Asia & the Pacific
**Report Period:** {week_ago.strftime('%B %d')} - {today.strftime('%B %d, %Y')}

---

"""
    
    summary = custom_header + summary
    
    return summary

def save_summary(summary):
    """Save the summary to a file"""
    timestamp = datetime.now().strftime('%Y-%m-%d')
    filename = f"summaries/summary_{timestamp}.md"
    
    # Create summaries directory if it doesn't exist
    os.makedirs("summaries", exist_ok=True)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(f"Summary saved to {filename}")
    return filename

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
            .content-block {
                margin: 15px 0;
                line-height: 1.8;
            }
            .field {
                margin: 8px 0;
                line-height: 1.7;
            }
            ul {
                padding-left: 25px;
                margin: 10px 0;
                list-style-type: disc;
            }
            li {
                margin-bottom: 8px;
                line-height: 1.7;
            }
            .label {
                color: #c0392b;
                font-weight: bold;
                display: inline;
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
        </style>
    </head>
    <body>
        <div class="container">
    """
    
    # Clean up the markdown text
    lines = markdown_text.split('\n')
    in_list = False
    in_content_block = False
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines
        if not line:
            if in_list:
                html += "</ul>\n"
                in_list = False
            if in_content_block:
                html += "</div>\n"
                in_content_block = False
            i += 1
            continue
        
        # Remove ** markdown
        display_line = line.replace('**', '')
        
        # Headers
        if line.startswith('# '):
            if in_list:
                html += "</ul>\n"
                in_list = False
            if in_content_block:
                html += "</div>\n"
                in_content_block = False
            html += f"<h1>{display_line[2:]}</h1>\n"
        
        elif line.startswith('## '):
            if in_list:
                html += "</ul>\n"
                in_list = False
            if in_content_block:
                html += "</div>\n"
                in_content_block = False
            html += f"<h2>{display_line[3:]}</h2>\n"
        
        elif line.startswith('### '):
            if in_list:
                html += "</ul>\n"
                in_list = False
            if in_content_block:
                html += "</div>\n"
                in_content_block = False
            html += f"<h3>{display_line[4:]}</h3>\n"
        
        # Bullet points (- or *)
        elif line.startswith('- ') or line.startswith('* '):
            if in_content_block:
                html += "</div>\n"
                in_content_block = False
            if not in_list:
                html += "<ul>\n"
                in_list = True
            
            item = display_line[2:]
            html += f"<li>{item}</li>\n"
        
        # Horizontal rule
        elif line.startswith('---'):
            if in_list:
                html += "</ul>\n"
                in_list = False
            if in_content_block:
                html += "</div>\n"
                in_content_block = False
            html += "<hr>\n"
        
        # Lines with colons (field labels)
        elif ':' in display_line and not display_line.startswith('http'):
            parts = display_line.split(':', 1)
            if len(parts) == 2 and len(parts[0]) < 40:
                if in_list:
                    html += "</ul>\n"
                    in_list = False
                if not in_content_block:
                    html += '<div class="content-block">\n'
                    in_content_block = True
                
                label = parts[0].strip()
                value = parts[1].strip()
                
                if value:
                    html += f'<div class="field"><span class="label">{label}:</span> {value}</div>\n'
                else:
                    html += f'<div class="field"><span class="label">{label}:</span></div>\n'
            else:
                if in_list:
                    html += "</ul>\n"
                    in_list = False
                if not in_content_block:
                    html += '<div class="content-block">\n'
                    in_content_block = True
                html += f'<div class="field">{display_line}</div>\n'
        
        # Regular text
        else:
            if in_list:
                html += "</ul>\n"
                in_list = False
            if not in_content_block:
                html += '<div class="content-block">\n'
                in_content_block = True
            html += f'<div class="field">{display_line}</div>\n'
        
        i += 1
    
    if in_list:
        html += "</ul>\n"
    if in_content_block:
        html += "</div>\n"
    
    # Close the HTML
    html += """
        <div class="footer">
            <p><strong>📊 Automated Weekly Report</strong></p>
            <p>Generated by Disaster Summary Agent • Powered by OpenAI GPT-4</p>
            <p style="font-size: 12px; margin-top: 10px;">Data compiled from multiple news and disaster monitoring sources</p>
        </div>
        </div>
    </body>
    </html>
    """
    
    return html

def send_email(summary):
    """Send summary via email with HTML formatting"""
    sender = os.environ.get("EMAIL_SENDER")
    password = os.environ.get("EMAIL_PASSWORD")
    recipients_str = os.environ.get("EMAIL_RECIPIENT")
    
    print(f"Email config check:")
    print(f"  Sender configured: {bool(sender)}")
    print(f"  Password configured: {bool(password)}")
    print(f"  Recipients configured: {bool(recipients_str)}")
    
    if not all([sender, password, recipients_str]):
        print("❌ Email credentials not configured, skipping email send")
        return
    
    # Split recipients by comma and clean whitespace
    recipients = [email.strip() for email in recipients_str.split(',')]
    
    print(f"Attempting to send email from {sender} to {len(recipients)} recipient(s): {', '.join(recipients)}")
    
    # Convert Markdown to HTML
    html_content = markdown_to_html(summary)
    
    # Create message with both plain text and HTML
    msg = MIMEMultipart('alternative')
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    msg['Subject'] = f'🌏 SDC Hub Bangkok: SE Asia & Pacific Disaster Summary - {datetime.now().strftime("%B %d, %Y")}'
    
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
        print(f"✅ Email sent successfully to: {', '.join(recipients)}")
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        print("Make sure you're using an App Password, not your regular Gmail password")
    except Exception as e:
        print(f"❌ Failed to send email: {type(e).__name__}: {e}")

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

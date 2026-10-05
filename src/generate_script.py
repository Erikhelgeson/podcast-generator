import imaplib
import email
import os
from datetime import datetime
import urllib.request
from bs4 import BeautifulSoup
from openai import OpenAI

# --- YOUR LOGIN & API DETAILS ---
EMAIL_ADDRESS = "erikrhelgeson@gmail.com"  # Replace with your podcast email
APP_PASSWORD = "sypz mrlg btsy drbu"          # Replace with your App Password
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")                # Replace with your OpenAI API Key

# Initialize OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# ----------------------------------------------------
# 1. LIVE SPORTS HEADLINES FETCHER
# ----------------------------------------------------
def fetch_sports_news():
    print("Fetching daily sports headlines...")
    try:
        url = "https://sports.yahoo.com/rss/"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=8) as response:
            xml_data = response.read()
        soup = BeautifulSoup(xml_data, "xml")
        items = soup.find_all("item")
        
        sports_bulletin = []
        for item in items[:6]:
            title = item.title.text if item.title else ""
            desc = item.description.text if item.description else ""
            clean_desc = BeautifulSoup(desc, "html.parser").get_text()
            sports_bulletin.append(f"- {title}: {clean_desc}")
            
        return "\n".join(sports_bulletin)
    except Exception as e:
        print(f"Note: Sports feed temporarily offline ({e}). AI will generate using general knowledge.")
        return "Focus on the latest major sports championships, trades, or global events."

# ----------------------------------------------------
# 2. COUNTRY OF THE DAY SELECTOR
# ----------------------------------------------------
COUNTRIES_POOL = [
    {"name": "Germany", "leader": "Chancellor Olaf Scholz", "history": "Transitioning away from cheap Russian gas, struggling with high energy costs, and restructuring its manufacturing sectors.", "strengths": "Highly skilled workforce, premium engineering exports, and low public debt.", "weaknesses": "Extreme energy dependency, rapidly aging workforce, and slow digital infrastructure adoption."},
    {"name": "Taiwan", "leader": "President Lai Ching-te", "history": "Solidified its position as the undisputed capital of global advanced microchip manufacturing (TSMC) while navigating diplomatic pressure from China.", "strengths": "Near-monopoly on high-end computer chips, highly educated workforce, and robust trade network.", "weaknesses": "Geopolitical vulnerability, 97%+ dependency on imported energy, and exceptionally low birth rates."},
    {"name": "India", "leader": "Prime Minister Narendra Modi", "history": "Underwent massive digital infrastructure rollouts, rapid economic growth, and positioned itself as a major manufacturing alternative.", "strengths": "Enormous young workforce, dominant IT and software export sector, and rapidly growing middle class.", "weaknesses": "Rigid bureaucratic regulations, high youth unemployment, and infrastructure gaps in rural areas."},
    {"name": "Japan", "leader": "Prime Minister Shigeru Ishiba", "history": "Recently began climbing out of a 30-year battle with economic deflation. Faced a historically weak Yen which boosted exports but made imported fuel expensive.", "strengths": "Global leader in high-tech manufacturing, immense foreign investments, and high social and economic stability.", "weaknesses": "The highest debt-to-GDP ratio in the developed world and severe population shrinkage."},
    {"name": "Mexico", "leader": "President Claudia Sheinbaum", "history": "Benefited from a massive 'nearshoring' boom as US companies moved manufacturing hubs out of China to Mexico under the USMCA trade agreement.", "strengths": "Direct land borders and free trade with the US, highly competitive factory sector, and a large young labor pool.", "weaknesses": "Internal security challenges, underfunded energy grids, and water scarcity."},
    {"name": "Brazil", "leader": "President Luiz Inácio Lula da Silva", "history": "Navigated major political swings while transforming into a global agricultural powerhouse, leading the world in soybean, beef, and coffee exports.", "strengths": "Incredible natural resources, a grid powered by over 80% renewable energy, and agricultural dominance.", "weaknesses": "Extremely complex tax systems, high government fiscal deficits, and transport/logistics bottlenecks."},
    {"name": "United Kingdom", "leader": "Prime Minister Keir Starmer", "history": "Spanned a decade adjusting to the post-Brexit trade realities with Europe, enduring political shifts, low productivity, and high cost of living shocks.", "strengths": "Global financial powerhouse (London), elite university research, and a world-class services economy.", "weaknesses": "Slow productivity growth, trade frictions with neighboring EU markets, and high national debt."},
    {"name": "China", "leader": "President Xi Jinping", "history": "Transitioned from double-digit explosive growth to slower, high-tech manufacturing. Experienced a severe property and real-estate debt crisis and worsening trade wars.", "strengths": "Unmatched global manufacturing supply chains, absolute dominance in green tech (EVs, batteries, solar).", "weaknesses": "Massive property sector debt, a shrinking demographic workforce, and heavy local government debt."},
    {"name": "Canada", "leader": "Prime Minister Justin Trudeau", "history": "Experienced a massive housing price boom and subsequent housing affordability crisis, while using high immigration to drive population growth.", "strengths": "Abundant critical minerals, oil, timber, and fresh water; highly educated workforce.", "weaknesses": "Low corporate productivity investment, housing bubble vulnerabilities, and high household debt."},
    {"name": "South Korea", "leader": "President Yoon Suk-yeol", "history": "Saw explosive global growth of K-culture while its tech conglomerates (Samsung, SK Hynix) battled for global semiconductor supremacy.", "strengths": "Massive corporate spending on Research & Development, global tech dominance, and disciplined labor force.", "weaknesses": "The lowest birth rate in the world and extreme economic exposure to global computer chip market cycles."},
    {"name": "Australia", "leader": "Prime Minister Anthony Albanese", "history": "Successfully avoided major economic recessions for decades on the back of an unprecedented raw materials export boom.", "strengths": "Immense mineral and energy wealth, stable banking sector, and robust national sovereign wealth.", "weaknesses": "Economic vulnerability to climate events, housing affordability stress, and heavy export concentration on China."},
    {"name": "Saudi Arabia", "leader": "Crown Prince Mohammed bin Salman", "history": "Launched the massive 'Vision 2030' plan to transition the kingdom's economy away from oil dependency, deploying trillions via its Sovereign Wealth Fund.", "strengths": "The world's lowest oil extraction costs, vast cash reserves, and highly strategic trade geography.", "weaknesses": "Still heavily dependent on oil revenues to balance budgets and high public-sector salary costs."},
    {"name": "South Africa", "leader": "President Cyril Ramaphosa", "history": "Struggled with severe, rolling electrical grid blackouts (loadshedding) that stunted growth, leading to historic coalition politics.", "strengths": "Deep reserves of critical minerals (platinum, gold, chromium) and the most advanced financial system in Africa.", "weaknesses": "Infrastructure bottlenecks (railway and power grids) and high youth unemployment (over 30%)."},
    {"name": "Turkey", "leader": "President Recep Tayyip Erdoğan", "history": "Endured years of runaway inflation due to unconventional interest rate policies, followed by a sudden pivot back to traditional economic principles.", "strengths": "Highly strategic location bridging Europe and Asia, dynamic private manufacturing sector, and young population.", "weaknesses": "Unstable currency (Lira), high foreign debt, and elevated inflation."},
    {"name": "Indonesia", "leader": "President Prabowo Subianto", "history": "Instituted a famous 'downstreaming' policy—banning raw metal exports to force foreign companies to build factories locally.", "strengths": "The world's largest nickel reserves and a massive, young, tech-savvy population.", "weaknesses": "Infrastructural challenges across 17,000 islands and high vulnerability to natural disasters."},
    {"name": "Switzerland", "leader": "The Rotating Federal Council", "history": "Maintained rock-solid inflation and growth, but experienced a massive shakeup when Credit Suisse collapsed and was absorbed by UBS.", "strengths": "The Swiss Franc safe-haven status, global hub for pharmaceutical and financial giants, and top-tier innovation.", "weaknesses": "Severe banking concentration (UBS is now larger than the entire Swiss annual GDP)."},
    {"name": "France", "leader": "President Emmanuel Macron", "history": "Faced domestic labor protests over retirement reforms while launching a major nuclear power renaissance and green tech manufacturing drive.", "strengths": "A highly stable, low-carbon electricity grid powered 70%+ by nuclear energy, and unmatched luxury export giants (LVMH).", "weaknesses": "Very high public debt levels and rigid labor regulations."},
    {"name": "Italy", "leader": "Prime Minister Giorgia Meloni", "history": "Navigated chronic slow GDP growth while receiving the largest share of the European Union's post-pandemic recovery fund.", "strengths": "World-famous industrial manufacturing cluster (machinery, fashion, food) and high family savings rates.", "weaknesses": "One of the oldest populations in the world and high sovereign debt (around 140% of GDP)."},
    {"name": "Russia", "leader": "President Vladimir Putin", "history": "Shifted into a highly state-directed 'war economy' following severe Western sanctions, diverting its entire commodity trade toward India and China.", "strengths": "Vast reserves of oil, gas, metals, and wheat; self-sufficient defense industry.", "weaknesses": "Deep international isolation, labor shortages, and complete long-term reliance on China for technology imports."},
    {"name": "United States", "leader": "The President", "history": "Pioneered the tech and AI boom while implementing massive subsidies to bring semiconductor and green factories back home.", "strengths": "The world's reserve currency (US Dollar), global tech and financial dominance, and complete energy self-sufficiency.", "weaknesses": "Deep political polarization and an enormous, expanding national debt."}
]

def get_country_of_the_day():
    day_of_year = datetime.now().timetuple().tm_yday
    index = day_of_year % len(COUNTRIES_POOL)
    return COUNTRIES_POOL[index]

# ----------------------------------------------------
# 3. CLEAN HTML TEXT
# ----------------------------------------------------
def clean_html(html_body):
    soup = BeautifulSoup(html_body, "html.parser")
    for element in soup(["script", "style", "a"]):
        element.decompose()
    return soup.get_text(separator="\n").strip()

# ----------------------------------------------------
# 4. FETCH UNREAD EMAILS
# ----------------------------------------------------
def fetch_unread_emails():
    print("Connecting to secure email server...")
    collected_articles = []
    
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(EMAIL_ADDRESS, APP_PASSWORD)
        mail.select("inbox")
        
        status, messages = mail.search(None, "UNSEEN")
        if status != "OK" or not messages or not messages[0]:
            print("No unread emails found.")
            return []
            
        email_ids = messages[0].split()
        for email_id in email_ids:
            status, msg_data = mail.fetch(email_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1]) 
                    subject = msg["Subject"] or "No Subject"
                    print(f"-> Processing: '{subject}'")
                    
                    raw_body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.is_multipart():
                                continue
                            if part.get_content_type() == "text/html":
                                payload = part.get_payload(decode=True)
                                if payload:
                                    raw_body = payload.decode(msg.get_content_charset() or 'utf-8', errors='ignore')
                                    break
                    else:
                        payload = msg.get_payload(decode=True)
                        if payload:
                            raw_body = payload.decode(msg.get_content_charset() or 'utf-8', errors='ignore')
                            
                    # Extract sender using standard library with unique local name to avoid scope errors
                    from_header = msg["From"] or "Unknown"
                    name = ""
                    addr = from_header
                    if "<" in from_header and ">" in from_header:
                        parts_header = from_header.split("<", 1)
                        name = parts_header[0].strip().strip('"')
                        addr = parts_header[1].split(">", 1)[0].strip()
                    
                    addr_lower = addr.lower()
                    friendly_source = "an email newsletter"
                    if "nytimes" in addr_lower:
                        friendly_source = "NYT"
                    elif "economist" in addr_lower:
                        friendly_source = "the Economist"
                    elif "peel" in addr_lower:
                        friendly_source = "the Daily Peel"
                    elif "barrons" in addr_lower or "barron" in addr_lower:
                        friendly_source = "Barron's"
                    elif "wsj" in addr_lower or "wallstreetjournal" in addr_lower:
                        friendly_source = "the Wall Street Journal"
                    elif "tufts" in addr_lower:
                        friendly_source = "Tufts Newsletter"
                    elif name:
                        friendly_source = name
                        
                    clean_text = clean_html(raw_body)
                    collected_articles.append(f"METADATA_SOURCE: {friendly_source}\nSource Email: {subject}\n\n{clean_text}")
                    
        mail.logout()
        return collected_articles
        
    except Exception as e:
        print(f"Error fetching email: {e}")
        return []


def generate_podcast_script(articles_text, sports_news, country_of_day):
    print("\nDrafting conversational script with OpenAI...")
    
    # Parse out sources and clean the context for GPT
    sources = []
    cleaned_articles = []
    for art in articles_text:
        if art.startswith("METADATA_SOURCE: "):
            parts = art.split("\n", 1)
            source_name = parts[0].replace("METADATA_SOURCE: ", "").strip()
            sources.append(source_name)
            body_text = parts[1] if len(parts) > 1 else ""
            cleaned_articles.append(body_text)
        else:
            sources.append("an email newsletter")
            cleaned_articles.append(art)
            
    news_context = "\n\n=======================\n\n".join(cleaned_articles)
    
    # Generate the dynamic intro sentence
    num_emails = len(sources)
    if num_emails == 0:
        intro_phrase = "We don't have any new email newsletters today, but we still have an exciting show for you!"
    elif num_emails == 1:
        intro_phrase = f"You got one email today, from {sources[0]}."
    elif num_emails == 2:
        intro_phrase = f"You got two emails today, one from {sources[0]} and one from {sources[1]}."
    else:
        source_list_str = ", ".join([f"one from {s}" for s in sources[:-1]]) + f", and one from {sources[-1]}"
        intro_phrase = f"You got {num_emails} emails today, {source_list_str}."
        
    intro_sentence = f"{intro_phrase} Here is our show for today!"
    
    system_instruction = (
        "You are an elite, highly professional podcast writer for a daily news show.\n\n"
        "Your task is to draft a natural, high-density, highly analytical 15-minute conversation between "
        "two co-hosts: ALEX and TAYLOR. They discuss daily news, sports, and an economic country spotlight.\n\n"
        "HOST PERSONALITIES AND VOICES:\n"
        "1. ALEX (Male Voice): The primary anchor. He is highly analytical, professional, and carries a serious, "
        "academic tone when explaining geopolitics, macroeconomics, or straight international news. He also delivers "
        "the sports segment. He sounds like a top-tier financial or geopolitical analyst.\n"
        "2. TAYLOR (Female Voice): The high-energy, relatable, and deeply curious co-host. She is the listener's champion, "
        "asking the right questions, reacting naturally, translating complex jargon into plain English, and providing context.\n\n"
        "IMPORTANT WRITING RULES (CRITICAL FOR RUNTIME, DEPTH AND QUALITY):\n"
        "1. THE OPENING: You MUST open the show by having ALEX or TAYLOR say exactly: "
        f"\"{intro_sentence}\" followed by a warm, brief greeting.\n"
        "2. ERIK'S PHILOSOPHIC CONCEPT OF THE DAY: Immediately after the warm opening greeting (within the first 45 seconds of the show), "
        "introduce a 2-minute segment called 'Erik's Philosophic Concept of the Day'.\n"
        "   - Select a profound, authentic philosophy quote or concept from a great thinker (e.g., Nietzsche, Descartes, Freud, Marcus Aurelius, Kant, Plato, Socrates, etc.).\n"
        "   - ALEX must slowly and clearly deliver the quote/concept, explaining who said it, and when/where.\n"
        "   - TAYLOR must then explain the concept's context, how it is interpreted, how people think about it, and specifically how the listener can apply it to everyday life and use it in normal daily conversations to build their philosophical understanding.\n"
        "   - Transition seamlessly from this segment into the daily news emails.\n"
        "3. NO FACTUAL FABRICATION: Never invent fake facts, fake names, fake statistics, or fake events. All news details "
        "must be strictly grounded in the provided email context. (The only exception is the philosophic segment, where you use real-world philosophical quotes/teachings).\n"
        "4. THE TURN RULE (CRITICAL FOR LENGTH): For EACH individual email newsletter topic (even secondary stories), ALEX and TAYLOR must engage in at least 3 substantial turns each (6 total back-and-forth exchanges per story).\n"
        "5. THE PARAGRAPH RULE: No short, one-sentence transition remarks or simple agreements (e.g. \"Exactly!\" or \"That's crazy!\"). Every single turn by ALEX or TAYLOR must be a fully realized, substantive paragraph of 3 to 5 sentences packed with context, explanation, or debate.\n"
        "6. THE 'WHY' RULE (DEEP CONCEPTUAL ANALYSIS): For every news item, co-hosts must define key terms, provide historical/structural context, and explore future implications. Never just read a headline and move on. Draw on established, accurate real-world economic and historical knowledge to educate the listener.\n"
        "7. EXHAUSTIVE DISCUSSION OF SUB-STORIES: Newsletters often contain multiple secondary articles, side-bars, or bullet points. Do not skip these! Systematically walk through the secondary stories, discussing their economic and strategic meanings. Turn a simple email into a comprehensive news roundup.\n"
        "8. DOUBLE-LENGTH COUNTRY SPOTLIGHT: The economic country spotlight segment must be at least twice as long as other segments (at least 5 substantial turns each co-host, or 10 total exchanges). They must deeply analyze the country's economic shifts, political structure, and public sentiment toward the current leader/politician in charge.\n"
        "9. DIALOGUE FLOW: Ensure turns are substantial and balanced. ALEX and TAYLOR should actively converse: teaching each other, offering counterpoints, asking clarifying questions, and building on each other's ideas rather than just reading lists of facts. Aim for a comprehensive, highly informative script of 2,200 to 2,500 words to ensure a full, deep-dive 15-minute show when multiple emails are present.\n"
        "10. AUDIENCE: Speak to an intelligent, busy professional. Keep the tone sophisticated, engaging, and professional."
    )
    
    user_prompt = (
        f"--- TODAY'S DAILY NEWS EMAILS ---\n{news_context}\n\n"
        f"--- DAILY SPORTS NEWS ---\n{sports_news}\n\n"
        f"--- ERIK'S ECONOMIC COUNTRY OF THE DAY ---\n"
        f"Country: {country_of_day['name']}\n"
        f"Leader: {country_of_day['leader']}\n"
        f"10-Year Political/Economic History: {country_of_day['history']}\n"
        f"Core Strengths: {country_of_day['strengths']}\n"
        f"Core Weaknesses: {country_of_day['weaknesses']}"
    )
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ]
        )
        script_text = response.choices[0].message.content
        return script_text
    except Exception as e:
        print(f"Error generating script: {e}")
        return None
def generate_audio_podcast(script_text, output_path):
    print("Generating AI voices for Alex and Taylor (this may take 2-3 minutes)...")
    import re
    
    if not script_text or str(script_text).strip().lower() == "none":
        print("Error: Script text is empty or None. Cannot generate audio.")
        return
        
    lines = script_text.splitlines()
    audio_chunks = []
    
    for idx, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        # Robustly parse speaker and spoken text using string manipulation (immune to regex errors)
        clean = line.replace("**", "").replace("*", "").replace("__", "").replace("_", "").strip()
        upper_clean = clean.upper()
        speaker = None
        text = None
        
        if upper_clean.startswith("ALEX"):
            colon_idx = clean.find(":")
            if colon_idx != -1:
                speaker_part = clean[:colon_idx].upper()
                if "ALEX" in speaker_part:
                    speaker = "ALEX"
                    text = clean[colon_idx+1:].strip()
        elif upper_clean.startswith("TAYLOR"):
            colon_idx = clean.find(":")
            if colon_idx != -1:
                speaker_part = clean[:colon_idx].upper()
                if "TAYLOR" in speaker_part:
                    speaker = "TAYLOR"
                    text = clean[colon_idx+1:].strip()
                    
        if not speaker or not text:
            continue
            
        # Clean up text (stage directions like [chuckles] or parentheses)
        text = re.sub(r"\[.*?\]", "", text)
        text = re.sub(r"\(.*?\)", "", text)
        text = text.strip()
        
        if not text:
            continue
            
        voice = "onyx" if speaker == "ALEX" else "shimmer"
        
        try:
            response = client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text
            )
            audio_chunks.append(response.content)
        except Exception as e:
            print(f"Error generating audio chunk {idx}: {e}")
            
    if audio_chunks:
        # Save as a single concatenated MP3 binary file
        try:
            with open(output_path, "wb") as f:
                for chunk in audio_chunks:
                    f.write(chunk)
            print("Success! Spoken audio saved directly to iCloud!")
        except Exception as e:
            print(f"Error saving final MP3 file: {e}")
    else:
        print("Error: No audio chunks were generated. Please check that speaker formatting matches 'ALEX:' or 'TAYLOR:'.")


def main():
    print("--- Starting Daily Podcast Script & Audio Generator ---")
    
    # 1. Fetch Emails
    articles = fetch_unread_emails()
    if not articles:
        print("No articles to process. Make sure you have unread emails in your inbox!")
        return
        
    # 2. Fetch Sports News
    sports = fetch_sports_news()
    
    # 3. Rotate Country of the Day
    country = get_country_of_the_day()
    print(f"Today's Economic Country Spotlight: {country['name']}")



    
    # 4. Generate AI Script
    script = generate_podcast_script(articles, sports, country)
    if not script:
        print("Failed to generate script.")
        return
        
    # 5. Define Output Locations (Documents and iCloud Drive)
    date_str = datetime.now().strftime("%Y_%m_%d")
    
    # Text Draft Backup Folder
    text_dir = os.path.expanduser("~/Documents/personal/Daily podcasts")
    os.makedirs(text_dir, exist_ok=True)
    text_path = os.path.join(text_dir, f"podcast_script_{date_str}.txt")
    
    # iCloud MP3 Output Folder
    icloud_dir = os.path.expanduser("~/Library/Mobile Documents/com~apple~CloudDocs/Daily Podcasts")
    os.makedirs(icloud_dir, exist_ok=True)
    mp3_path = os.path.join(text_dir, f"podcast_{date_str}.mp3")
    
    # Save Text Draft
    try:
        with open(text_path, "w", encoding="utf-8") as file:
            file.write(script)
        print(f"Saved text backup to: {text_path}")
    except Exception as e:
        print(f"Could not save text backup: {e}")
        
    # 6. Generate Voice Audio & Save to iCloud
    generate_audio_podcast(script, mp3_path)

if __name__ == "__main__":
    main()
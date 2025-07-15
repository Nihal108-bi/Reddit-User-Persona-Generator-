
import argparse
import os
from dotenv import load_dotenv

from persona.reddit_client import RedditClient
from persona.generator import PersonaGenerator
from persona.parser import PersonaParser
from persona.html_exporter import HTMLExporter

load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="Generate a detailed user persona from a Reddit profile.")
    parser.add_argument("username", type=str, help="The Reddit username or the full URL of the user's profile.")
    args = parser.parse_args()

    if "reddit.com/user/" in args.username:
        username = args.username.strip("/").split("/")[-1]
    else:
        username = args.username

    print(f"🔍 Starting persona generation for user: {username}")
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    reddit_client = RedditClient()
    persona_generator = PersonaGenerator(api_key=os.getenv("GOOGLE_API_KEY"))
    persona_parser = PersonaParser()
    html_exporter = HTMLExporter()

    # Geting user object and their avatar URL
    user_data = reddit_client.get_user(username)
    if not user_data:
        return

    user, avatar_url = user_data

    activity = reddit_client.get_user_activity(user)
    if not activity:
        print(f"No public activity found for user '{username}'. Cannot generate a persona.")
        return

    print(f"✅ Found {len(activity)} activities. Generating persona with Gemini...")
    persona_text = persona_generator.generate(username, activity)

    all_sources = sorted(list(set(item["permalink"] for item in activity)))
    sources_str = "\n".join([f"{i+1}. {url}" for i, url in enumerate(all_sources)])
    placeholder = "(This section will be populated by the application later, do not add anything here.)"
    
    if placeholder in persona_text:
        persona_text = persona_text.replace(placeholder, sources_str)
    else:
        persona_text += f"\n\nCITED SOURCES\n-------------\n{sources_str}"

    txt_path = os.path.join(output_dir, f"{username}_persona.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(persona_text)
    print(f"✅ Successfully saved text persona with citations to {txt_path}")

    try:
        print("Parsing the persona to generate the HTML file...")
        # Passing the avatar_url to the parser
        parsed_persona = persona_parser.parse(username, persona_text, avatar_url)
        parsed_persona["sources"] = all_sources

        html_path = os.path.join(output_dir, f"{username}_persona.html")
        html_exporter.export(parsed_persona, html_path)
        print(f"✅ Successfully exported HTML persona to {html_path}")
    except Exception as e:
        print(f"❌ Failed to parse and export HTML persona. Error: {e}")

if __name__ == "__main__":
    main()
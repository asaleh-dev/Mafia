import os
import json
import requests
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "google/gemini-2.5-pro-exp-03-25:free") # Default fallback model
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

def generate_mafia_story(num_players):
    """
    Generate a Mafia game story using the OpenRouter API.

    Args:
        num_players (int): Number of players in the game

    Returns:
        dict: JSON response containing story, characters, and clues
    """
    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY.strip() == "":
        raise ValueError("OpenRouter API key not found or empty. Please check your .env file.")

    # Check if the API key looks valid (basic format check)
    if not OPENROUTER_API_KEY.startswith("sk-or-"):
        print(f"Warning: OpenRouter API key doesn't match expected format. Key starts with: {OPENROUTER_API_KEY[:10]}...")
        # Continue anyway, as the format might change in the future

    # Add a timestamp to ensure uniqueness in each generation
    import time
    timestamp = int(time.time())

    prompt = f"""أنت مؤلف قصص بوليسية محترف باللهجة المصرية. اكتب قصة جريمة قتل غامضة ومعقدة (بحد أقصى 2000 كلمة) مع {num_players} شخصيات، وضحية، و3 أدلة ذكية تتعلق بالجريمة.

مهم جداً: اصنع قصة معقدة مع حبكة غير متوقعة وتحويلات مفاجئة. اجعل القصة صعبة الحل بحيث:

1. كل الشخصيات عندها دوافع محتملة للقتل، وليس فقط القاتل الحقيقي
2. كل الشخصيات عندها علاقات معقدة مع الضحية (مش مجرد صديق أو عدو)
3. كل الشخصيات عندها أسرار خاصة ممكن تخليهم يبانوا مشبوهين
4. ضع معلومات مضللة وأدلة كاذبة تشتت الانتباه عن القاتل الحقيقي
5. اجعل الأدلة غامضة وتحتاج تفكير عميق لربطها بالقاتل

لكل شخصية، قدم:
1. اسم مميز وكامل
2. وصف مفصل (العمر، المظهر، المهنة)
3. سمات الشخصية وطباعها
4. علاقة معقدة ومتناقضة مع الضحية (مثلاً: صديق ظاهرياً لكن بينهم توتر خفي)
5. دوافع محتملة للقتل (لكل الشخصيات، مش بس القاتل)
6. أسرار أو ماضي غامض

الأدلة:
- الدليل الأول: غامض ويمكن تفسيره بأكثر من طريقة
- الدليل الثاني: يشير لعدة أشخاص محتملين
- الدليل الثالث: يشير للقاتل الحقيقي لكن بطريقة ذكية وغير مباشرة

أضف عنصر مفاجأة أو تحول درامي في القصة (مثل: الضحية كان عنده أسرار خطيرة، أو علاقات سرية، أو خطط انتقامية). لا تضيف اي شئ جنسي في القصة.

تذكر: هذه قصة جديدة تماماً (رقم فريد: {timestamp})، لا تكرر قصصاً سابقة.

Give your response in this JSON format (but write the content in Egyptian Arabic dialect):

{{
  "main_story": "قصة معقدة عن جريمة قتل باللهجة المصرية مع حبكة غير متوقعة وتحويلات مفاجئة",
  "killed_character_name": "اسم الضحية",
  "players": [
    {{
      "character_name": "اسم الشخصية 1",
      "character_description": "وصف مفصل للشخصية يشمل العمر والمظهر والمهنة وسمات الشخصية وعلاقتها المعقدة بالضحية والدوافع المحتملة للقتل والأسرار الخاصة",
      "is_mafia": false
    }},
    ... (there must be exactly {num_players} characters)
  ],
  "clues": [
    "الدليل الأول: دليل غامض يمكن تفسيره بأكثر من طريقة",
    "الدليل الثاني: دليل يشير لعدة أشخاص محتملين",
    "الدليل الثالث: دليل ذكي يشير للقاتل الحقيقي بطريقة غير مباشرة"
  ]
}}

It is critical that your response is valid JSON that matches this format exactly. Do not include any text before or after the JSON object. Make sure all text is in Egyptian Arabic dialect (not formal Arabic)."""

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": OPENROUTER_MODEL or "google/gemini-2.5-pro-exp-03-25:free",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 2000,
        "temperature": 0.9,
        "response_format": {"type": "json_object"}  # Request JSON response specifically
    }

    try:
        response = requests.post(OPENROUTER_BASE_URL, headers=headers, json=data)

        # Handle HTTP errors more gracefully
        if response.status_code == 401:
            print("Authentication error: The OpenRouter API key is invalid or expired.")
            print("Please update your .env file with a valid API key.")
            raise ValueError("Invalid or expired OpenRouter API key")
        elif response.status_code == 429:
            print("Rate limit exceeded: Too many requests to OpenRouter API.")
            raise ValueError("OpenRouter API rate limit exceeded")
        elif response.status_code != 200:
            print(f"OpenRouter API returned error status code: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            raise ValueError(f"OpenRouter API error: {response.status_code}")

        response_data = response.json()

        if "choices" not in response_data or not response_data["choices"]:
            raise ValueError(f"Invalid API response structure: {response_data}")

        content = response_data["choices"][0]["message"]["content"]

        # Debug response
        print(f"API Response: {content[:100]}...")

        # Extract JSON from content
        story_data = extract_json_from_content(content)

        # Validate the response structure
        validate_story_data(story_data, num_players)

        return story_data

    except requests.exceptions.RequestException as e:
        print(f"Network error connecting to OpenRouter API: {str(e)}")
        raise ConnectionError(f"Failed to connect to OpenRouter API: {str(e)}")
    except (json.JSONDecodeError, ValueError) as e:
        # Print full error and API response if available
        print(f"Error: {str(e)}")
        if 'content' in locals():
            print(f"API Response content: {content[:500]}")
        elif 'response' in locals() and hasattr(response, 'text'):
            print(f"API Response text: {response.text[:500]}")
        else:
            print("No API response content available")

        raise ValueError(f"Error processing API response: {str(e)}")

def extract_json_from_content(content):
    """
    Extract valid JSON from the API response content using multiple strategies.

    Args:
        content (str): The content from the API response

    Returns:
        dict: Extracted JSON data

    Raises:
        ValueError: If no valid JSON could be extracted
    """
    # Strategy 1: Check if it's already valid JSON
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass

    # Strategy 2: Try to extract from code blocks
    json_match = re.search(r'```(?:json)?\s*(.*?)\s*```', content, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    # Strategy 3: Try to find JSON-like patterns with curly braces
    json_match = re.search(r'({[\s\S]*})', content, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    # Strategy 4: Try removing any non-JSON text at the beginning and end
    content = content.strip()
    start_idx = content.find('{')
    end_idx = content.rfind('}')

    if start_idx != -1 and end_idx != -1:
        try:
            return json.loads(content[start_idx:end_idx+1])
        except json.JSONDecodeError:
            pass

    # If we reached here, we couldn't extract valid JSON
    raise ValueError(f"Couldn't extract valid JSON from the API response. Response: {content[:200]}...")

def validate_story_data(data, num_players):
    """
    Validate that the story data has the expected structure and content.

    Args:
        data (dict): The story data to validate
        num_players (int): The number of players in the game

    Raises:
        ValueError: If the story data is invalid
    """
    # Check essential fields
    required_fields = ["main_story", "killed_character_name", "players", "clues"]
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")

    # Check player count
    if len(data["players"]) != num_players:
        # Try to fix by adding more players if needed
        if len(data["players"]) < num_players:
            # Clone the last player to fill the gap
            last_player = data["players"][-1].copy()
            last_player["character_name"] = f"Extra Character {len(data['players']) + 1}"

            while len(data["players"]) < num_players:
                data["players"].append(last_player.copy())

            print(f"Warning: Added {num_players - len(data['players'])} missing players to match required count")
        elif len(data["players"]) > num_players:
            # Truncate extra players
            data["players"] = data["players"][:num_players]
            print(f"Warning: Truncated player list to match required count of {num_players}")

    # Check clues
    if len(data["clues"]) != 3:
        if len(data["clues"]) < 3:
            # Add generic clues if missing
            while len(data["clues"]) < 3:
                data["clues"].append(f"Additional clue {len(data['clues']) + 1} pointing to the killer.")
            print("Warning: Added missing clues to match required count of 3")
        elif len(data["clues"]) > 3:
            # Keep only the first 3 clues
            data["clues"] = data["clues"][:3]
            print("Warning: Truncated clues to match required count of 3")

    # Ensure all players have the required fields
    for i, player in enumerate(data["players"]):
        if "character_name" not in player:
            player["character_name"] = f"Character {i+1}"
        if "character_description" not in player:
            player["character_description"] = f"A mysterious person connected to the case."
        if "is_mafia" not in player:
            player["is_mafia"] = False  # Default to civilian
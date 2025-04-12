import random
import time
from .openrouter import generate_mafia_story
import traceback

def generate_game_story(num_players):
    """
    Generate a story for the game with the given number of players.

    Args:
        num_players (int): Number of players in the game

    Returns:
        dict: The generated story data
    """
    # Validate player count
    if num_players < 3:
        raise ValueError("Minimum 3 players required for a Mafia game")

    # Check if we have a valid API key before attempting to call the API
    from .openrouter import OPENROUTER_API_KEY

    # If no API key is available or it's empty, use fallback immediately
    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY.strip() == "":
        print("No valid OpenRouter API key found. Using fallback story generator.")
        return generate_fallback_story(num_players)

    # Try to generate the story using OpenRouter API
    try:
        story_data = generate_mafia_story(num_players)
        return story_data
    except Exception as e:
        print(f"Error generating story from API: {str(e)}")
        print(traceback.format_exc())
        # Fall back to a pre-defined template if API fails
        return generate_fallback_story(num_players)

def generate_fallback_story(num_players):
    """
    Generate a fallback story when the API call fails.

    Args:
        num_players (int): Number of players in the game

    Returns:
        dict: A basic story template
    """
    print("Using fallback story generator")

    # Create detailed character templates with more information
    character_templates = [
        {"name": "الدكتور", "desc": "طبيب عمره 45 سنة، طويل وبشرته بيضة، بيلبس نظارة طبية دايماً. شخصيته هادية وبيفكر كتير قبل ما يتكلم. كان بيعالج الضحية من مرض خطير، وكان عارف أسرار صحية عن الضحية ممكن تضره لو انتشرت. عنده دافع محتمل إنه يخاف الضحية يفضح إنه كان بيعالجه بطريقة غلط."},
        {"name": "المحامي", "desc": "محامي شاطر عمره 50 سنة، قصير وبدين، دايماً بيلبس بدلة أنيقة. شخصيته قوية وبيحب يسيطر على اللي حواليه. كان المسؤول عن تنفيذ وصية الضحية، وكان عارف كل تفاصيل ثروته. عنده دافع محتمل إنه يعدل في الوصية لصالحه."},
        {"name": "الشيف", "desc": "طباخ محترف عمره 35 سنة، متوسط الطول، بشرته سمرا، وشعره مجعد. شخصيته مرحة وبيحب يتكلم كتير. كان بيحضر كل وجبات الضحية، وكان موجود في البيت وقت الجريمة. عنده دافع محتمل إن الضحية كان بيهينه قدام الضيوف."},
        {"name": "المحقق", "desc": "محقق متقاعد عمره 60 سنة، طويل ونحيف، وشعره أبيض. شخصيته فضولية وبيلاحظ كل حاجة. كان صديق قديم للضحية وعارف أسراره الخطيرة. عنده دافع محتمل إن الضحية كان بيهدده إنه هيفضح فساده أيام شغله."},
        {"name": "الفنان", "desc": "رسام مشهور عمره 40 سنة، طويل وشعره طويل، وبيلبس هدوم غريبة. شخصيته حساسة ومزاجية. كان بيرسم صورة للضحية وقضى معاه وقت طويل قبل موته. عنده دافع محتمل إن الضحية رفض يدفع ثمن اللوحة اللي طلبها."},
        {"name": "السكرتير", "desc": "سكرتير شخصي عمره 38 سنة، متوسط الطول، أنيق جداً. شخصيته منظمة ودقيقة في كل حاجة. كان بيشتغل مع الضحية لمدة 15 سنة وعارف كل أسراره. عنده دافع محتمل إن الضحية كان بيستغله ومش بيديله حقوقه."},
        {"name": "البستاني", "desc": "بستاني عمره 55 سنة، قوي البنية، بشرته سمرا من الشمس. شخصيته هادية وبيحب العزلة. كان بيعتني بحديقة الضحية وشاف حاجات كتير من الشباك. عنده دافع محتمل إن الضحية كان هيطرده من شغله."},
        {"name": "الخادم", "desc": "خادم عمره 42 سنة، نحيف وبيتحرك بهدوء. شخصيته كتومة وبيعرف يخبي مشاعره. كان بيخدم في بيت الضحية وبيدخل كل الغرف. عنده دافع محتمل إن الضحية كان بيعامله بطريقة سيئة ومهينة."},
        {"name": "الجار", "desc": "جار عمره 50 سنة، متوسط الطول، دايماً بيلبس نظارة شمس. شخصيته فضولية وبيحب يعرف كل حاجة عن اللي حواليه. كان ساكن جنب الضحية وبيراقبه كتير. عنده دافع محتمل إنهم كان بينهم خلافات على حدود الأرض."},
        {"name": "شريك العمل", "desc": "رجل أعمال عمره 48 سنة، طويل وبدين، بيلبس ساعة غالية دايماً. شخصيته طموحة وبيحب الفلوس. كان شريك الضحية في التجارة وعارف كل تفاصيل الشغل. عنده دافع محتمل إنه عايز يسيطر على الشركة لوحده."}
    ]

    # Ensure we have enough templates
    while len(character_templates) < num_players:
        character_templates.append({"name": f"ضيف {len(character_templates) + 1}",
                                   "desc": "شخص غامض كان يعرف الضحية."})

    # Shuffle and select the needed number of templates
    random.shuffle(character_templates)
    selected_templates = character_templates[:num_players]

    # Create the players list
    players = []
    for i, template in enumerate(selected_templates):
        players.append({
            "character_name": f"{template['name']} {chr(65 + i)}",
            "character_description": template["desc"],
            "is_mafia": False
        })

    # Randomly select one player to be the killer
    killer_idx = random.randint(0, len(players) - 1)
    players[killer_idx]["is_mafia"] = True

    # Generate a more unique fallback story with randomization

    # Use current timestamp to ensure uniqueness
    timestamp = int(time.time())
    random.seed(timestamp)

    # Create a list of possible settings
    settings = [
        {
            "location": "فيلا معزولة",
            "event": "حفلة عشاء",
            "weather": "ليلة عاصفة",
            "time": "الساعة 12 بالليل"
        },
        {
            "location": "قصر قديم",
            "event": "احتفال بمناسبة خاصة",
            "weather": "ليلة ممطرة",
            "time": "الساعة 10 مساءً"
        },
        {
            "location": "فندق فخم",
            "event": "مؤتمر أعمال",
            "weather": "ليلة باردة",
            "time": "منتصف الليل"
        },
        {
            "location": "مزرعة بعيدة",
            "event": "رحلة عائلية",
            "weather": "ليلة مقمرة هادئة",
            "time": "بعد العشاء مباشرة"
        },
        {
            "location": "يخت فخم",
            "event": "رحلة بحرية",
            "weather": "ليلة هادئة في عرض البحر",
            "time": "الساعة 11 مساءً"
        }
    ]

    # Create a list of possible victim names
    victim_names = [
        "السيد فريد",
        "الدكتور سامي",
        "المهندس عادل",
        "رجل الأعمال كريم",
        "الأستاذ محمود"
    ]

    # Create a list of possible murder weapons
    weapons = [
        "سكينة قديمة",
        "مسدس صغير",
        "حبل رفيع",
        "زجاجة مكسورة",
        "تمثال ثقيل"
    ]

    # Create a list of possible clues - more complex and ambiguous
    possible_clues = [
        # Clues that can be interpreted in multiple ways
        "ساعة الضحية كانت واقفة عند {}، لكن فيه علامات إن حد غير وقتها عمداً.",
        "ورقة ممزقة من مذكرات الضحية بتقول إنه كان بيخبي سر خطير عن واحد من الموجودين، لكن مافيش اسم محدد.",
        "فيه بقعة دم صغيرة على سجادة في مكان بعيد عن مكان الجريمة، ومحدش لاحظها غير شخص واحد.",

        # Clues that point to multiple suspects
        "بصمات متعددة على {} اللي استخدمت في الجريمة، وكأن فيه أكتر من شخص لمسها.",
        "الضحية كان عنده ملف فيه معلومات عن ثلاثة من الموجودين، والملف اختفى بعد الجريمة.",
        "رسالة غامضة وصلت للضحية قبل الحادث بيوم بتقول: 'اللي بتثق فيهم هما اللي هيأذوك'.",

        # Subtle clues that point to the real killer
        "الضحية كتب اسم مشفر في مذكراته قبل موته، والاسم ده ممكن يشير للقاتل لو حد عرف يفك الشفرة.",
        "فيه شيء صغير مفقود من مكان الجريمة، والشيء ده ممكن يكون موجود مع القاتل بس محدش يعرف.",
        "الضحية كان بيتكلم بالتليفون قبل موته بساعة، وقال جملة غريبة ممكن تشير للقاتل لو فهمناها صح."
    ]

    # Randomly select elements for the story
    setting = random.choice(settings)
    victim_name = random.choice(victim_names)
    weapon = random.choice(weapons)

    # Generate random times for clues
    random_time = f"{random.randint(10, 11)}:{random.randint(30, 59)} مساءً"

    # Select and format clues
    selected_clues = random.sample(possible_clues, 3)
    formatted_clues = []
    for clue in selected_clues:
        if "{}" in clue:
            if "ساعة" in clue:
                formatted_clues.append(clue.format(random_time))
            elif "بصمات" in clue:
                formatted_clues.append(clue.format(weapon))
            else:
                formatted_clues.append(clue)
        else:
            formatted_clues.append(clue)

    # Create a list of possible plot twists
    plot_twists = [
        f"الحقيقة إن {victim_name} كان بيبتز كذا واحد من الموجودين بأسرار خطيرة",
        f"المفاجأة إن {victim_name} كان بيحضر لتغيير وصيته ويحرم كذا واحد من الورثة",
        f"الغريب إن {victim_name} كان عنده علاقات سرية مع أكتر من شخص من الموجودين",
        f"المدهش إن {victim_name} كان بيخطط لانتقام من شخص ما من الموجودين",
        f"المفاجأة إن {victim_name} كان عنده مرض خطير وعمره قصير، وكان بيخطط ينتقم قبل موته"
    ]

    # Select a random plot twist
    plot_twist = random.choice(plot_twists)

    # Generate a more complex story with a plot twist
    story = f"""في {setting['weather']}، اجتمع {num_players} من الضيوف في {setting['location']} لحضور {setting['event']}. كان المضيف، {victim_name}، رجل أعمال غني مشهور بغرابة أطواره وثروته الكبيرة. كان الجو متوتر بين الضيوف، وكأن فيه حاجة غريبة في الهوا.

    وفجأة، عند {setting['time']}، انقطع النور لدقائق معدودة، ولما رجع، سمع الجميع صرخة مرعبة. جري الضيوف لمصدر الصوت ولقيوا {victim_name} ملقي على الأرض، وفيه {weapon} مستخدمة في القتل.

    كانت الأبواب والنوافذ مقفولة من الداخل، والعاصفة بره منعت أي حد يدخل أو يخرج، فاتضح إن القاتل موجود وسط الضيوف الموجودين.

    الغريب إن مع بداية التحقيق، بدأت تظهر حقائق مخفية عن الضحية. {plot_twist}. وده خلى كل الموجودين مشبوهين.

    ودلوقتي، محبوسين سوا لحد الصبح، لازم الضيوف يكتشفوا الحقيقة قبل ما القاتل يضرب تاني. لكن السؤال: هل القاتل واحد بس، ولا فيه حد تاني متورط معاه؟"""

    # Create the fallback story structure
    fallback_story = {
        "main_story": story,
        "killed_character_name": victim_name,
        "players": players,
        "clues": formatted_clues
    }

    return fallback_story

def format_role_description(character_info, killed_character_name=None):
    """
    Format a character role description for display to the player.

    Args:
        character_info (dict): The character information
        killed_character_name (str, optional): The name of the killed character

    Returns:
        str: Formatted role description
    """
    # Handle missing information safely
    if not character_info or not isinstance(character_info, dict):
        return "**Error: Character information is missing or invalid**"

    name = character_info.get("character_name", "Unknown Character")
    description = character_info.get("character_description", "No description available")
    is_mafia = character_info.get("is_mafia", False)
    killed_character = killed_character_name or "the victim"

    # Format the description to highlight different aspects
    formatted_description = description

    # Try to extract and format different parts of the description if it's detailed enough
    if len(description) > 50:  # Only try to format if description is substantial
        # Look for common patterns that might indicate different sections
        sections = []

        # Try to identify age/appearance information
        appearance_patterns = ["عمره", "عندها", "شكله", "مظهره", "طويل", "قصير"]
        for pattern in appearance_patterns:
            if pattern in description.lower():
                sections.append("👤 **المظهر والعمر**: ")
                break

        # Try to identify personality traits
        personality_patterns = ["شخصية", "طباع", "عصبي", "هادئ", "ذكي", "متوتر"]
        for pattern in personality_patterns:
            if pattern in description.lower():
                sections.append("🧠 **الشخصية والطباع**: ")
                break

        # Try to identify relationship with victim
        relation_patterns = ["علاقته", "علاقتها", "صديق", "قريب", "عدو", "شريك"]
        for pattern in relation_patterns:
            if pattern in description.lower():
                sections.append("🔗 **العلاقة بالضحية**: ")
                break

        # Try to identify motive
        motive_patterns = ["دافع", "سبب", "يكره", "ينتقم", "غيران", "طمعان"]
        for pattern in motive_patterns:
            if pattern in description.lower():
                sections.append("💭 **الدافع المحتمل**: ")
                break

        # If we found sections, try to format the description
        if sections:
            # Split description into sentences
            sentences = [s.strip() for s in description.split('.')]
            sentences = [s for s in sentences if s]  # Remove empty strings

            # Distribute sentences among sections
            section_count = len(sections)
            sentences_per_section = max(1, len(sentences) // section_count)

            formatted_parts = []
            for i, section in enumerate(sections):
                start_idx = i * sentences_per_section
                end_idx = start_idx + sentences_per_section if i < section_count - 1 else len(sentences)
                section_text = '. '.join(sentences[start_idx:end_idx]) + '.' if sentences[start_idx:end_idx] else ''
                formatted_parts.append(f"{section}{section_text}")

            formatted_description = '\n\n'.join(formatted_parts)

    role_text = ""

    if is_mafia:
        role_text = f"## You are {name} (The Killer)\n\n"
        role_text += f"{formatted_description}\n\n"
        role_text += f"**You are the killer! You killed {killed_character}. Your goal is to avoid being identified by the other players.**"
    else:
        role_text = f"## You are {name} (Civilian)\n\n"
        role_text += f"{formatted_description}\n\n"
        role_text += f"**You are a civilian. Your goal is to identify the killer responsible for {killed_character}'s death.**"

    return role_text

def format_main_story(story_data):
    """
    Format the main story for display.

    Args:
        story_data (dict): The story data

    Returns:
        str: Formatted main story
    """
    # Handle missing information safely
    if not story_data or not isinstance(story_data, dict):
        return "**Error: Story data is missing or invalid**"

    main_story = story_data.get("main_story", "The story details are mysteriously missing...")
    killed_character = story_data.get("killed_character_name", "Someone")

    # Format the story with markdown for better display
    formatted_story = "# Murder Mystery\n\n"
    formatted_story += main_story + "\n\n"
    formatted_story += f"**{killed_character} has been murdered!**\n\n"
    formatted_story += "As the investigation begins, you must work with the other players to identify the killer responsible for this crime.\n"

    return formatted_story

def format_clue(clue_text, clue_number, total_clues):
    """
    Format a clue for display.

    Args:
        clue_text (str): The clue text
        clue_number (int): The clue number
        total_clues (int): Total number of clues

    Returns:
        str: Formatted clue
    """
    if not clue_text:
        clue_text = "This clue appears to be missing or obscured..."

    return f"**Clue {clue_number} of {total_clues}:** {clue_text}"

def format_round_instructions(round_number):
    """
    Generate instructions for the current game round.

    Args:
        round_number (int): The current round number

    Returns:
        str: Round instructions
    """
    # Handle invalid round number
    try:
        round_num = int(round_number)
        if round_num < 1:
            round_num = 1
    except (ValueError, TypeError):
        round_num = 1

    if round_num == 1:
        return """
        ## Round 1: Investigation Begins

        1. **Discuss the case** with other players outside the app.
        2. Think about the story details and the first clue.
        3. Share your ideas and suspicions.
        4. When you're ready, the admin should select a suspect.
        """
    else:
        return f"""
        ## Round {round_num}: Investigation Continues

        1. A player has been eliminated based on the previous round's accusation.
        2. A new clue has been revealed.
        3. **Discuss again** with the remaining players outside the app.
        4. Reconsider your suspicions based on the new information.
        5. When you're ready, the admin should select a new suspect.
        """

def format_game_results(winner, suspected_player=None, character_name=None):
    """
    Format the game results for display.

    Args:
        winner (str): "civilians" or "mafia"
        suspected_player (str, optional): Name of the suspected player
        character_name (str, optional): Character name of the suspected player

    Returns:
        str: Formatted game results
    """
    # Handle missing information
    suspected_player = suspected_player or "The Killer"
    character_name = character_name or "Unknown Character"

    if winner == "civilians":
        return f"""
        # The Civilians Win!

        Congratulations! The civilians have successfully identified the killer.

        **{suspected_player}** who played the role of **{character_name}** was the killer and has been caught!

        Justice has been served and the town can sleep peacefully again.
        """
    else:
        return """
        # The Killer Wins!

        The killer has eliminated enough civilians to take control of the town.

        The town has descended into darkness as the killer's influence continues unchecked.

        Better luck next time, civilians!
        """
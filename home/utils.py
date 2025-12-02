from openai import OpenAI
from django.conf import settings
import ast
import re

client = OpenAI(api_key=settings.OPENAI_API)

def ideas(Temperature, Weather_Condition, Day, Time, category):
    """
    Generates 10 high-quality, Google Places API–friendly search keywords
    based on weather, temperature, day, time, and category.
    """

    # Category-specific hints
    category_hints = {
        "restaurant": ["dining", "buffet", "grill", "seafood", "bbq", "family", "rooftop", "brunch"],
        "cafe": ["coffee", "dessert", "brunch", "tea", "bistro", "chill", "outdoor"],
        "bar": ["cocktail", "beer", "lounge", "pub", "rooftop", "nightlife", "sports"],
        "activity": ["museum", "park", "cinema", "game zone", "escape room", "bowling", "arcade"],
        "service": ["salon", "spa", "gym", "laundry", "car wash", "repair shop", "pet grooming"]
    }

    related_types = ", ".join(category_hints.get(category.lower(), []))

    # Prompt
    prompt = f"""
    You are generating optimized search keywords for Google Places API.

    Context:
    - Temperature: {Temperature}°C
    - Weather: {Weather_Condition}
    - Day: {Day}
    - Time: {Time}
    - Category: {category}
    - Related types to consider: {related_types}

    Task:
    Generate 10 realistic Google Places–style *search keywords* (each under 5 words)
    that a user might use when searching for {category} given these conditions.

    ✅ Focus on:
    - Real-world business or location types
    - Context relevance (e.g., brunch restaurant for a warm Saturday morning)
    - Diversity (mix ambiance, cuisine, or experience)
    🚫 Avoid:
    - “near me” or “close by”
    - Abstract words like “nice place” or “hidden gem”
    - Duplicates

    Output format (strictly): ["keyword1", "keyword2", ..., "keyword10"]
    """

    response = client.chat.completions.create(model="gpt-4o-mini",  # or "gpt-3.5-turbo"
    messages=[{"role": "user", "content": prompt}],
    temperature=0.8)

    suggestions = response.choices[0].message.content

    # 🧹 Clean possible prefixes like "Output:" or Markdown code fences
    cleaned = re.sub(r"^.*?\[", "[", suggestions, flags=re.DOTALL)
    cleaned = re.sub(r"\].*$", "]", cleaned, flags=re.DOTALL).strip()

    # 🧩 Try parsing clean JSON-style list
    try:
        idea_list = ast.literal_eval(cleaned)
        idea_list = [str(item).strip() for item in idea_list if isinstance(item, str)]
    except (ValueError, SyntaxError):
        print(f"⚠️ Error parsing AI response:\n{suggestions}\n")
        idea_list = [f"{category} nearby"] * 10

    # Guarantee exactly 10
    while len(idea_list) < 10:
        idea_list.append(f"{category} nearby")
    idea_list = idea_list[:10]

    return idea_list


def analyze_reviews_with_ai(place_name, types, combined_text, is_food_related):
    """
    Use OpenAI to summarize reviews + description.
    Returns a summary string and numeric ratings.
    """
    prompt = f"""
You are an expert reviewer. Analyze the following information for {place_name} ({', '.join(types)}).

Description + Reviews:
{combined_text}

1. Identify the top 3 most common positive reasons people like this place.
   Return them as numbered short points (5–6 words each).

2. Provide numeric ratings (out of 5) for:
   {"Food, Service, Atmosphere, Price" if is_food_related else "Service, Atmosphere"}

Return your answer in JSON format like:
{{
  "summary": ["reason1", "reason2", "reason3"],
  "ratings": {{
      "food": 4.5,
      "service": 4.2,
      "atmosphere": 4.0,
      "price": 3.5
  }}
}}
"""

    try:
        response = client.chat.completions.create(model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7)
        content = response.choices[0].message.content.strip()
        # Try to parse JSON returned by AI
        import json
        return json.loads(content)
    except Exception as e:
        print("OpenAI Error:", e)
        return {
            "summary": ["Summary not available."],
            "ratings": {
                "food": None if is_food_related else None,
                "service": None,
                "atmosphere": None,
                "price": None if is_food_related else None
            }
        }


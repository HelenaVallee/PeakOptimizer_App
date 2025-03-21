import warnings
import os
import json
import logging

# Configure logging
logger = logging.getLogger(__name__)

warnings.filterwarnings("ignore")

# Try to read API key but use fallback if not available
try:
    with open("api_keys.json", "r") as f:
        api_keys = json.load(f)
        your_api_key = api_keys.get("together")
        if not your_api_key:
            logger.warning("No Together API key found in api_keys.json")
            your_api_key = "default_key"  # This will fail gracefully when API is called
except Exception as e:
    logger.error(f"Error loading API key: {e}")
    your_api_key = "default_key"  # This will fail gracefully when API is called

# Fallback recommendations by mood type
FALLBACK_RECOMMENDATIONS = {
    "default": [
        "Take 3 deep breaths to center yourself.",
        "Stretch your arms overhead for 10 seconds.",
        "Set one clear goal for this work session."
    ],
    "stressed": [
        "Practice box breathing: 4 counts in, hold 4, out 4, hold 4.",
        "Roll your shoulders slowly in circles to release tension.",
        "Write down your top priority for the next hour."
    ],
    "tired": [
        "Try 10 jumping jacks to boost energy and circulation.",
        "Stretch your back by twisting gently from side to side.",
        "Break your next task into smaller, more manageable steps."
    ],
    "distracted": [
        "Focus on your breath for 30 seconds to reset your attention.",
        "Stretch your neck by tilting your head from side to side.",
        "Close unnecessary browser tabs and apps for better focus."
    ],
    "creative": [
        "Take five deep breaths to expand your thinking.",
        "Loosen up with shoulder circles and arm stretches.",
        "Quickly freewrite your ideas without judgment for 2 minutes."
    ]
}

# Function to call LLM (simplified version to avoid the together import)
def prompt_llm(prompt, show_cost=False):
    logger.error("LLM API is not available, using fallbacks")
    return None

# RecommendActions class
class RecommendActions:
    def generate_recommendations(self, mood, duration, concerns="", num_interventions=3):
        """
        Generate personalized recommendations based on mood, duration, and physical concerns.
        
        Args:
            mood (str): The user's current mood or full input text
            duration (int): Session duration in minutes
            concerns (str): Specific physical concerns (e.g., back pain)
            num_interventions (int): Number of interventions to generate
            
        Returns:
            str: Recommendations, each on a new line
        """
        # Clean up inputs
        if not mood or mood.strip() == "":
            mood = "neutral"
        
        # Normalize mood to lowercase for matching
        mood_lower = mood.lower().strip()
        concerns_lower = concerns.lower().strip() if concerns else ""
        
        # The user input could be in either mood or concerns or both
        combined_input = f"{mood}"
        if concerns and concerns != mood:  # If concerns contains different information
            combined_input = f"{mood}. {concerns}"
        
        # Log the request
        logger.info(f"Generating {num_interventions} recommendations for user input: '{combined_input}', duration: {duration} minutes")
        
        # Using fallbacks directly since together API is removed for simplicity
        logger.warning("Using fallback recommendations since API is not available")
        
        # Use combined input to better detect concerns for fallbacks
        combined_lower = combined_input.lower()
        
        # Use specialized fallbacks based on concerns if applicable
        for key in ["head", "headache", "migraine"]:
            if key in combined_lower:
                head_exercises = [
                    "Gently massage your temples in small circles for 30 seconds.",
                    "Take a short break from screens and close your eyes for 1 minute.",
                    "Drink a full glass of water to stay hydrated.",
                    "Try gentle neck stretches by slowly tilting your head side to side.",
                    "Apply light pressure to the area between your eyebrows for 20 seconds."
                ]
                logger.info(f"Using headache fallback recommendations for input: {combined_input}")
                return "\n".join(head_exercises[:num_interventions])
                
        for key in ["back", "spine", "neck", "posture"]:
            if key in combined_lower:
                back_exercises = [
                    "Gently stretch your lower back by leaning forward in your chair.",
                    "Stand up and do a gentle spinal twist to release back tension.",
                    "Try the cat-cow stretch to mobilize your spine and relieve pressure.",
                    "Stretch your psoas by doing a gentle lunge while standing.",
                    "Sit up straight and do shoulder rolls to align your posture."
                ]
                logger.info(f"Using back pain fallback recommendations for input: {combined_input}")
                return "\n".join(back_exercises[:num_interventions])
                
        for key in ["eye", "vision", "sight", "screen"]:
            if key in combined_lower:
                eye_exercises = [
                    "Look at something 20 feet away for 20 seconds (20-20-20 rule).",
                    "Gently massage around your eyes to reduce eye strain.",
                    "Close your eyes and cover them with warm palms for 30 seconds.",
                    "Blink rapidly 15 times to refresh your eyes and clear your vision.",
                    "Look far left, right, up, down, holding each for 3 seconds."
                ]
                logger.info(f"Using eye strain fallback recommendations for input: {combined_input}")
                return "\n".join(eye_exercises[:num_interventions])
                
        for key in ["wrist", "hand", "finger", "carpal"]:
            if key in combined_lower:
                wrist_exercises = [
                    "Stretch your wrists by extending arms and gently pulling fingers back.",
                    "Make fists then spread your fingers wide 5 times to improve circulation.",
                    "Rotate your wrists in circles 10 times in each direction.",
                    "Gently shake out your hands to release tension.",
                    "Press your palms together in prayer position to stretch your wrists."
                ]
                logger.info(f"Using wrist pain fallback recommendations for input: {combined_input}")
                return "\n".join(wrist_exercises[:num_interventions])
                
        for key in ["focus", "attention", "distract", "concentrate"]:
            if key in combined_lower:
                focus_exercises = [
                    "Take three deep breaths to reset your attention.",
                    "Close your eyes and count slowly to 10 to clear your mind.",
                    "Write down the one most important task to focus on now.",
                    "Do a 2-minute mindfulness practice focusing only on your breath.",
                    "Close unnecessary browser tabs and apps before continuing."
                ]
                logger.info(f"Using focus improvement fallback recommendations for input: {combined_input}")
                return "\n".join(focus_exercises[:num_interventions])
                
        for key in ["leg", "foot", "knee", "ankle", "asleep"]:
            if key in combined_lower:
                leg_exercises = [
                    "Stand up and gently shake out your legs to improve circulation.",
                    "Try ankle rotations - 10 circles in each direction per foot.",
                    "Do 10 gentle knee bends while holding onto your desk for support.",
                    "While seated, lift and lower your heels 15 times to engage your calves.",
                    "March in place for 30 seconds to wake up your leg muscles."
                ]
                logger.info(f"Using leg circulation fallback recommendations for input: {combined_input}")
                return "\n".join(leg_exercises[:num_interventions])
        
        # Determine which fallback set to use based on mood
        for key in ["stressed", "tired", "distracted", "creative"]:
            if key in combined_lower:
                logger.info(f"Using '{key}' fallback recommendations for mood in: {combined_input}")
                return "\n".join(FALLBACK_RECOMMENDATIONS[key][:num_interventions])
        
        # Default fallback
        logger.info(f"Using default fallback recommendations for input: {combined_input}")
        return "\n".join(FALLBACK_RECOMMENDATIONS["default"][:num_interventions])
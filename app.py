from flask import Flask, jsonify, request, render_template
from agents import RecommendActions
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
recommend_agent = RecommendActions()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/start_session', methods=['POST'])
def start_session():
    try:
        data = request.get_json()
        
        if not data:
            logger.warning("No JSON data received in request")
            return jsonify({"error": "No data provided"}), 400
            
        # Extract from the combined user input
        user_input = data.get('user_input', 'neutral')
        duration = data.get('duration', 30)
        
        # Process the user input to identify mood and concerns
        # This simple approach will be enhanced by the AI model
        user_input_lower = user_input.lower()
        
        # Extract potential concerns by looking for common physical issues
        concerns = ""
        concern_keywords = [
            "pain", "ache", "hurt", "sore", "tension", "strain", 
            "eye", "back", "neck", "head", "wrist", "shoulder", "knee",
            "tired", "fatigue", "exhaust", "stress", "focus", "concentrate"
        ]
        
        for keyword in concern_keywords:
            if keyword in user_input_lower:
                concerns = user_input  # If we find any concern, use the full input
                break
        
        # Determine primary mood (simplified approach)
        mood = "neutral"  # default
        mood_keywords = {
            "stressed": ["stress", "anxious", "worried", "overwhelm", "pressure"],
            "tired": ["tired", "exhaust", "fatigue", "sleepy", "drowsy"],
            "distracted": ["distract", "focus", "concentrate", "attention"],
            "creative": ["creative", "inspired", "imaginative"],
            "happy": ["happy", "good", "great", "excellent", "amazing"],
            "sad": ["sad", "down", "depress", "unhappy", "blue"]
        }
        
        for potential_mood, keywords in mood_keywords.items():
            for keyword in keywords:
                if keyword in user_input_lower:
                    mood = potential_mood
                    break
            if mood != "neutral":
                break
                
        # If no specific mood detected, use the full input as mood
        if mood == "neutral" and user_input != "neutral":
            mood = user_input
        
        logger.info(f"Processed user input: '{user_input}' → Mood: '{mood}', Concerns: '{concerns}', Duration: {duration}")
        
        # Calculate optimal number of interventions based on session length
        # For shorter sessions (under 20 min), just 1 intervention
        # For medium sessions (20-40 min), 2 interventions
        # For longer sessions (over 40 min), 3+ interventions (1 per 20 minutes)
        if duration < 20:
            num_interventions = 1
        elif duration < 40:
            num_interventions = 2
        else:
            num_interventions = max(3, round(duration / 20))
            
        # Cap at a reasonable number
        num_interventions = min(num_interventions, 5)
        
        logger.info(f"Planning {num_interventions} interventions for {duration}-minute session")
        
        # Generate personalized snack recommendations
        ai_response = recommend_agent.generate_recommendations(mood, duration, concerns, num_interventions)
        
        # Ensure proper JSON structure
        nudges = [line.strip() for line in ai_response.split("\n") if line.strip()]
        
        if not nudges or len(nudges) < num_interventions:
            # If no valid nudges were found, provide fallback recommendations
            nudges = []
            if "back" in concerns.lower() or "spine" in concerns.lower():
                nudges.append("Gently stretch your lower back by leaning forward in your chair.")
                nudges.append("Stand up and do a gentle spinal twist to release back tension.")
            elif "eye" in concerns.lower() or "vision" in concerns.lower():
                nudges.append("Look away at something 20 feet away for 20 seconds (20-20-20 rule).")
                nudges.append("Gently massage around your eyes to reduce eye strain.")
            elif "wrist" in concerns.lower() or "hand" in concerns.lower():
                nudges.append("Stretch your wrists by extending your arms and gently pulling fingers back.")
                nudges.append("Make fists then spread your fingers wide 5 times to improve circulation.")
            else:
                # Default fallbacks if specific concerns don't match
                nudges.append("Take 3 deep breaths to center yourself.")
                nudges.append("Stand up and stretch your arms overhead for 10 seconds.")
                nudges.append("Set one clear goal for the remainder of your work session.")
            
            # Ensure we have exactly the right number of interventions
            while len(nudges) < num_interventions:
                nudges.append("Take a moment to stand up, stretch, and reset your posture.")
            
            # Trim if we have too many
            nudges = nudges[:num_interventions]
            
            logger.warning("Using fallback recommendations - no valid nudges returned from AI")
        
        # Calculate timing for interventions (when they should appear during the session)
        timing = []
        if num_interventions == 1:
            # Single intervention goes at the halfway mark
            timing = [int(duration * 30)]  # in seconds (half the duration)
        else:
            # Space interventions evenly throughout the session, but leave some
            # buffer at the beginning and end (don't start right away or end at the very end)
            session_seconds = duration * 60
            usable_time = session_seconds * 0.85  # Use 85% of the session time for interventions
            start_buffer = (session_seconds - usable_time) / 2  # Buffer at start and end
            
            if num_interventions > 1:
                interval = usable_time / (num_interventions - 1) if num_interventions > 1 else usable_time
                for i in range(num_interventions):
                    # First intervention after a short delay, last one before session ends
                    timing.append(int(start_buffer + (interval * i)))
            else:
                timing = [int(session_seconds / 2)]  # Fallback to middle if calculation fails
        
        # Ensure timings aren't too early or too late
        timing = [max(10, t) for t in timing]  # At least 10 seconds into session
        timing = [min(t, duration * 60 - 10) for t in timing]  # At least 10 seconds before end
        
        logger.info(f"Intervention timing (seconds): {timing}")
        logger.info(f"Returning {len(nudges)} nudges with {num_interventions} planned interventions")
        
        return jsonify({
            "nudges": nudges,
            "timing": timing  # Return timing information to the frontend
        })
        
    except Exception as e:
        logger.error(f"Error in start_session: {str(e)}")
        return jsonify({"error": "An error occurred processing your request", "details": str(e)}), 500

@app.route('/static/<path:filename>')
def serve_static(filename):
    return app.send_static_file(filename)

if __name__ == '__main__':
    print("Starting PeakOptimizer app...")
    print("Access the app at: http://localhost:5001")
    app.run(debug=True, port=5001)


# suppress warnings
import warnings
import os
import json

warnings.filterwarnings("ignore")
from together import Together

# Get Client
with open("api_keys.json", "r") as f:
    api_keys = json.load(f)

your_api_key = api_keys["together"]
client = Together(api_key=your_api_key)


def prompt_llm(prompt, show_cost=False):
    # This function allows us to prompt an LLM via the Together API

    # model
    model = "meta-llama/Meta-Llama-3-8B-Instruct-Lite"

    # Calculate the number of tokens
    tokens = len(prompt.split())

    # Calculate and print estimated cost for each model
    if show_cost:
        print(f"\nNumber of tokens: {tokens}")
        cost = (0.1 / 1_000_000) * tokens
        print(f"Estimated cost for {model}: ${cost:.10f}\n")

    # Make the API call
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


# Add CancellationEmailAgent class
class CancellationEmailAgent:
    def generate_email(
        self, patient_name, appointment_date, appointment_time, clinician_name
    ):
        prompt = f"""
        Generate an empathetic email to a patient whose medical appointment has been canceled.
        
        Use this as an example of how to write an email to a patient whose appointment has been canceled:
        Example 1:
        Subject: Appointment Rescheduled
        Dear [Patient Name],
        I hope this message finds you well. I wanted to inform you that your upcoming appointment with Dr. [Clinician Name] has been rescheduled.
        The new date and time for your appointment are [New Date and Time].
        Please note that this change is due to unforeseen circumstances, and we apologize for any inconvenience this may cause.
        If you have any questions or need further assistance, please do not hesitate to contact us at [Office Phone Number].
        Thank you for your understanding and cooperation.
        Best regards,
        [Your Name]
        [Your Position]
        [Your Contact Information]
        
        
        - Patient Name: {patient_name}
        - Original Appointment Date: {appointment_date}
        - Original Appointment Time: {appointment_time}
        - Clinician: {clinician_name}
        
        INSTRUCTIONS:
        - Start with a respectful greeting
        - Express sincere apology for the cancellation
        - Briefly explain that unforeseen circumstances required rescheduling (without specifics)
        - Invite them to call the office to reschedule at their convenience
        - Provide the office phone number as (555) 123-4567
        - End with a professional and caring closing
        - Keep the tone empathetic, professional, and concise
        - The email should be 4-6 sentences total
        
        Write only the email content, with no additional commentary.
        """

        return prompt_llm(prompt)


# Add RecommendActions class
class RecommendActions:
    def generate_recommendations(self, activity_data):
        prompt = f"""
        As an AI wellness assistant, analyze the following user activity data and provide personalized recommendations 
        for breaks, movement, and ergonomic improvements.

        USER ACTIVITY DATA:
        {json.dumps(activity_data, indent=2)}
        
        INSTRUCTIONS:
        - Analyze typing patterns, mouse usage, and application switching frequency
        - Suggest exactly 2 specific, actionable recommendations:
          1. One posture/ergonomic recommendation
          2. One productivity optimization tip
        - Each recommendation MUST be 12 words or fewer
        - Keep recommendations concise, practical and actionable
        - Format your response as HTML with the following structure:
        - Show only the recommendations, and a one line justifying the recommendations
        
        <p>Based on your activity patterns:</p>
        <ul>
          <li><strong>Posture Tip:</strong> [Your recommendation here - max 12 words]</li>
          <li><strong>Productivity Tip:</strong> [Your recommendation here - max 12 words]</li>
        </ul>
        
        Your recommendations should be personalized to the specific patterns in the data.
        """

        return prompt_llm(prompt)
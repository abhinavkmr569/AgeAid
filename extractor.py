from google import genai
from google.genai import types
import os
import json
from schemas import ExtractionResult

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def call_gemini_model(model_name: str, image_bytes: bytes, mime_type: str):
    valid_mime = mime_type if mime_type in ["application/pdf", "image/png"] else "image/jpeg"
    
    prompt_text = """
    Extract blood test data into valid JSON.
    
    CRITICAL RULES FOR EXTRACTION:
    1. **Lab Name**: Extract from header (e.g. "Thyrocare", "Apollo").
    2. **Date**: Format as "DD Month YYYY" (e.g., "10 July 2025").
    
    3. **MEDICAL SANITY CHECK (CRITICAL):**
       - **Cross-check values with standard units.**
       - **HDL Cholesterol:** Must be in **mg/dL** (usually 30-80). If value is < 10 (e.g., 2.9, 4.5) and unit is "Ratio", rename it to **"Chol/HDL Ratio"** or **"LDL/HDL Ratio"**. DO NOT call it "HDL Cholesterol".
       - **HbA1c:** Value is usually 4-10%. If value is > 50, check if it is "Average Glucose" instead.
       - **Creatinine:** Value is usually 0.5-2.0 mg/dL.
       - **Platelets:** Value is usually 150-450 (x10^3). If text says "1.5 Lakh", convert to 150. 
       - **Manual Overrides**: If remark says "Manual: 150", use 150.

       
    4. **RANGES:**
       - "< 200" -> min:0, max:200
       - "> 55" -> min:55, max:null
       - "10-20" -> min:10, max:20
    
    Rate confidence (0-100).
    """

    response = client.models.generate_content(
        model=model_name,
        contents=[
            types.Content(
                role="user",
                parts=[
                    types.Part(text=prompt_text),
                    types.Part(inline_data=types.Blob(data=image_bytes, mime_type=valid_mime))
                ]
            )
        ],
        config={"response_mime_type": "application/json", "response_schema": ExtractionResult}
    )
    return response

def smart_extract(image_bytes: bytes, mime_type: str):
    print(f"⚡ Attempting Gemini 2.5 Flash...")
    model_used = "gemini-2.5-flash"
    tokens = 0 # <--- NEW: Default
    try:
        response = call_gemini_model("gemini-2.5-flash", image_bytes, mime_type)
        data = response.parsed

        if response.usage_metadata:
            tokens = response.usage_metadata.total_token_count
        
        avg = sum(r.confidence_score for r in data.results)/len(data.results) if data.results else 0
        
        # Fallback if confidence is low or critical fields missing
        if avg < 90 or not data.results:
            print("⚠️ Low Confidence. Escalating to Gemini 2.5 Pro...")
            
            model_used = "gemini-2.5-pro"
            response = call_gemini_model("gemini-2.5-pro", image_bytes, mime_type)
            data = response.parsed

            # Update Tokens (We take the Pro usage cost)
            if response.usage_metadata:
                tokens = response.usage_metadata.total_token_count

    except Exception as e:
        print(f"❌ Error: {e}. Retrying with Pro...")

        model_used = "gemini-2.5-pro"
        response = call_gemini_model("gemini-2.5-pro", image_bytes, mime_type)

        data = response.parsed 

        # Update Tokens (We take the Pro usage cost)
        if response.usage_metadata:
            tokens = response.usage_metadata.total_token_count  
        

    return data, model_used

# ... (Keep analyze_trend_with_gemini same as before) ...
def analyze_trend_with_gemini(user_profile, primary_target, history_by_date, current_remark):
    timeline_text = ""
    for date in sorted(history_by_date.keys()):
        timeline_text += f"\n📅 {date}\n"
        for test in history_by_date[date]:
            marker = "👉" if test['name'].lower() == primary_target.lower() else "-"
            timeline_text += f"   {marker} {test['name']}: {test['value']} {test['unit']} (Ref: {test['min']}-{test['max']}) [Lab: {test['lab']}]\n"

    prompt = f"""
    You are a medical AI. Analyze "{primary_target}".
    
    PATIENT: {user_profile.get('name')} ({user_profile.get('gender')}, DOB: {user_profile.get('birth_date')})
    HISTORY: {user_profile.get('medical_history')}
    LIFESTYLE: Diet: {user_profile.get('diet')}, Activity: {user_profile.get('activity')}
    
    HEALTH JOURNAL (Context):
    {current_remark}
    
    DATA:
    {timeline_text}
    
    TASK:
    1. Trend Analysis (Improving/Worsening?)
    2. Correlate with Journal/Lifestyle.
    3. Suggest 3 actionable tips.
    
    DISCLAIMER: Start with "⚠️ **AI Analysis**" and end with "**Please consult a doctor.**"
    """
    
    try:
        response = client.models.generate_content(model="gemini-2.5-pro", contents=prompt)
        return response.text
    except:
        return client.models.generate_content(model="gemini-2.5-flash", contents=prompt).text
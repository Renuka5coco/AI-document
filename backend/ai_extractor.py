import json
import os
import re
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

def local_regex_extractor(text):
    """Fallback local extractor using Regex when OpenAI API key is missing."""
    data = {
        "customer_name": None,
        "loan_amount": None,
        "emi": None,
        "interest_rate": None,
        "start_date": None
    }
    
    # Extract name (e.g., Name: John Doe or Customer Name: Jane Smith)
    name_match = re.search(r'(?i)(?:Name|Customer[\s_]*Name)[\s:]*([A-Za-z\s]+)', text)
    if name_match:
        # Take the first 2-3 words as name to avoid capturing the whole remaining text
        words = name_match.group(1).strip().split()
        data["customer_name"] = " ".join(words[:3])
        
    # Extract loan amount (e.g., Loan Amount: 50000 or $50,000)
    amount_match = re.search(r'(?i)(?:Loan[\s_]*Amount|Principal|Amount)[\s:\$]*([\d,\.]+)', text)
    if amount_match:
        try:
            data["loan_amount"] = float(amount_match.group(1).replace(',', ''))
        except:
            pass
            
    # Extract EMI (e.g., EMI: 500 or Monthly Installment: 500)
    emi_match = re.search(r'(?i)(?:EMI|Monthly[\s_]*Installment|Installment|Monthly)[\s:\$]*([\d,\.]+)', text)
    if emi_match:
        try:
            data["emi"] = float(emi_match.group(1).replace(',', ''))
        except:
            pass
            
    # Extract interest rate (e.g., Interest Rate: 10% or Rate: 5.5%)
    rate_match = re.search(r'(?i)(?:Interest[\s_]*Rate|Rate)[\s:]*([\d\.]+\s*%)', text)
    if rate_match:
        data["interest_rate"] = rate_match.group(1).strip()
        
    # Extract start date (e.g., Start Date: 2024-01-01 or Date: 01/01/2024)
    date_match = re.search(r'(?i)(?:Start[\s_]*Date|Date)[\s:]*([\d]{2,4}[-/][\d]{1,2}[-/][\d]{1,4})', text)
    if date_match:
        data["start_date"] = date_match.group(1).strip()
        
    # If no fields were extracted, we provide a preview of what OCR actually read
    # This helps debugging if Tesseract read garbage or the image was empty.
    if not any(data.values()):
         preview = text.strip()[:150] + "..." if len(text.strip()) > 150 else text.strip()
         if not preview:
             preview = "No text could be read from the document."
         return {
             "customer_name": "Could not identify (Regex Local)",
             "loan_amount": 0,
             "emi": 0,
             "interest_rate": "0%",
             "start_date": "N/A",
             "ocr_text_preview": preview
         }
         
    return data

def extract_structured_data(text):
    api_key = os.environ.get("OPENAI_API_KEY", "")
    
    # Use local extraction if key is missing or default
    if not api_key or api_key == "your_openai_api_key_here" or OpenAI is None:
        print("Using Local Regex Extractor since OpenAI API key is missing.")
        return local_regex_extractor(text)
        
    client = OpenAI(api_key=api_key)
    prompt = f"""
    You are an intelligent document parsing assistant. Extract the required data fields from the raw OCR text below. The text may be unstructured and come from various document formats.

    Fields to extract:
    1. "customer_name" (string): Full name of the customer.
    2. "loan_amount" (number): Total loan amount (numeric only).
    3. "emi" (number): Equated Monthly Installment amount (numeric only).
    4. "interest_rate" (string): The interest rate (e.g., 12%).
    5. "start_date" (string): The loan start date.

    Strict Rules:
    - You MUST output ONLY a valid JSON object. No explanations, no markdown blocks, no extra text.
    - The keys in your JSON object must exactly match the field names listed above.
    - If a field is missing, unclear, or not found in the text, you MUST set its value to `null`.

    Raw OCR Text:
    {text}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a precise data extraction API. You always respond strictly with a valid JSON object, containing no extra text."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"OpenAI API Error: {e}")
        # Fall back to local extractor even if API fails
        print("Falling back to local extractor.")
        return local_regex_extractor(text)

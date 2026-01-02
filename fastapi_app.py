from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from pydantic import BaseModel
import pandas as pd
from google import genai
import os
from dotenv import load_dotenv
import uuid
import io
import json
import textwrap

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Gemini CSV Chat API",
    description="API for uploading CSVs and chatting with Gemini AI",
    version="1.0.0"
)

# In-memory session storage
# Structure: {session_id: {"df": DataFrame, "summary": str, "filename": str}}
sessions = {}

def get_client():
    """Initialize Gemini Client"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured in .env")
    return genai.Client(api_key=api_key)

def get_csv_context(df, max_rows=100):
    """Extract meaningful context from the dataframe for Gemini"""
    
    # Limit rows to avoid token limits
    if len(df) > max_rows:
        df_sample = df.head(max_rows)
    else:
        df_sample = df
    
    # Convert to structured JSON format for better understanding
    context = {
        "dataset_info": {
            "rows": len(df),
            "columns": len(df.columns),
            "columns_list": df.columns.tolist()
        },
        "data_preview": {
            "first_5_rows": df_sample.head().to_dict(orient='records'),
            "last_5_rows": df_sample.tail().to_dict(orient='records')
        },
        "statistics": {
            "numeric_columns": df.describe().to_dict() if not df.select_dtypes(include='number').empty else {},
            "categorical_summary": {
                col: df[col].value_counts().head().to_dict() 
                for col in df.select_dtypes(include='object').columns[:5]  # Limit to 5 categorical cols
            }
        }
    }
    
    # Convert to text for Gemini
    context_text = f"""
# CSV DATA ANALYSIS CONTEXT

## DATASET OVERVIEW
- Total Rows: {context['dataset_info']['rows']}
- Total Columns: {context['dataset_info']['columns']}
- Column Names: {', '.join(context['dataset_info']['columns_list'])}

## DATA PREVIEW

### First 5 Rows:
{json.dumps(context['data_preview']['first_5_rows'], indent=2)}

### Last 5 Rows:
{json.dumps(context['data_preview']['last_5_rows'], indent=2)}

## STATISTICAL SUMMARY

### Numeric Columns Summary:
{json.dumps(context['statistics']['numeric_columns'], indent=2)}

### Categorical Columns (Top Values):
{json.dumps(context['statistics']['categorical_summary'], indent=2)}
"""
    
    return context_text

class ChatRequest(BaseModel):
    session_id: str
    message: str
    model: str = "gemini-2.5-flash"

@app.get("/")
async def root():
    return {"message": "Welcome to Gemini CSV Chat API. POST to /upload to start."}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a CSV file and get a session ID"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    try:
        content = await file.read()
        # Read CSV from bytes with better error handling
        df = pd.read_csv(io.BytesIO(content))
        
        # Basic cleaning
        df = df.dropna(how='all')  # Remove completely empty rows
        df = df.reset_index(drop=True)
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Store DataFrame and context in memory
        sessions[session_id] = {
            "df": df,
            "context": get_csv_context(df),
            "filename": file.filename,
            "original_df": df.copy()  # Keep original for reference
        }
        
        return {
            "session_id": session_id,
            "message": "File uploaded successfully",
            "filename": file.filename,
            "rows": len(df),
            "columns": len(df.columns),
            "sample_data": df.head(3).to_dict(orient='records')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.post("/chat")
async def chat(request: ChatRequest):
    """Chat with the uploaded CSV data"""
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found. Please upload a file first.")
    
    session_data = sessions[request.session_id]
    context = session_data["context"]
    df = session_data["df"]
    
    client = get_client()
    
    # Enhanced prompt with better instructions
    prompt = f"""
You are a data analyst assistant. You have access to CSV data. 
Use the following data context to answer the user's question accurately.

{context}

USER'S QUESTION: {request.message}

IMPORTANT INSTRUCTIONS:
1. Base your answer ONLY on the data provided above
2. If you need to calculate something, show your reasoning
3. If data is not available, say "The data doesn't contain information about [specific thing]"
4. Be specific and include actual numbers/values from the data
5. Format your answer clearly with bullet points or short paragraphs
6. If asked about trends or patterns, analyze the provided data

ANSWER:
"""
    
    try:
        # Generate content using the specified model
        response = client.models.generate_content(
            model=request.model,
            contents=prompt
        )
        
        # Clean up the response
        answer = response.text.strip()
        
        # For certain types of questions, you could add data validation here
        if any(word in request.message.lower() for word in ["sum", "total", "average", "mean", "count"]):
            # Try to double-check with pandas if it's a simple calculation
            try:
                # This is a simple example - you could expand this
                if "total" in request.message.lower() and "sales" in request.message.lower():
                    # Check if there's a sales column
                    if 'sales' in df.columns.str.lower():
                        sales_col = df.columns[df.columns.str.lower().str.contains('sales')][0]
                        total_sales = df[sales_col].sum()
                        answer += f"\n\n**Data Validation:** Based on direct calculation, total {sales_col} = {total_sales}"
            except:
                pass  # Don't break if validation fails
        
        return {"response": answer}
    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg:
            raise HTTPException(status_code=404, detail=f"Model {request.model} not found. Try 'gemini-2.5-flash'.")
        if "429" in error_msg:
            raise HTTPException(status_code=429, detail="Quota exceeded. Please wait or switch models.")
        if "content" in error_msg.lower():
            # Handle content policy issues
            return {"response": "⚠️ The question might violate content policies. Please rephrase."}
        
        raise HTTPException(status_code=500, detail=f"Gemini API Error: {error_msg}")

# Optional: Add an endpoint to get raw data for debugging
@app.get("/session/{session_id}/data")
async def get_session_data(session_id: str, max_rows: int = 20):
    """Debug endpoint to see what data is stored"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    df = sessions[session_id]["df"]
    return {
        "filename": sessions[session_id]["filename"],
        "total_rows": len(df),
        "data_preview": df.head(max_rows).to_dict(orient='records'),
        "context_preview": sessions[session_id]["context"][:1000] + "..." if len(sessions[session_id]["context"]) > 1000 else sessions[session_id]["context"]
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting API server on http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load environment variables from .env file
load_dotenv()

def test_llm_connection():
    """
    Tests the connection to the LLM provider by making a direct API call.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    
    if not api_key:
        print("❌ Error: OPENROUTER_API_KEY is not set in the environment.")
        return
        
    print("--- Configuration ---")
    print("✅ API Key loaded.")
    print(f"✅ Base URL: {base_url}")
    print("--------------------")

    try:
        print("\nAttempting to initialize ChatOpenAI...")
        llm = ChatOpenAI(
            model_name="deepseek/deepseek-r1:free",
            api_key=api_key,
            base_url=base_url
        )
        print("✅ ChatOpenAI initialized successfully.")
        
        print("\nAttempting to invoke the language model...")
        response = llm.invoke("Hello, this is a test.")
        
        print("\n✅ Success! Received response from the LLM:")
        print(response)
        
    except Exception as e:
        print(f"\n❌ A critical error occurred during the API call:")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Details: {e}")
        print("\nFull Traceback:")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_llm_connection() 
# eval-ai-agents

## Create agent with Google ADK

### STEP 1. Setup the python virtual environment
Open terminal window and run the following commands:

**macOS / Linux**
```bash
rm -rf .venv
python3.12 -m venv .venv
source .venv/bin/activate
```

**Windows**
```powershell
rm -r -fo .venv
py -3.12 -m venv .venv
.venv\Scripts\activate
```

### STEP 2. Install Google ADK
```pip install google-adk```

### STEP 3. Create agent

```adk create my_agent```

When prompted,
```
Choose a model for the root agent:
1. gemini-3.5-flash
2. gemini-3.8-flash
3. Other models (fill later)
Choose model (1, 2, 3): 1
1. Google AI
2. Vertex AI
3. Login with Google
Choose a backend (1, 2, 3): 1
```

### STEP 4. Run with the web intefrace
```adk web --port 8000```

Run this command from the parent directory that contains your my_agent/ folder.


### STEP 5. Add a tool to an agent
In ```agent.py```:
```
import requests
from google.adk.agents.llm_agent import Agent


MOCK_API_BASE_URL = "https://fake-json-api.mock.beeceptor.com/users"


def get_user_data(user_id: str) -> dict:
    try:
        response = requests.get(f"{MOCK_API_BASE_URL}/{user_id}", timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}

root_agent = Agent(
    model='gemini-3.5-flash',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge. Use the get_user_data tool to retrieve user data. Put user ID to the input of the tool.',
    tools=[get_user_data]
)
```

### STEP 6. Install Eval module
```pip install "google-adk[eval]"```

### STEP 7. Add test cofig for the evaluations

Create `test_config.json` in `my_agent` folder:

```
{
  "criteria": {
    "rubric_based_final_response_quality_v1": {
      "threshold": 0.8,
      "judge_model_options": {
        "judge_model": "gemini-3.5-flash",
        "num_samples": 3
      },
      "rubrics": [
        {
          "rubric_id": "has_contact_details",
          "rubric_content": {
            "text_property": "The response contains any user's email, phone number, or address"
          }
        },
        {
          "rubric_id": "has_name",
          "rubric_content": {
            "text_property": "The response contains user's name."
          }
        }
      ]
    }
  }
}
```

Run the evaluation with this config:
```adk eval my_agent my_agent/<YOUR_EVAL_SET>.evalset.json --config_file_path=my_agent/test_config.json```
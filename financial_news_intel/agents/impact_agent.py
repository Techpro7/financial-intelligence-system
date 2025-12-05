# from langchain_community.chat_models import ChatOllama
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List, Optional

# --- Import ALL required structures from models.py ---
# Assumes models.py contains FinancialNewsState, ImpactedStock, ImpactDirection, ImpactType, and ImpactedStockList
from financial_news_intel.core.models import (
    FinancialNewsState, 
    ImpactedStock,          
    ImpactDirection,        
    ImpactType,             
    ImpactedStockList,      # The wrapper model for the list output
)

from financial_news_intel.agents.tools import ALL_TOOLS # Import the custom tool list
from financial_news_intel.core.config import OLLAMA_BASE_URL, OLLAMA_MODEL_NAME

# Agent function (runs as a node in LangGraph)
def impact_stock_agent(state: FinancialNewsState) -> FinancialNewsState:
    """
    Analyzes the current story and uses the ticker tool and LLM reasoning to determine 
    stock tickers, directional impact, confidence, and impact type, adhering to 
    the problem statement's business logic.
    """
    current_story = state.current_story
    if not current_story:
        print("ERROR: Impact Stock Agent received no current_story.")
        return state

    print(f"--- Running Impacted Stock Agent for Story ID: {current_story.unique_story_id[:8]}...")

    # 1. Define LLM and Prompt
    llm = ChatOllama(model=OLLAMA_MODEL_NAME, base_url=OLLAMA_BASE_URL, temperature=0.1)

    # Convert Enum values to strings for prompt clarity
    impact_types_str = ", ".join([f"'{t.value}'" for t in ImpactType]) 
    
    # --- UPDATED SYSTEM PROMPT with Confidence and Type Logic ---
    system_prompt = (
        "You are an expert financial analyst. Your task is to determine the stock ticker, "
        "directional impact, **confidence score**, and **impact type** for every relevant entity "
        "mentioned in the news story. You MUST analyze the entire context (content, entities, sentiment) "
        "to generate the final structured output."
        
        "\n\nStory Content:\n{story_text}"
        "\n\nExtracted Companies:\n{companies_list}"
        "\n\nExtracted Sectors:\n{sectors_list}"
        "\n\nExtracted Regulators:\n{regulators_list}"
        "\n\nSentiment (for context):\n{sentiment}"
        
        "\n\n*** Process Instructions: ***"
        "\n1. For every named company, CALL the `resolve_company_ticker` tool to get its stock ticker. This will be the 'symbol'."
        "\n2. For sector or regulatory impacts, choose an appropriate symbol (e.g., 'TECH_SECTOR', 'RBI_ACTION')."
        "\n3. **Confidence Rules (MUST be applied strictly):**"
        "\n   - **Direct Mention (type='direct'):** Confidence MUST be **1.0**."
        "\n   - **Sector-Wide Impact (type='sector'):** Confidence MUST be between **0.60 and 0.80**."
        "\n   - **Regulatory Impact (type='regulatory'):** Confidence MUST be between **0.80 and 0.95**."
        "\n4. The 'type' MUST be one of: " + impact_types_str + "."
        "\n5. The 'impact_direction' MUST be one of: 'POSITIVE', 'NEGATIVE', 'NEUTRAL', 'UNCLEAR'."
        "\n6. The final output must conform strictly to the required JSON schema."
    )
    # -------------------------------------------------------------

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Analyze the story and the extracted entities. Resolve all symbols and determine the financial impact (direction, confidence, and type). Output the final result using the structured JSON schema."),
    ])

    # 2. Bind Tools and Structure Output
    # This uses the imported ImpactedStockList Pydantic model
    structured_llm_with_tools = (
        llm.bind_tools(ALL_TOOLS) 
        .with_structured_output(ImpactedStockList)
    )

    # 3. Create Chain and Invoke
    chain = prompt | structured_llm_with_tools

    try:
        companies_list = ", ".join(current_story.entities.companies)
        sectors_list = ", ".join(current_story.entities.sectors)
        regulators_list = ", ".join(current_story.entities.regulators)
        
        # Invoke the chain, providing all context
        result: ImpactedStockList = chain.invoke({
            "story_text": current_story.text,
            "companies_list": companies_list,
            "sectors_list": sectors_list,
            "regulators_list": regulators_list,
            "sentiment": current_story.sentiment or "Neutral (Not Extracted)"
        })

        # 4. Update State
        current_story.impacted_stocks = result.impacts
        state.current_story = current_story
        state.status = "STOCKS_IMPACTED"
        
        print(f"SUCCESS: Determined {len(result.impacts)} stock impacts for Story ID: {current_story.unique_story_id[:8]}")
        print("Impact Details (JSON):\n" + result.json(indent=2))
        print(f"length of deduplication_groups : {len(state.deduplication_groups)}")

    except Exception as e:
        error_msg = f"ERROR in Impact Stock Agent: {e}"
        print(error_msg)
        state.error_message = error_msg
        state.status = "ERROR"
        return state

    return state
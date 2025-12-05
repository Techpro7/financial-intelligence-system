from financial_news_intel.core.models import (
    ConsolidatedStory, ExtractedEntity, ImpactedStock, ImpactType, ImpactDirection
)
from typing import List, Dict, Any

# --- HELPER FUNCTION: To simplify generating ImpactDirection and ImpactType strings ---
P = ImpactDirection.POSITIVE
N = ImpactDirection.NEGATIVE
U = ImpactDirection.UNCLEAR
T = ImpactDirection.NEUTRAL

DIR = ImpactType.DIRECT
REG = ImpactType.REGULATORY
SECT = ImpactType.SECTOR # CORRECTED: Changed from SECTORAL to SECTOR


# --- 1. Raw Input Articles (30 Articles, 20 Unique Stories) ---

RAW_INPUT_ARTICLES: List[Dict[str, Any]] = [
    # STORY 01 (TCS - Positive) - Articles 1, 2, 3 (Duplicates)
    {"title": "TCS shares surge 3% after announcing massive US contract", "link": "link_01", "summary": "Tata Consultancy Services (TCS) reported better-than-expected Q3 results and secured a landmark deal with a top US retailer, boosting market confidence.", "source": "ET Markets", "published_at": "2025-12-05T09:00:00Z"},
    {"title": "AI Deal Propels TCS Stock to All-Time High", "link": "link_02", "summary": "The major contract win by TCS is attributed to its advanced AI capabilities, leading to a strong buying momentum in its stock.", "source": "Business Today", "published_at": "2025-12-05T09:15:00Z"},
    {"title": "Tech Sector Cheers as TCS Closes Mega US Retail Deal", "link": "link_03", "summary": "TCS's performance and the large deal suggest a promising outlook for the entire Indian IT services sector.", "source": "CNBC-TV18", "published_at": "2025-12-05T09:30:00Z"},

    # STORY 02 (HDFC Bank - Negative) - Articles 4, 5 (Duplicates)
    {"title": "HDFC Bank faces penalty from RBI over KYC non-compliance", "link": "link_04", "summary": "The Reserve Bank of India (RBI) imposed a significant fine on HDFC Bank for deficiencies in regulatory compliance regarding KYC norms. Stock is down 1%.", "source": "The Hindu", "published_at": "2025-12-05T10:00:00Z"},
    {"title": "Banking Stocks Sink as RBI Slams HDFC Bank with Fine", "link": "link_05", "summary": "The RBI action against HDFC Bank has sent negative ripples across the private banking space, with ICICI Bank also seeing declines.", "source": "LiveMint", "published_at": "2025-12-05T10:15:00Z"},

    # STORY 03 (Maruti - Positive) - Articles 6, 7 (Duplicates)
    {"title": "Maruti Suzuki reports record sales for SUV segment", "link": "link_06", "summary": "Maruti Suzuki announced its highest-ever monthly sales figures, driven primarily by strong demand for its new SUV models. Analysts upgraded the stock.", "source": "NDTV Profit", "published_at": "2025-12-05T11:00:00Z"},
    {"title": "Auto Sector Roars: Maruti Sales Surge Boosts Investor Sentiment", "link": "link_07", "summary": "The strong sales performance of Maruti Suzuki has created optimism in the broader auto sector, suggesting robust consumer spending.", "source": "Financial Express", "published_at": "2025-12-05T11:15:00Z"},

    # STORY 04 (SUNPHARMA - Negative) - Article 8
    {"title": "USFDA issues warning letter to Sun Pharma manufacturing unit", "link": "link_08", "summary": "Sun Pharmaceutical Industries received an adverse inspection report from the USFDA concerning one of its key formulation plants, raising regulatory concerns.", "source": "MoneyControl", "published_at": "2025-12-05T12:00:00Z"},

    # STORY 05 (HUL - Neutral) - Articles 9, 10 (Duplicates)
    {"title": "HUL maintains Q3 profit guidance, no major changes expected", "link": "link_09", "summary": "Hindustan Unilever (HUL) released a business update maintaining its previous guidance, signaling stability but lack of growth drivers.", "source": "Reuters", "published_at": "2025-12-05T13:00:00Z"},
    {"title": "FMCG Sector Quiet as HUL holds steady on earnings outlook", "link": "link_10", "summary": "The broader FMCG sector reacted neutrally as HUL's profit guidance met, but did not exceed, market expectations.", "source": "Business Standard", "published_at": "2025-12-05T13:15:00Z"},

    # STORY 06 (RIL - Positive) - Article 11
    {"title": "Reliance Industries green energy arm secures massive funding", "link": "link_11", "summary": "Reliance Industries Ltd (RIL) announced its new energy subsidiary raised a large round of foreign capital to accelerate its clean energy projects.", "source": "Economic Times", "published_at": "2025-12-05T14:00:00Z"},

    # STORY 07 (AIRTEL - Negative) - Article 12
    {"title": "Airtel loses market share to Jio in key metropolitan circles", "link": "link_12", "summary": "Bharti Airtel reported a slight loss in subscriber base in Delhi and Mumbai to rival Reliance Jio, causing concerns over tariff wars.", "source": "India Today", "published_at": "2025-12-05T15:00:00Z"},

    # STORY 08 (RBI - Neutral/Regulatory) - Article 13
    {"title": "RBI keeps key interest rates unchanged in monetary policy review", "link": "link_13", "summary": "The Monetary Policy Committee (MPC) of the RBI voted unanimously to maintain the repo rate at 6.5%, meeting market expectations.", "source": "Mint", "published_at": "2025-12-05T16:00:00Z"},

    # STORY 09 (PAYTM - Positive) - Article 14
    {"title": "Paytm receives final approval for its payment aggregator license", "link": "link_14", "summary": "One97 Communications (Paytm) announced it secured the crucial payment aggregator license from the RBI, removing a major regulatory overhang.", "source": "MoneyControl", "published_at": "2025-12-06T09:00:00Z"},

    # STORY 10 (INFY) - Negative
    {"title": "Infosys stock drops 4% as major client cancels transformation project", "link": "link_15", "summary": "Infosys (INFY) shares fell sharply after a surprise cancellation of a multi-year digital transformation contract by a large US banking client.", "source": "ET Markets", "published_at": "2025-12-06T10:00:00Z"},

    # STORY 11 (TATA MOTORS) - Neutral
    {"title": "Tata Motors launches new line of commercial EVs", "link": "link_16", "summary": "Tata Motors unveiled its new range of electric commercial vehicles, aimed at municipal corporations. The long-term outlook is positive, but near-term impact is neutral.", "source": "Business Today", "published_at": "2025-12-06T11:00:00Z"},

    # STORY 12 (DLF) - Positive
    {"title": "DLF sells out luxury project in Gurgaon in record time", "link": "link_17", "summary": "Realty major DLF announced a complete sell-out of its luxury housing project in Sector 63, Gurgaon, within 48 hours, highlighting strong demand.", "source": "The Hindu", "published_at": "2025-12-06T12:00:00Z"},

    # STORY 13 (CONCOR) - Negative
    {"title": "CONCOR shares slide as railway freight volumes disappoint", "link": "link_18", "summary": "Container Corporation of India (CONCOR) reported disappointing Q3 freight volumes due to slowing international trade, leading to stock weakness.", "source": "LiveMint", "published_at": "2025-12-06T13:00:00Z"},

    # STORY 14 (CIPLA - Positive) - Article 19
    {"title": "Cipla receives final USFDA approval for key generic drug", "link": "link_19", "summary": "Cipla announced the final approval from the USFDA to market a generic version of a high-demand epilepsy drug in the US.", "source": "NDTV Profit", "published_at": "2025-12-06T14:00:00Z"},

    # STORY 15 (ICICI Bank - Negative) - Articles 20, 21 (Duplicates)
    {"title": "ICICI Bank faces technical glitch, digital services disrupted for hours", "link": "link_20", "summary": "ICICI Bank's digital services were affected for several hours due to a technical outage, drawing attention from banking regulators and frustrating customers.", "source": "Financial Express", "published_at": "2025-12-06T15:00:00Z"},
    {"title": "Digital Outage Drags ICICI Bank Shares Down", "link": "link_21", "summary": "The significant technical disruption faced by ICICI Bank's mobile app and net banking caused a minor dip in its stock price amid concerns over operational resilience.", "source": "MoneyControl", "published_at": "2025-12-06T15:30:00Z"},

    # STORY 16 (JSW STEEL - Positive) - Article 22
    {"title": "JSW Steel targets massive capacity expansion by 2030", "link": "link_22", "summary": "JSW Steel announced aggressive plans to nearly double its domestic steel manufacturing capacity over the next five years, signaling long-term confidence.", "source": "Economic Times", "published_at": "2025-12-06T16:00:00Z"},

    # STORY 17 (SEBI - Neutral/Regulatory) - Article 23
    {"title": "SEBI amends rules for mutual fund liquidity risk management", "link": "link_23", "summary": "The Securities and Exchange Board of India (SEBI) notified minor tweaks to rules governing liquidity management for open-ended debt mutual funds.", "source": "Business Today", "published_at": "2025-12-06T17:00:00Z"},

    # STORY 18 (BAJAJ-AUTO) - Positive
    {"title": "Bajaj Auto posts strong double-digit growth in two-wheeler exports", "link": "link_24", "summary": "Bajaj Auto's global sales, particularly in the two-wheeler segment, saw a robust increase last month, beating street estimates.", "source": "Reuters", "published_at": "2025-12-07T09:00:00Z"},
    {"title": "Export Market Lifts Bajaj Auto Shares", "link": "link_25", "summary": "Strong export figures from Bajaj Auto underscore recovering demand in international markets, providing a positive catalyst for the stock.", "source": "The Hindu", "published_at": "2025-12-07T09:15:00Z"},

    # STORY 19 (WIPRO) - Negative
    {"title": "Wipro misses consensus estimates on margin performance", "link": "link_26", "summary": "Wipro reported quarterly results that were slightly below analyst consensus, citing project ramp-downs and margin pressure in its cloud division.", "source": "Mint", "published_at": "2025-12-07T10:00:00Z"},

    # STORY 20 (ONGC) - Positive
    {"title": "ONGC discovers new oil and gas reserves in western offshore block", "link": "link_27", "summary": "Oil and Natural Gas Corporation (ONGC) announced a major new discovery of hydrocarbon reserves, which could significantly boost its production outlook.", "source": "Economic Times", "published_at": "2025-12-07T11:00:00Z"},
    {"title": "Major Hydrocarbon Discovery Fuels ONGC Stock", "link": "link_28", "summary": "The new oil and gas find by ONGC is viewed as a substantial positive for the public sector undertaking (PSU) energy giant and the entire energy sector.", "source": "LiveMint", "published_at": "2025-12-07T11:15:00Z"},
    {"title": "Government praises ONGC for successful offshore exploration", "link": "link_29", "summary": "Official government sources commented positively on ONGC's latest exploration success, hinting at future production increases.", "source": "NDTV Profit", "published_at": "2025-12-07T11:30:00Z"},
    {"title": "Energy Sector Outlook Brightens with ONGC's Reserve Addition", "link": "link_30", "summary": "ONGC's successful exploration validates the potential of India's western offshore region and provides a positive outlook for energy security.", "source": "Financial Express", "published_at": "2025-12-07T11:45:00Z"},
]

# --- 2. Ground Truth Mapping (20 Unique Stories) ---

GROUND_TRUTH_MAP: Dict[str, ConsolidatedStory] = {
    # STORY 01 (TCS) - Positive
    "TCS_AI_CONTRACT": ConsolidatedStory(
        unique_story_id="TCS_AI_CONTRACT", sentiment=P,
        text="Tata Consultancy Services (TCS) secured a massive landmark deal with a top US retailer, attributed to its advanced AI capabilities, and reported strong Q3 results, boosting the stock and the broader IT sector.",
        entities=ExtractedEntity(companies=["TCS", "Tata Consultancy Services"], sectors=["Technology", "IT"]),
        impacted_stocks=[ImpactedStock(company_name="TCS", stock_ticker="TCS", impact_direction=P, type=DIR, confidence=1.0)],
    ),
    # STORY 02 (HDFC) - Negative
    "HDFC_RBI_FINE": ConsolidatedStory(
        unique_story_id="HDFC_RBI_FINE", sentiment=N,
        text="The RBI imposed a significant fine on HDFC Bank for KYC non-compliance, sending negative ripples across the private banking sector.",
        entities=ExtractedEntity(companies=["HDFC Bank", "ICICI Bank"], regulators=["RBI"]),
        impacted_stocks=[ImpactedStock(company_name="HDFC Bank", stock_ticker="HDFCBANK", impact_direction=N, type=REG, confidence=0.9)],
    ),
    # STORY 03 (MARUTI) - Positive
    "MARUTI_RECORD_SALES": ConsolidatedStory(
        unique_story_id="MARUTI_RECORD_SALES", sentiment=P,
        text="Maruti Suzuki reported record monthly sales, driven primarily by strong demand for its new SUV models, boosting investor sentiment in the broader auto sector.",
        entities=ExtractedEntity(companies=["Maruti Suzuki"], sectors=["Auto"]),
        impacted_stocks=[ImpactedStock(company_name="Maruti Suzuki", stock_ticker="MARUTI", impact_direction=P, type=DIR, confidence=1.0)],
    ),
    # STORY 04 (SUNPHARMA) - Negative
    "SUNPHARMA_USFDA": ConsolidatedStory(
        unique_story_id="SUNPHARMA_USFDA", sentiment=N,
        text="Sun Pharmaceutical Industries received an adverse USFDA warning letter regarding one of its key manufacturing units, raising regulatory and stock concerns.",
        entities=ExtractedEntity(companies=["Sun Pharmaceutical Industries", "Sun Pharma"], regulators=["USFDA"]),
        impacted_stocks=[ImpactedStock(company_name="Sun Pharma", stock_ticker="SUNPHARMA", impact_direction=N, type=REG, confidence=0.85)],
    ),
    # STORY 05 (HUL) - Neutral
    "HUL_GUIDANCE": ConsolidatedStory(
        unique_story_id="HUL_GUIDANCE", sentiment=T,
        text="Hindustan Unilever (HUL) released a business update maintaining its previous profit guidance, signaling stability but resulting in a neutral reaction across the FMCG sector.",
        entities=ExtractedEntity(companies=["Hindustan Unilever", "HUL"], sectors=["FMCG"]),
        impacted_stocks=[ImpactedStock(company_name="HUL", stock_ticker="HINDUNILVR", impact_direction=T, type=DIR, confidence=1.0)],
    ),
    # STORY 06 (RIL) - Positive
    "RIL_GREEN_FUNDING": ConsolidatedStory(
        unique_story_id="RIL_GREEN_FUNDING", sentiment=P,
        text="Reliance Industries Ltd (RIL) announced its new energy subsidiary raised a large round of foreign capital to accelerate its clean energy projects.",
        entities=ExtractedEntity(companies=["Reliance Industries Ltd", "RIL"]),
        impacted_stocks=[ImpactedStock(company_name="RIL", stock_ticker="RELIANCE", impact_direction=P, type=DIR, confidence=0.9)],
    ),
    # STORY 07 (AIRTEL) - Negative
    "AIRTEL_MARKET_SHARE": ConsolidatedStory(
        unique_story_id="AIRTEL_MARKET_SHARE", sentiment=N,
        text="Bharti Airtel reported a slight loss in subscriber base to rival Reliance Jio in key metropolitan circles, causing concerns over tariff wars and market share.",
        entities=ExtractedEntity(companies=["Bharti Airtel", "Reliance Jio"]),
        impacted_stocks=[ImpactedStock(company_name="Bharti Airtel", stock_ticker="BHARTIARTL", impact_direction=N, type=DIR, confidence=0.8)],
    ),
    # STORY 08 (RBI) - Neutral/Regulatory
    "RBI_REPO_RATE": ConsolidatedStory(
        unique_story_id="RBI_REPO_RATE", sentiment=T,
        text="The Monetary Policy Committee (MPC) of the RBI voted unanimously to maintain the repo rate at 6.5%, meeting market expectations and leading to a neutral policy impact.",
        entities=ExtractedEntity(regulators=["Reserve Bank of India", "RBI"]),
        impacted_stocks=[ImpactedStock(company_name="RBI Policy", stock_ticker="NIFTY50", impact_direction=T, type=REG, confidence=1.0)],
    ),
    # STORY 09 (PAYTM) - Positive
    "PAYTM_LICENSE": ConsolidatedStory(
        unique_story_id="PAYTM_LICENSE", sentiment=P,
        text="One97 Communications (Paytm) secured the crucial payment aggregator license from the RBI, removing a major regulatory overhang and boosting the stock.",
        entities=ExtractedEntity(companies=["Paytm", "One97 Communications"]),
        impacted_stocks=[ImpactedStock(company_name="Paytm", stock_ticker="PAYTM", impact_direction=P, type=REG, confidence=0.95)],
    ),
    # STORY 10 (INFY) - Negative
    "INFY_CONTRACT_CANCEL": ConsolidatedStory(
        unique_story_id="INFY_CONTRACT_CANCEL", sentiment=N,
        text="Infosys (INFY) shares fell sharply after a surprise cancellation of a multi-year digital transformation contract by a large US banking client.",
        entities=ExtractedEntity(companies=["Infosys", "INFY"]),
        impacted_stocks=[ImpactedStock(company_name="Infosys", stock_ticker="INFY", impact_direction=N, type=DIR, confidence=1.0)],
    ),
    # STORY 11 (TATA MOTORS) - Neutral
    "TATAMOTORS_EV_LAUNCH": ConsolidatedStory(
        unique_story_id="TATAMOTORS_EV_LAUNCH", sentiment=T,
        text="Tata Motors unveiled a new line of electric commercial vehicles aimed at municipal corporations, with a positive long-term but neutral near-term stock impact.",
        entities=ExtractedEntity(companies=["Tata Motors"]),
        impacted_stocks=[ImpactedStock(company_name="Tata Motors", stock_ticker="TATAMOTORS", impact_direction=T, type=DIR, confidence=0.7)],
    ),
    # STORY 12 (DLF) - Positive
    "DLF_SELLOUT": ConsolidatedStory(
        unique_story_id="DLF_SELLOUT", sentiment=P,
        text="Realty major DLF announced a complete sell-out of its luxury housing project in Gurgaon within 48 hours, highlighting strong demand in the real estate sector.",
        entities=ExtractedEntity(companies=["DLF", "Realty major"]),
        impacted_stocks=[ImpactedStock(company_name="DLF", stock_ticker="DLF", impact_direction=P, type=DIR, confidence=1.0)],
    ),
    # STORY 13 (CONCOR) - Negative
    "CONCOR_FREIGHT": ConsolidatedStory(
        unique_story_id="CONCOR_FREIGHT", sentiment=N,
        text="Container Corporation of India (CONCOR) reported disappointing Q3 freight volumes due to slowing international trade, leading to stock weakness.",
        entities=ExtractedEntity(companies=["Container Corporation of India", "CONCOR"]),
        impacted_stocks=[ImpactedStock(company_name="CONCOR", stock_ticker="CONCOR", impact_direction=N, type=DIR, confidence=0.9)],
    ),
    # STORY 14 (CIPLA - Positive)
    "CIPLA_USFDA_APPROVAL": ConsolidatedStory(
        unique_story_id="CIPLA_USFDA_APPROVAL", sentiment=P,
        text="Cipla received final USFDA approval to market a generic version of a high-demand epilepsy drug in the US market.",
        entities=ExtractedEntity(companies=["Cipla"], regulators=["USFDA"]),
        impacted_stocks=[ImpactedStock(company_name="Cipla", stock_ticker="CIPLA", impact_direction=P, type=REG, confidence=0.9)],
    ),
    # STORY 15 (ICICI) - Negative
    "ICICI_OUTAGE": ConsolidatedStory(
        unique_story_id="ICICI_OUTAGE", sentiment=N,
        text="ICICI Bank's digital services were affected for several hours due to a technical outage, drawing attention from regulators and causing a minor dip in its stock price.",
        entities=ExtractedEntity(companies=["ICICI Bank"]),
        impacted_stocks=[ImpactedStock(company_name="ICICI Bank", stock_ticker="ICICIBANK", impact_direction=N, type=DIR, confidence=0.85)],
    ),
    # STORY 16 (JSW STEEL) - Positive
    "JSW_EXPANSION": ConsolidatedStory(
        unique_story_id="JSW_EXPANSION", sentiment=P,
        text="JSW Steel announced aggressive plans to nearly double its domestic steel manufacturing capacity over the next five years, signaling long-term confidence.",
        entities=ExtractedEntity(companies=["JSW Steel"]),
        impacted_stocks=[ImpactedStock(company_name="JSW Steel", stock_ticker="JSWSTEEL", impact_direction=P, type=DIR, confidence=0.9)],
    ),
    # STORY 17 (SEBI) - Neutral/Regulatory
    "SEBI_MF_RULES": ConsolidatedStory(
        unique_story_id="SEBI_MF_RULES", sentiment=T,
        text="SEBI notified minor tweaks to rules governing liquidity management for open-ended debt mutual funds, resulting in a neutral market reaction.",
        entities=ExtractedEntity(regulators=["SEBI"]),
        impacted_stocks=[ImpactedStock(company_name="SEBI Rules", stock_ticker="NIFTY", impact_direction=T, type=REG, confidence=0.9)],
    ),
    # STORY 18 (BAJAJ-AUTO) - Positive
    "BAJAJ_AUTO_EXPORTS": ConsolidatedStory(
        unique_story_id="BAJAJ_AUTO_EXPORTS", sentiment=P,
        text="Bajaj Auto posted strong double-digit growth in two-wheeler exports, beating street estimates and underscoring recovering international market demand.",
        entities=ExtractedEntity(companies=["Bajaj Auto"]),
        impacted_stocks=[ImpactedStock(company_name="Bajaj Auto", stock_ticker="BAJAJ-AUTO", impact_direction=P, type=DIR, confidence=1.0)],
    ),
    # STORY 19 (WIPRO) - Negative
    "WIPRO_MARGIN_MISS": ConsolidatedStory(
        unique_story_id="WIPRO_MARGIN_MISS", sentiment=N,
        text="Wipro reported quarterly results slightly below analyst consensus, citing margin pressure and project ramp-downs in its cloud division.",
        entities=ExtractedEntity(companies=["Wipro"]),
        impacted_stocks=[ImpactedStock(company_name="Wipro", stock_ticker="WIPRO", impact_direction=N, type=DIR, confidence=0.95)],
    ),
    # STORY 20 (ONGC) - Positive
    "ONGC_OIL_DISCOVERY": ConsolidatedStory(
        unique_story_id="ONGC_OIL_DISCOVERY", sentiment=P,
        text="Oil and Natural Gas Corporation (ONGC) announced a major new discovery of oil and gas reserves in the western offshore block, a substantial positive for the energy sector.",
        entities=ExtractedEntity(companies=["ONGC"], sectors=["Energy"]),
        impacted_stocks=[ImpactedStock(company_name="ONGC", stock_ticker="ONGC", impact_direction=P, type=DIR, confidence=1.0)],
    ),
}
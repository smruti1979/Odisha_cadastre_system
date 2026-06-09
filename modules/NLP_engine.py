import pandas as pd
from rapidfuzz import process, fuzz

def resolve_identity_by_name(search_query: str, target_df: pd.DataFrame, threshold: int = 55) -> pd.DataFrame:
    """
    Advanced AI Identity Matcher. Upgraded to partial_ratio scoring to safely
    resolve isolated single-word spelling typos (like 'Mapatra') against multi-word lines.
    """
    if not search_query or target_df.empty:
        return pd.DataFrame(columns=target_df.columns)
        
    # Clean and lower the search string to maximize match capability
    clean_query = search_query.strip().lower()
    
    # Store standard evaluation comparison lists
    en_names = target_df['tenant_name_en'].dropna().unique()
    or_names = target_df['tenant_name_or'].dropna().unique()
    
    # FIX: Swapped to fuzz.partial_ratio to allow sub-string typo tracking (e.g. Mapatra -> Mohapatra)
    matched_en = process.extract(clean_query, en_names, scorer=fuzz.partial_ratio, score_cutoff=threshold)
    matched_or = process.extract(clean_query, or_names, scorer=fuzz.partial_ratio, score_cutoff=threshold)
    
    # Correctly unpack RapidFuzz result tuples to isolate raw matching strings
    valid_names_en = [item[0] for item in matched_en] if matched_en else []
    valid_names_or = [item[0] for item in matched_or] if matched_or else []
    
    # Query matching data slices from the master dataframe
    resolved_df = target_df[
        target_df['tenant_name_en'].str.lower().isin([name.lower() for name in valid_names_en]) | 
        target_df['tenant_name_or'].isin(valid_names_or)
    ].copy()
    
    # Inject computed validation accuracy metrics back into the display table
    if not resolved_df.empty:
        resolved_df['ai_confidence_score'] = resolved_df['tenant_name_en'].apply(
            lambda x: float(fuzz.partial_ratio(clean_query, x.lower()))
        )
        return resolved_df.sort_values(by='ai_confidence_score', ascending=False)
        
    return resolved_df
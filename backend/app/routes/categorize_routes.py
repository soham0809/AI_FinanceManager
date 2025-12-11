"""Vendor categorization endpoint (simple heuristic)"""
from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/v1", tags=["categorize"])

# Basic keyword → category mapping (extend as needed)
CATEGORY_MAP = {
    "food & dining": ["swiggy", "zomato", "domino", "pizza", "kfc", "mcd"],
    "shopping": ["amazon", "flipkart", "myntra", "ajio", "meesho"],
    "transportation": ["uber", "ola", "rapido"],
    "utilities": ["jio", "airtel", "vi ", "vodafone", "bsnl", "electric", "gas"],
    "entertainment": ["netflix", "spotify", "prime video", "hotstar", "zee"],
    "education": ["coursera", "udemy", "byju", "unacademy"],
    "financial": ["hdfc", "icici", "sbi", "axis", "canara"],
    "fuel": ["hpcl", "bpcl", "ioc", "indianoil", "shell"],
}

@router.post("/categorize")
async def categorize_vendor(vendor: str = Query(..., min_length=2, description="Vendor/Merchant name")):
    """Categorize a vendor name into a spending category using simple heuristics.
    Returns { success, vendor, category, confidence }.
    """
    try:
        v = (vendor or "").strip()
        if not v:
            raise HTTPException(status_code=400, detail="vendor is required")

        v_lower = v.lower()
        best_category = "Others"
        best_score = 0.4  # default low confidence

        for category, keywords in CATEGORY_MAP.items():
            for kw in keywords:
                if kw in v_lower:
                    # score by keyword match length; prefer earlier/bigger matches
                    score = min(0.95, 0.6 + len(kw) / max(6, len(v_lower)))
                    if score > best_score:
                        best_category = category.title()
                        best_score = score

        return {
            "success": True,
            "vendor": v,
            "category": best_category,
            "confidence": round(best_score, 2)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Categorization error: {str(e)}")
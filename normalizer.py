from thefuzz import process

# The "Golden List" of standard names
STANDARD_TESTS = {
    # --- DIABETES ---
    "HbA1c": ["hba1c", "glycated hemoglobin", "glycosylated hb", "hb a1c", "a1c", "hemoglobin a1c", "glyco hb"],
    "Fasting Glucose": ["fasting blood sugar", "fbs", "glucose fasting", "sugar fasting", "blood glucose (f)", "plasma glucose fasting"],
    "Post Prandial Glucose": ["ppbs", "post prandial blood sugar", "glucose pp", "blood glucose (pp)", "2 hr post prandial"],
    "Random Glucose": ["rbs", "random blood sugar", "glucose random", "b.s.r"],
    "Average Glucose": ["estimated average glucose", "eag", "avg glucose"],

    # --- LIPIDS (Crucial: Specific keys to avoid overlap) ---
    "Total Cholesterol": ["total cholesterol", "cholesterol total", "s. cholesterol", "serum cholesterol"],
    "HDL Cholesterol": ["hdl", "high density lipoprotein", "hdl cholesterol", "good cholesterol"],
    "LDL Cholesterol": ["ldl", "low density lipoprotein", "ldl cholesterol", "bad cholesterol", "ldl direct"],
    "VLDL Cholesterol": ["vldl", "very low density lipoprotein"],
    "Triglycerides": ["triglycerides", "tgl", "s. triglycerides", "serum triglycerides"],
    # Ratios: Added extra aliases to catch "HDL Ratio" or "Risk Ratio"
    "Total/HDL Ratio": ["chol/hdl ratio", "tc/hdl ratio", "risk ratio", "hdl ratio", "cholesterol/hdl ratio"],
    "LDL/HDL Ratio": ["ldl/hdl ratio", "ldl/hdl"],

    # --- THYROID ---
    "Thyroid Stimulating Hormone": ["tsh", "thyroid stimulating hormone", "thyrotropin", "t.s.h", "tsh ultrasensitive", "tsh 3rd gen"],
    "Total T3": ["total t3", "triiodothyronine", "t3 total"],
    "Total T4": ["total t4", "thyroxine", "t4 total"],
    "Free T3": ["ft3", "free triiodothyronine", "free t3"],
    "Free T4": ["ft4", "free thyroxine", "free t4"],
    "Anti-TPO": ["anti thyroid peroxidase", "anti tpo", "tpo antibodies"],

    # --- COMPLETE BLOOD COUNT (CBC) ---
    "Hemoglobin": ["hemoglobin", "hb", "hgb", "haemoglobin"],
    "PCV / Hematocrit": ["pcv", "packed cell volume", "hematocrit", "hct"],
    "RBC Count": ["rbc", "red blood cell count", "erythrocyte count"],
    "MCV": ["mcv", "mean corpuscular volume", "mean cell volume"],
    "MCH": ["mch", "mean corpuscular hemoglobin", "mean cell hemoglobin"],
    "MCHC": ["mchc", "mean corpuscular hemoglobin concentration"],
    "RDW": ["rdw", "red cell distribution width", "rdw-cv", "rdw-sd"],
    "Total WBC Count": ["total wbc", "white blood cell count", "tlc", "total leucocyte count", "wbc count"],
    "Neutrophils": ["neutrophils", "polymorphs", "neutrophil %", "segs"],
    "Lymphocytes": ["lymphocytes", "lymphocyte %", "lymphos"],
    "Monocytes": ["monocytes", "monocyte %"],
    "Eosinophils": ["eosinophils", "eosinophil %"],
    "Basophils": ["basophils", "basophil %"],
    "Platelet Count": ["platelet count", "plt", "thrombocyte count", "platelets"],
    "ESR": ["erythrocyte sedimentation rate", "esr", "sed rate", "westergren"],

    # --- KIDNEY FUNCTION (KFT) ---
    "Creatinine": ["creatinine", "s. creatinine", "serum creatinine", "creat"],
    "Blood Urea Nitrogen": ["bun", "blood urea nitrogen"],
    "Urea": ["urea", "blood urea", "serum urea"],
    "Uric Acid": ["uric acid", "s. uric acid", "serum uric acid"],
    "Calcium": ["calcium", "s. calcium", "total calcium"],
    "eGFR": ["egfr", "estimated gfr", "glomerular filtration rate"],

    # --- LIVER FUNCTION (LFT) ---
    "Total Bilirubin": ["total bilirubin", "t. bilirubin", "bilirubin total"],
    "Direct Bilirubin": ["direct bilirubin", "d. bilirubin", "conjugated bilirubin"],
    "Indirect Bilirubin": ["indirect bilirubin", "unconjugated bilirubin"],
    "SGOT / AST": ["sgot", "ast", "aspartate aminotransferase", "serum aspartate transaminase"],
    "SGPT / ALT": ["sgpt", "alt", "alanine aminotransferase", "serum alanine transaminase"],
    "Alkaline Phosphatase": ["alp", "alkaline phosphatase", "s. alp"],
    "Total Protein": ["total protein", "s. protein", "protein total"],
    "Albumin": ["albumin", "s. albumin"],
    "Globulin": ["globulin"],
    "A/G Ratio": ["a/g ratio", "albumin globulin ratio"],
    "GGT": ["ggt", "gamma glutamyl transferase", "gamma gt"],

    # --- VITAMINS & MINERALS ---
    "Vitamin D": ["vitamin d", "25-oh vitamin d", "total vitamin d", "25 hydroxy cholecalciferol"],
    "Vitamin B12": ["vitamin b12", "cobalamin", "cyanocobalamin"],
    "Iron": ["iron", "serum iron", "fe"],
    "Ferritin": ["ferritin", "serum ferritin"],
    "TIBC": ["tibc", "total iron binding capacity"],
    "Transferrin Saturation": ["transferrin saturation", "tsat"],

    # --- ELECTROLYTES ---
    "Sodium": ["sodium", "na+", "serum sodium"],
    "Potassium": ["potassium", "k+", "serum potassium"],
    "Chloride": ["chloride", "cl-", "serum chloride"],

    # --- URINE EXAMINATION ---
    "Urine Color": ["urine colour", "color", "physical examination color"],
    "Urine pH": ["urine ph", "reaction"],
    "Specific Gravity": ["specific gravity", "sp. gravity"],
    "Urine Protein/Albumin": ["urine protein", "urine albumin", "albumin (urine)"],
    "Urine Sugar/Glucose": ["urine sugar", "urine glucose", "glucose (urine)"],
    "Urine Ketones": ["urine ketone", "ketones", "acetone"],
    "Urine Pus Cells": ["pus cells", "leukocytes", "wbc (urine)"],
    "Urine RBCs": ["urine rbc", "red blood cells (urine)"],
    "Urine Epithelial Cells": ["epithelial cells"],
    "Urine Casts": ["casts"],
    "Urine Crystals": ["crystals"]
}

def normalize_test_name(raw_name):
    if not raw_name: return "Unknown"
    raw_lower = str(raw_name).lower().strip()
    
    # 1. Exact Match Check
    for std, aliases in STANDARD_TESTS.items():
        if raw_lower == std.lower() or raw_lower in aliases:
            return std

    # 2. Fuzzy Match
    all_options = []
    for std, aliases in STANDARD_TESTS.items():
        for alias in aliases:
            all_options.append((alias, std))
    
    choices = [x[0] for x in all_options]
    best_match, score = process.extractOne(raw_lower, choices)
    
    # 90% Threshold prevents False Positives (e.g. "Vitamin D" matching "Vitamin B12")
    if score >= 90:
        for alias, std in all_options:
            if alias == best_match:
                return std

    return raw_name.title()
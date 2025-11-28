from thefuzz import process

# The "Golden List" of standard names
STANDARD_TESTS = {
    # --- DIABETES ---
    "HbA1c": ["hba1c", "glycated hemoglobin", "glycosylated hb", "hb a1c", "a1c", "hemoglobin a1c", "glyco hb"],
    "Fasting Glucose": ["fasting blood sugar", "fbs", "glucose fasting", "sugar fasting", "blood glucose (f)", "plasma glucose fasting", "fasting blood sugar(glucose)", "blood sugar (f)"],
    "Post Prandial Glucose": ["ppbs", "post prandial blood sugar", "glucose pp", "blood glucose (pp)", "2 hr post prandial"],
    "Random Glucose": ["rbs", "random blood sugar", "glucose random", "b.s.r"],
    "Average Glucose": ["estimated average glucose", "eag", "avg glucose", "average blood glucose (abg)"],

    # --- LIPIDS ---
    "Total Cholesterol": ["total cholesterol", "cholesterol total", "s. cholesterol", "serum cholesterol"],
    "HDL Cholesterol": ["hdl", "high density lipoprotein", "hdl cholesterol", "good cholesterol", "hdl cholesterol direct", "hdlc", 'hdl cholesterol, serum'],
    "LDL Cholesterol": ["ldl", "low density lipoprotein", "ldl cholesterol", "bad cholesterol", "ldl cholesterol direct", "ldl direct", "ldlc", 'ldl cholesterol, serum', 'low density lipoprotein-cholesterol, serum', 'low density lipoprotein-cholesterol', 'low density lipoprotein-cholesterol (ldl)'],
    "VLDL Cholesterol": ["vldl", "very low density lipoprotein", "vldl cholesterol", "vldlc"],
    "Non-HDL Cholesterol": ["non-hdl cholesterol", "non hdl", "cholesterol non hdl"], # <--- NEW
    "Triglycerides": ["triglycerides", "tgl", "s. triglycerides", "serum triglycerides"],
    
    # Ratios
    "Total Cholesterol/HDL Ratio": ["chol/hdl ratio", "tc/hdl cholesterol ratio", "risk ratio", "hdl ratio", "cholesterol/hdl ratio", "tc/ hdl cholesterol ratio", "tc/hdlc ratio", "tc/hdlc"],
    "LDL/HDL Ratio": ["ldl/hdl ratio", "ldl/hdl", "ldlc/hdlc ratio", "ldlc/hdlc"],
    "HDL/LDL Ratio": ["hdl/ldl ratio", "hdl/ldl", "hdlc/ldlc ratio", "hdlc/ldlc"], # <--- NEW
    "Trig/HDL Ratio": ["trig/hdl ratio", "triglycerides/hdl ratio", "tgl/hdl ratio", "triglycerides/hdlc ratio", "triglycerides/hdlc", "tgl/hdlc"], # <--- NEW
    

    # --- THYROID ---
    "Thyroid Stimulating Hormone": ["tsh", "thyroid stimulating hormone", "thyrotropin", "t.s.h", "tsh ultrasensitive", "tsh-ultrasensitive", "tsh 3rd gen"],
    "Total T3": ["total t3", "triiodothyronine", "t3 total", "total triiodothyronine", "total triiodothyronine (t3)"],
    "Total T4": ["total t4", "thyroxine", "t4 total", "total thyroxine", "total thyroxine (t4)"],
    "Free T3": ["ft3", "free triiodothyronine", "free t3"],
    "Free T4": ["ft4", "free thyroxine", "free t4"],
    "Anti-TPO": ["anti thyroid peroxidase", "anti tpo", "tpo antibodies"],

    # --- COMPLETE BLOOD COUNT (CBC) ---
    "Hemoglobin": ["hemoglobin", "hb", "hgb", "haemoglobin"],
    "PCV or Hematocrit": ["pcv", "packed cell volume", "hematocrit", "hct", "hematocrit(pcv)"],
    "RBC Count": ["rbc", "red blood cell count", "erythrocyte count", "total rbc"],
    "MCV": ["mcv", "mean corpuscular volume", "mean cell volume", "mean corpuscular volume (mcv)"],
    "MCH": ["mch", "mean corpuscular hemoglobin", "mean cell hemoglobin", "mean corpuscular hemoglobin (mch)", "corpuscular hemoglobin(mch)"],
    "MCHC": ["mchc", "mean corpuscular hemoglobin concentration", "corp.hemo.conc(mchc)", "mean corp. hemo. conc (mchc)"],
    "RDW": ["rdw", "red cell distribution width", "rdw-cv", "red cell distribution width (rdw-cv)", "red cell distribution width cv"], # Kept CV as standard RDW usually
    "RDW-SD": ["rdw-sd", "red cell distribution width-sd(rdw-sd)", "red cell distribution width - sd (rdw-sd)", "red cell distribution width sd"], # <--- NEW
    "Mentzer Index": ["mentzer index", "mi"], # <--- NEW
    "RDWI": ["rdwi", "red cell distribution width index"], # <--- NEW
    
    # WBCs
    "Total WBC Count": ["total wbc", "white blood cell count", "tlc", "total leucocyte count", "wbc count", "total leucocyte count (wbc)"],
    "Neutrophils %": ["neutrophils", "polymorphs", "neutrophil %", "segs", "neutrophils percentage"],
    "Lymphocytes %": ["lymphocytes", "lymphocyte %", "lymphos", "lymphocytes percentage", "lymphocyte"],
    "Monocytes %": ["monocytes", "monocyte %", "monocytes percentage"],
    "Eosinophils %": ["eosinophils", "eosinophil %", "eosinophils percentage"],
    "Basophils %": ["basophils", "basophil %", "basophils percentage"],
    "Immature Granulocytes %": ["immature granulocyte percentage (ig%)", "ig%"], # <--- NEW
    
    # Absolute Counts (Important to distinguish from %)
    "Neutrophils - Absolute": ["neutrophils absolute count", "neutrophils - absolute count", "absolute neutrophils"],
    "Lymphocytes - Absolute": ["lymphocytes absolute count", "lymphocytes - absolute count", "absolute lymphocytes"],
    "Monocytes - Absolute": ["monocytes absolute count", "monocytes - absolute count", "absolute monocytes"],
    "Eosinophils - Absolute": ["eosinophils absolute count", "eosinophils - absolute count", "absolute eosinophils"],
    "Basophils - Absolute": ["basophils absolute count", "basophils - absolute count", "absolute basophils"],
    "Immature Granulocytes - Absolute": ["immature granulocytes (ig)", "immature granulocytes absolute"],
    
    "Platelet Count": ["platelet count", "plt", "thrombocyte count", "platelets"],
    "Mean Platelet Volume (MPV)": ["mpv", "mean platelet volume", "mean platelet volume (mpv)", "platelet volume (mpv)"],
    "ESR": ["erythrocyte sedimentation rate", "esr", "sed rate", "westergren", "erythrocyte sedimentation rate (esr)"],

    # --- KIDNEY FUNCTION (KFT) ---
    "Creatinine": ["creatinine", "s. creatinine", "serum creatinine", "creat", "creatinine - serum"],
    "Blood Urea Nitrogen": ["bun", "blood urea nitrogen", "blood urea nitrogen (bun)"],
    "BUN/Creatinine Ratio": ["bun/sr.creatinine ratio", "bun/creatinine ratio", "bun/creat ratio"],
    "Urea": ["urea", "blood urea", "serum urea", "urea (calculated)"],
    "Urea/Creatinine Ratio": ["urea / sr.creatinine ratio", "urea/creatinine ratio", "urea/creat ratio"],
    "Uric Acid": ["uric acid", "s. uric acid", "serum uric acid"],
    "Calcium": ["calcium", "s. calcium", "total calcium"],
    "eGFR": ["egfr", "estimated gfr", "glomerular filtration rate", "est. glomerular filtration rate (egfr)", "egfr (estimated glomerular filtration rate)", "estimated glomerular filtration rate (egfr)", "estimated glomerular filtration rate"],
    "Phosphorous": ["phosphorous", "phosphate", "serum phosphorous"], # <--- NEW from report
    "Magnesium": ["magnesium", "serum magnesium"], # <--- NEW from report

    # --- LIVER FUNCTION (LFT) ---
    "Total Bilirubin": ["total bilirubin", "t. bilirubin", "bilirubin total", "bilirubin - total"],
    "Direct Bilirubin": ["direct bilirubin", "d. bilirubin", "conjugated bilirubin", "bilirubin -direct"],
    "Indirect Bilirubin": ["indirect bilirubin", "unconjugated bilirubin", "bilirubin (indirect)"],
    "SGOT or AST": ["sgot", "ast", "aspartate aminotransferase", "serum aspartate transaminase", "aspartate aminotransferase (sgot)"],
    "SGPT or ALT": ["sgpt", "alt", "alanine aminotransferase", "serum alanine transaminase", "alanine transaminase (sgpt)"],
    "SGOT/SGPT Ratio": ["sgot/sgpt ratio", "ast/alt ratio"], # <--- NEW
    "Alkaline Phosphatase": ["alp", "alkaline phosphatase", "s. alp"],
    "Total Protein": ["total protein", "s. protein", "protein total", "protein - total"],
    "Albumin": ["albumin", "s. albumin", "albumin - serum"],
    "Globulin": ["globulin", "serum globulin"],
    "A/G Ratio": ["a/g ratio", "albumin globulin ratio", "serum alb/globulin ratio"],
    "GGT": ["ggt", "gamma glutamyl transferase", "gamma gt", "gamma glutamyl transferase (ggt)", "ggtp"],

    # --- VITAMINS & MINERALS ---
    "Vitamin D - Total": ["vitamin d", "25-oh vitamin d", "total vitamin d", "25-oh vitamin d (total)", "25 hydroxy cholecalciferol"],
    "Vitamin B12": ["vitamin b12", "cobalamin", "cyanocobalamin", "vitamin b-12"],
    "Iron": ["iron", "serum iron", "fe"],
    "Ferritin": ["ferritin", "serum ferritin"],
    "TIBC": ["tibc", "total iron binding capacity", "total iron binding capacity (tibc)"],
    "UIBC": ["uibc", "unsat.iron-binding capacity(uibc)", "unsaturated iron binding capacity"], # <--- NEW
    "Transferrin Saturation": ["transferrin saturation", "tsat", "% transferrin saturation"],

    # --- ELECTROLYTES ---
    "Sodium": ["sodium", "na+", "serum sodium"],
    "Potassium": ["potassium", "k+", "serum potassium"],
    "Chloride": ["chloride", "cl-", "serum chloride"],

    # --- URINE EXAMINATION ---
    "Urine Color": ["urine colour", "color", "physical examination color", "colour"],
    "Urine pH": ["urine ph", "reaction", "ph"],
    "Urine Specific Gravity": ["specific gravity", "sp. gravity"],
    "Urine Protein or Albumin": ["urine protein", "urine albumin", "albumin (urine)", "urinary protein"],
    "Urine Sugar or Glucose": ["urine sugar", "urine glucose", "glucose (urine)", "urinary glucose"],
    "Urine Ketones": ["urine ketone", "ketones", "acetone", "urine ketone"],
    "Urine Pus Cells": ["pus cells", "leukocytes", "wbc (urine)", "urinary leucocytes (pus cells)"],
    "Urine RBCs": ["urine rbc", "red blood cells (urine)", "red blood cells"],
    "Urine Epithelial Cells": ["epithelial cells"],
    "Urine Casts": ["casts"],
    "Urine Crystals": ["crystals"],
    "Urine Volume": ["volume"],
    "Urine Appearance": ["appearance"],
    "Urine Bilirubin": ["urinary bilirubin"],
    "Urine Urobilinogen": ["urobilinogen"],
    "Urine Nitrite": ["nitrite"],
    "Urine Blood": ["urine blood"],

    # --- METABOLIC PANEL ---
    "Lactate Dehydrogenase (LDH)": ["lactate dehydrogenase", "ldh", "lactate dehydrogenase (ldh)", "ldh (lactate dehydrogenase)"],

    # --- CANCER TESTS ---
    "PSA (Prostate Specific Antigen)": ["psa", "prostate specific antigen", "prostate specific antigen (psa)", "psa (prostate specific antigen)"]
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
    
    # 90% Threshold prevents False Positives
    if score >= 90:
        for alias, std in all_options:
            if alias == best_match:
                return std

    return raw_name.title()
TEST_CLUSTERS = {
    "Diabetes Profile": ["HbA1c", "Fasting Glucose", "Post Prandial Glucose", "Random Glucose", "Average Glucose"],
    "Lipid Profile": ["Total Cholesterol", "HDL Cholesterol", "LDL Cholesterol", "VLDL Cholesterol", "Triglycerides", "Total/HDL Ratio", "LDL/HDL Ratio"],
    "Thyroid Profile": ["Thyroid Stimulating Hormone", "Total T3", "Total T4", "Free T3", "Free T4", "Anti-TPO"],
    "Complete Blood Count (CBC)": ["Hemoglobin", "PCV / Hematocrit", "RBC Count", "MCV", "MCH", "MCHC", "RDW", "Total WBC Count", "Neutrophils", "Lymphocytes", "Monocytes", "Eosinophils", "Basophils", "Platelet Count", "ESR"],
    "Kidney Function (KFT)": ["Creatinine", "Blood Urea Nitrogen", "Urea", "Uric Acid", "Calcium", "eGFR"],
    "Liver Function (LFT)": ["Total Bilirubin", "Direct Bilirubin", "Indirect Bilirubin", "SGOT / AST", "SGPT / ALT", "Alkaline Phosphatase", "Total Protein", "Albumin", "Globulin", "A/G Ratio", "GGT"],
    "Vitamin & Mineral Profile": ["Vitamin D", "Vitamin B12", "Iron", "Ferritin", "TIBC", "Transferrin Saturation"],
    "Electrolytes": ["Sodium", "Potassium", "Chloride"],
    "Urine Routine": ["Urine Color", "Urine pH", "Specific Gravity", "Urine Protein/Albumin", "Urine Sugar/Glucose", "Urine Ketones", "Urine Pus Cells", "Urine RBCs", "Urine Epithelial Cells", "Urine Casts", "Urine Crystals"]
}

def get_related_tests(query_name):
    query_lower = query_name.lower()
    
    # 1. Check if the query IS a Cluster Name
    for group, tests in TEST_CLUSTERS.items():
        if query_lower in group.lower():
            return tests
            
    # 2. Check if the query is INSIDE a Cluster
    for group, tests in TEST_CLUSTERS.items():
        if any(t.lower() == query_lower for t in tests):
            return tests
            
    # 3. Fallback
    return [query_name]
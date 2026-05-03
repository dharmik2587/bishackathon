# enrich_standards.py
"""
Enriches standards.json with domain-specific descriptions,
synonyms, and richer context chunks.
Run ONCE before indexing.
"""

import json
import os

MANUAL_ENRICHMENT = {
    "IS 269: 1989": {
        "description": "33 Grade Ordinary Portland Cement - chemical and physical requirements including compressive strength, setting time, soundness, fineness",
        "keywords": ["cement", "portland", "ordinary", "opc", "33 grade", "binding", "mortar", "concrete", "construction", "chemical", "physical", "strength", "setting"],
        "contextChunks": [
            "IS 269: 1989 covers 33 Grade Ordinary Portland Cement. Specifies chemical composition requirements: silica, alumina, iron oxide, calcium oxide, magnesia, sulphuric anhydride. Physical requirements: fineness minimum 225 m²/kg, initial setting time minimum 30 minutes, final setting time maximum 600 minutes, compressive strength minimum 16 MPa at 3 days and 22 MPa at 7 days, soundness by Le Chatelier not exceeding 10mm.",
            "Use IS 269:1989 for manufacturing standard OPC 33 Grade cement used in general construction, masonry, plasterwork, and non-critical concrete work."
        ]
    },
    "IS 383: 1970": {
        "description": "Coarse and fine aggregates from natural sources for concrete - grading, quality, and testing requirements for river sand, crushed stone, gravel",
        "keywords": ["aggregate", "sand", "gravel", "coarse", "fine", "natural", "concrete", "river", "crushed stone", "grading", "sieve", "particle", "structural concrete"],
        "contextChunks": [
            "IS 383: 1970 specifies requirements for coarse and fine aggregates derived from natural sources for use in concrete. Covers grading requirements for fine aggregates (Zones I-IV), coarse aggregates (nominal sizes 40mm, 20mm, 16mm, 12.5mm, 10mm), quality requirements for deleterious materials, organic impurities, clay, silt content, and mechanical properties.",
            "IS 383: 1970 applies to river sand, quarry sand, crushed stone sand, gravel, and crushed stone used as aggregates in structural and plain concrete. Mandatory for any concrete mix design under IS 456."
        ]
    },
    "IS 458: 2003": {
        "description": "Precast concrete pipes with and without reinforcement for water mains, drainage, sewerage, culverts",
        "keywords": ["precast", "concrete", "pipe", "reinforcement", "reinforced", "water main", "drainage", "culvert", "sewerage", "non-pressure", "pressure", "rcc pipe"],
        "contextChunks": [
            "IS 458: 2003 specifies requirements for precast concrete pipes both with and without reinforcement intended for use as water mains, drains, sewers, and culverts. Covers NP (non-pressure) and P (pressure) classes. Specifies dimensions, tolerances, materials, reinforcement, concrete mix, testing including three-edge bearing test and hydrostatic test.",
            "IS 458: 2003 applies to manufacturing of precast RCC pipes and plain concrete pipes for gravity flow and pressure applications in water supply and sanitation infrastructure."
        ]
    },
    "IS 2185 (Part 2): 1983": {
        "description": "Hollow and solid lightweight concrete masonry blocks - dimensions, compressive strength, water absorption requirements",
        "keywords": ["concrete", "block", "masonry", "hollow", "solid", "lightweight", "aac", "cellular", "dimensions", "wall", "partition", "aggregate", "pumice", "cinder"],
        "contextChunks": [
            "IS 2185 (Part 2): 1983 specifies requirements for hollow and solid lightweight concrete masonry blocks made with lightweight aggregates such as pumice, cinder, blast furnace slag, or expanded clay/shale. Covers dimensions (nominal sizes), compressive strength requirements, water absorption limits, and testing procedures.",
            "IS 2185 Part 2 is the applicable standard for manufacturing lightweight concrete blocks used in load-bearing and non-load-bearing walls and partitions."
        ]
    },
    "IS 459: 1992": {
        "description": "Corrugated and semi-corrugated asbestos cement sheets for roofing and cladding - profile dimensions, physical and mechanical requirements",
        "keywords": ["asbestos", "cement", "corrugated", "semi-corrugated", "roofing", "cladding", "sheet", "profile", "ac sheet", "industrial", "shed"],
        "contextChunks": [
            "IS 459: 1992 specifies requirements for corrugated and semi-corrugated asbestos cement sheets used for roofing and cladding of buildings. Covers profile dimensions, tolerances, water absorption, transverse breaking load, and impermeability tests.",
            "IS 459: 1992 applies to manufacturing of standard profile AC (asbestos cement) corrugated sheets for industrial sheds, warehouses, agricultural buildings, and residential roofing."
        ]
    },
    "IS 455: 1989": {
        "description": "Portland slag cement - manufactured by intergrinding or blending OPC clinker with granulated blast furnace slag",
        "keywords": ["cement", "portland", "slag", "psc", "blast furnace", "granulated", "intergrinding", "blending", "low heat", "sulphate resistance", "marine"],
        "contextChunks": [
            "IS 455: 1989 specifies requirements for Portland Slag Cement (PSC) manufactured by either intergrinding Portland cement clinker with granulated blast furnace slag or by intimately blending Portland cement with finely ground granulated blast furnace slag. Covers chemical and physical requirements including slag content (25-65%), compressive strength, setting time, soundness.",
            "Portland Slag Cement per IS 455: 1989 is preferred for marine structures, mass concrete, and sulfate-resistant applications due to lower heat of hydration and improved durability."
        ]
    },
    "IS 1489 (Part 2): 1991": {
        "description": "Portland Pozzolana Cement - Calcined clay based (PPC) - manufactured using calcined clay or calcined shale as pozzolanic material",
        "keywords": ["cement", "portland", "pozzolana", "ppc", "calcined clay", "calcined shale", "fly ash", "pozzolanic", "blended cement"],
        "contextChunks": [
            "IS 1489 (Part 2): 1991 specifies requirements for Portland Pozzolana Cement (PPC) of the calcined clay based variety. Pozzolanic material is calcined clay or calcined shale. Covers chemical requirements, pozzolana content (15-35% by mass), physical requirements including fineness, setting time, strength, soundness.",
            "IS 1489 Part 2 calcined clay based PPC is used for general construction, mass concrete, hydraulic structures, and where resistance to sulphate attack is needed."
        ]
    },
    "IS 3466: 1988": {
        "description": "Masonry cement for mortars in brick, stone, and block masonry - not for structural concrete, higher workability and plasticity",
        "keywords": ["cement", "masonry", "mortar", "brick", "stone", "block", "plaster", "workability", "plasticity", "general purpose", "non-structural"],
        "contextChunks": [
            "IS 3466: 1988 specifies requirements for masonry cement intended for use in mortars for masonry construction (brick, stone, concrete block). Masonry cement provides better workability and water retention than OPC but is NOT suitable for structural concrete. Covers compressive strength, setting time, fineness, air content.",
            "IS 3466: 1988 masonry cement is used exclusively for mortar preparation in masonry works, plastering, and pointing, not for structural concrete elements."
        ]
    },
    "IS 6909: 1990": {
        "description": "Supersulphated cement for marine works, sewage works, aggressive ground conditions - made from granulated blast furnace slag, calcium sulphate and OPC clinker",
        "keywords": ["supersulphated", "cement", "marine", "sulphate", "aggressive", "sewage", "chemical resistance", "slag", "calcium sulphate", "ground water", "seawater"],
        "contextChunks": [
            "IS 6909: 1990 specifies requirements for supersulphated cement manufactured from granulated blast furnace slag (80-85%), calcium sulphate (anhydrite or gypsum, 10-15%), and a small amount of Portland cement clinker (1-5%). Exhibits excellent resistance to sulphate attack, seawater, and aggressive ground conditions.",
            "IS 6909: 1990 supersulphated cement is specifically recommended for marine works, submerged foundations, sewage treatment plants, chemical plants, and any application involving contact with sulphate-bearing soils or aggressive waters."
        ]
    },
    "IS 8042: 1989": {
        "description": "White Portland cement for architectural, decorative, and ornamental work - low iron oxide content for white color",
        "keywords": ["white", "cement", "portland", "decorative", "architectural", "ornamental", "terrazzo", "mosaic", "precast", "color", "aesthetic", "low iron"],
        "contextChunks": [
            "IS 8042: 1989 specifies requirements for White Portland Cement characterized by very low iron oxide and manganese oxide content to achieve white color. Manufactured by careful selection of raw materials and fuel. Covers whiteness index, compressive strength, chemical and physical requirements.",
            "IS 8042: 1989 white Portland cement is used for architectural features, decorative concrete, terrazzo floors, exposed aggregate finishes, precast cladding panels, and any application requiring aesthetic white color."
        ]
    }
}

def enrich_standards(input_file: str, output_file: str):
    if not os.path.exists(input_file):
        print(f"Input file not found: {input_file}")
        return

    with open(input_file, 'r', encoding='utf-8') as f:
        standards = json.load(f)
    
    enriched_count = 0
    for std in standards:
        std_num = std.get('standardNumber', '')
        if std_num in MANUAL_ENRICHMENT:
            enrichment = MANUAL_ENRICHMENT[std_num]
            std['description'] = enrichment['description']
            std['keywords'] = enrichment['keywords']
            std['contextChunks'] = enrichment['contextChunks']
            enriched_count += 1
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(standards, f, indent=2)
    
    print(f"Enriched {enriched_count} standards")

if __name__ == '__main__':
    enrich_standards('../frontend/public/standards.json', '../frontend/public/standards_enriched.json')

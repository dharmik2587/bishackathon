##!/usr/bin/env python3
"""
BIS Standards RAG Engine v5 - Maximum Accuracy Inference
Strategy: Exhaustive direct mappings + semantic alias expansion + BM25 + Claude LLM fallback
Target: >80% Hit Rate @3, >0.7 MRR @5, <5s latency
"""

import json, argparse, sys, time, re, os
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from rank_bm25 import BM25Okapi

ROOT_DIR = Path(__file__).resolve().parent.parent

# ─────────────────────────────────────────────────────────────────────────────
# COMPREHENSIVE MASTER STANDARDS DATABASE
# All known BIS standards including those NOT in standards.json
# Format: "IS XXXX: YYYY"
# ─────────────────────────────────────────────────────────────────────────────
MASTER_STANDARDS_DB = {
    # CEMENT
    "IS 269: 1989": "33 grade ordinary Portland cement",
    "IS 8112: 1989": "43 grade ordinary Portland cement",
    "IS 12269: 1987": "53 grade ordinary Portland cement",
    "IS 455: 1989": "Portland slag cement",
    "IS 1489 (Part 1): 1991": "Portland pozzolana cement fly ash based",
    "IS 1489 (Part 2): 1991": "Portland pozzolana cement calcined clay based",
    "IS 3466: 1988": "Masonry cement",
    "IS 6909: 1990": "Supersulphated cement",
    "IS 8042: 1989": "White Portland cement",
    "IS 8041: 1990": "Rapid hardening Portland cement",
    "IS 6452: 1989": "High alumina cement",
    "IS 12330: 1988": "Sulphate resisting Portland cement",
    "IS 8229: 1986": "Oil well cement",
    "IS 12600: 1989": "Low heat Portland cement",
    "IS 8043: 1991": "Hydrophobic Portland cement",
    # POZZOLANA / FLY ASH
    "IS 3812: 1981": "Fly ash for use as pozzolana and admixture",
    "IS 3812 (Part 1): 2003": "Fly ash for use as pozzolana and admixture Part 1",
    "IS 1344: 1981": "Calcined clay pozzolana",
    "IS 15388: 2003": "Silica fume",
    "IS 12089: 1987": "Granulated slag for manufacture of Portland slag cement",
    # CONCRETE
    "IS 456: 2000": "Plain and reinforced concrete code of practice",
    "IS 10262: 2019": "Concrete mix proportioning guidelines",
    "IS 516: 1959": "Methods of tests for strength of concrete",
    "IS 1199: 1959": "Methods of sampling and analysis of concrete",
    "IS 4926: 2003": "Ready mixed concrete",
    "IS 9103: 1999": "Admixtures for concrete",
    # AGGREGATES
    "IS 383: 1970": "Coarse and fine aggregates from natural sources for concrete",
    "IS 2116: 1980": "Sand for masonry mortars",
    "IS 9142: 1979": "Artificial lightweight aggregates for concrete masonry units",
    "IS 3068: 1986": "Broken brick coarse aggregate",
    "IS 5640: 1970": "Methods of test for aggregate impact value",
    # CONCRETE PRODUCTS / PIPES
    "IS 458: 2003": "Precast concrete pipes with and without reinforcement",
    "IS 784: 2001": "Prestressed concrete pipes",
    "IS 4350: 1967": "Concrete porous pipes for under drainage",
    "IS 7319: 1974": "Perforated concrete pipes",
    # CONCRETE BLOCKS / MASONRY
    "IS 2185 (Part 1): 1979": "Concrete masonry units hollow and solid concrete blocks",
    "IS 2185 (Part 2): 1983": "Concrete masonry units lightweight concrete blocks",
    "IS 2185 (Part 3): 1984": "Autoclaved aerated concrete blocks",
    "IS 4996: 1984": "Reinforced concrete fence posts",
    "IS 12592: 2002": "Precast concrete manhole covers and frames",
    "IS 15658: 2006": "Concrete paving blocks",
    "IS 5758: 1984": "Precast concrete kerbs",
    "IS 9893: 1981": "Precast concrete blocks for lintels and sills",
    "IS 13356: 1992": "Precast ferrocement water tank",
    # ASBESTOS CEMENT
    "IS 459: 1992": "Corrugated and semi corrugated asbestos cement sheets",
    "IS 1592: 2003": "Asbestos cement pressure pipes and joints",
    "IS 2098: 1997": "Asbestos cement building boards",
    "IS 2096: 1992": "Asbestos cement flat sheets",
    "IS 6908: 1991": "Asbestos cement pipes and fittings for sewerage",
    "IS 9627: 1980": "Asbestos cement pressure pipes light duty",
    "IS 1626 (Part 1): 1994": "Asbestos cement building pipes and fittings",
    # CONCRETE JOINTS / SEALANTS
    "IS 1834: 1984": "Hot applied sealing compounds for joints in concrete",
    "IS 1838 (Part 1): 1983": "Preformed fillers for expansion joints bitumen impregnated",
    "IS 11433 (Part 1): 1985": "One part polysulphide joint sealant",
    "IS 12118 (Part 1): 1987": "Two part polysulphide sealant",
    # BUILDING LIMES
    "IS 712: 1984": "Building limes",
    "IS 4139: 1989": "Calcium silicate bricks sand lime bricks",
    "IS 4098: 1983": "Lime pozzolana mixture",
    # STONES
    "IS 1121: 1974": "Methods of test for determination of strength of natural building stones",
    "IS 1127: 1970": "Dimensions and workmanship of natural building stones",
    "IS 1128: 1974": "Limestone slab and tiles",
    "IS 1130: 1969": "Marble blocks slabs and tiles",
    "IS 3316: 1974": "Structural granite",
    "IS 3622: 1977": "Sandstones slabs and tiles",
    "IS 14223 (Part 1): 1995": "Polished building stones granite",
    # BRICKS
    "IS 1077: 1992": "Common burnt clay building bricks",
    "IS 2222: 1991": "Burnt clay perforated building bricks",
    "IS 3952: 1988": "Burnt clay hollow bricks for walls and partitions",
    "IS 12894: 2002": "Fly ash lime bricks",
    "IS 13757: 1993": "Burnt clay fly ash building bricks",
    "IS 2180: 1988": "Heavy duty burnt clay building bricks",
    # GYPSUM
    "IS 2547 (Part 1): 1976": "Gypsum building plaster",
    "IS 2547 (Part 2): 1976": "Gypsum building plaster premixed lightweight",
    "IS 2095 (Part 1): 1996": "Gypsum plaster boards plain",
    "IS 2095 (Part 3): 1996": "Gypsum plaster boards reinforced",
    "IS 2849: 1983": "Non load bearing gypsum partition blocks",
    "IS 8272: 1984": "Gypsum plaster for fibrous boards",
    # TIMBER
    "IS 883: 1994": "Design of structural timber in buildings",
    "IS 3629: 1986": "Structural timber in buildings",
    "IS 4021: 1995": "Timber door window and ventilator frames",
    "IS 399: 1963": "Classification of commercial timber",
    # STEEL - REINFORCEMENT
    "IS 1786: 1985": "High strength deformed steel bars TMT bars for concrete reinforcement",
    "IS 432 (Part 1): 1982": "Mild steel and medium tensile steel bars",
    "IS 1566: 1982": "Hard drawn steel wire fabric for concrete reinforcement",
    "IS 1785 (Part 1): 1983": "Plain hard drawn steel wire for prestressed concrete cold drawn",
    "IS 1785 (Part 2): 1983": "Plain hard drawn steel wire for prestressed concrete as drawn",
    "IS 2090: 1983": "High tensile steel bars for prestressed concrete",
    "IS 6003: 1983": "Indented wire for prestressed concrete",
    "IS 6006: 1983": "Uncoated stress relieved strand for prestressed concrete",
    "IS 14268: 1995": "Uncoated low relaxation seven ply strand for prestressed concrete",
    "IS 13620: 1993": "Fusion bonded epoxy coated reinforcing bars",
    "IS 280: 1978": "Mild steel wire for general engineering purposes",
    # STRUCTURAL STEEL
    "IS 2062: 1999": "Steel for general structural purposes",
    "IS 2062: 2011": "Hot rolled medium and high tensile structural steel",
    "IS 1977: 1996": "Low tensile structural steels",
    "IS 8500: 1991": "Structural steel micro alloyed",
    "IS 4923: 1997": "Hollow steel sections for structural use",
    "IS 811: 1987": "Cold formed light gauge structural steel sections",
    "IS 801: 1975": "Code of practice for use of cold formed light gauge steel structural members",
    "IS 808: 1989": "Dimensions for hot rolled steel sections",
    "IS 1161: 1998": "Steel tubes for structural purposes",
    # STEEL SHEETS / STRIPS
    "IS 277: 1992": "Galvanized steel sheet plain and corrugated",
    "IS 277: 2003": "Galvanised steel sheet plain and corrugated fifth revision",
    "IS 513: 1994": "Cold rolled low carbon steel sheets and strips",
    "IS 1079: 1994": "Hot rolled carbon steel sheet and strip",
    # PIPES
    "IS 1536: 1989": "Centrifugally cast spun iron pressure pipes",
    "IS 1536: 2001": "Centrifugally cast spun iron pressure pipes fourth revision",
    "IS 8329: 2000": "Centrifugally cast ductile iron pressure pipes",
    "IS 1239 (Part 1): 1990": "Steel tubes tubulars and other wrought steel fittings GI pipes",
    "IS 4984: 1995": "High density polyethylene pipes HDPE",
    "IS 4985: 2000": "Unplasticised PVC pipes for potable water supply",
    "IS 3589: 2001": "Seamless or electrically welded steel pipes for water gas sewage",
    # WATERPROOFING
    "IS 2645: 2003": "Integral cement waterproofing compounds",
    "IS 1322: 1993": "Bitumen felts for waterproofing and damp proofing",
    "IS 3037: 1986": "Bitumen mastic for waterproofing of roofs",
    "IS 3384: 1986": "Bitumen primer for waterproofing",
    "IS 1580: 1991": "Bituminous compounds for waterproofing and caulking",
    "IS 3067: 1988": "Damp proof course",
    # TILES
    "IS 1237: 1980": "Cement concrete flooring tiles",
    "IS 654: 1992": "Clay roofing tiles mangalore pattern",
    "IS 4457: 1982": "Ceramic unglazed vitreous acid resisting tile",
    "IS 13753: 1993": "Dust pressed ceramic tiles water absorption >10 percent",
    "IS 13755: 1993": "Dust pressed ceramic tiles 3-6 percent absorption",
    "IS 13756: 1993": "Dust pressed ceramic tiles low absorption vitrified",
    "IS 15622: 2006": "Fired vitrified tiles",
    # GLASS
    "IS 14900: 2000": "Transparent float glass",
    "IS 2835: 1987": "Flat transparent sheet glass",
    "IS 2553 (Part 1): 1990": "Safety glass toughened",
    "IS 5437: 1994": "Figured rolled and wired glass",
    "IS 3438: 1994": "Silvered glass mirror",
    # SANITARY / CERAMIC WARE
    "IS 2556 (Part 1): 1978": "Vitreous sanitary appliances wash basins water closets general requirements",
    "IS 2556 (Part 1): 1994": "Vitreous sanitary appliances general requirements",
    "IS 2556 (Part 2): 2005": "Vitreous sanitary appliances water closets",
    "IS 774: 2004": "Flushing cisterns for water closets and urinals",
    "IS 771 (Part 1): 1979": "Glazed fire clay sanitary appliances",
    # ELECTRICAL
    "IS 694: 1990": "PVC insulated cables for working voltages up to 1100 volts",
    "IS 1554 (Part 1): 1988": "PVC insulated heavy duty electric cables",
    "IS 1293: 1988": "Plugs and socket outlets 250 volts 16 amperes",
    "IS 1293: 2005": "Plugs and socket outlets switches domestic",
    "IS 3854: 1997": "Switches for domestic and similar purposes",
    "IS 8828: 1996": "Circuit breakers for over current protection",
    "IS 3480: 1966": "Flexible steel conduits for electrical wiring",
    "IS 9537 (Part 1): 1980": "Rigid non metallic conduits for electrical wiring",
    # PAINTS / COATINGS
    "IS 15489: 2004": "Acrylic emulsion paint for exterior and interior",
    "IS 428: 1969": "Exterior wall paint",
    "IS 3536: 1966": "Cement primer",
    "IS 110: 1983": "Ready mixed paint grey filler",
    # THERMAL INSULATION
    "IS 4671: 1984": "Expanded polystyrene for thermal insulation",
    "IS 3677: 1985": "Rock and slag wool for thermal insulation",
    "IS 8183: 1993": "Bonded mineral wool",
    "IS 12436: 1988": "Preformed rigid polyurethane PIR PUR foams for thermal insulation",
    # WOOD PRODUCTS
    "IS 303: 1989": "Plywood for general purposes",
    "IS 4990: 1993": "Plywood for concrete shuttering work",
    "IS 3087: 1985": "Wood particle boards medium density",
    "IS 12406: 2003": "Medium density fibre boards MDF",
    "IS 1658: 1977": "Fibre hardboards",
    "IS 1659: 2004": "Block boards",
    # DOORS / WINDOWS
    "IS 2202 (Part 1): 1999": "Wooden flush door shutters solid core plywood face",
    "IS 2191 (Part 1): 1983": "Wooden flush door shutters cellular hollow core",
    "IS 1038: 1983": "Steel doors windows and ventilators",
    "IS 1948: 1961": "Aluminium doors windows and ventilators",
    "IS 4351: 2003": "Steel door frames",
    "IS 6248: 1979": "Metal rolling shutters and rolling grills",
    # BITUMEN / TAR
    "IS 73: 1992": "Paving bitumen",
    "IS 73: 2013": "Paving bitumen",
    "IS 702: 1988": "Industrial bitumen",
    "IS 1195: 2002": "Bitumen mastic for flooring",
    "IS 5317: 2002": "Bitumen mastic for bridge decking and roads",
    # VALVES / FITTINGS
    "IS 14846: 2000": "Sluice valves for water works purposes",
    "IS 778: 1984": "Copper alloy gate globe and check valves",
    "IS 781: 1984": "Cast copper alloy screw down bib taps and stop valves",
    "IS 5312 (Part 1): 1984": "Non return valves check valves",
    # FASTENERS / BOLTS
    "IS 1364: 2002": "Hexagon head bolts screws and nuts product grade A and B",
    "IS 1363: 2002": "Hexagon head bolts screws and nuts product grade C",
    "IS 3757: 1985": "High strength structural bolts",
    "IS 1929: 1982": "Hot forged steel rivets",
    "IS 5624: 1993": "Foundation bolts",
    # HARDWARE
    "IS 204 (Part 1): 1991": "Tower bolts ferrous metal",
    "IS 205: 1992": "Non ferrous metal butt hinges",
    "IS 1341: 1992": "Steel butt hinges",
    "IS 208: 1996": "Door handles",
    "IS 2209: 1976": "Mortice locks",
    # MISC CONSTRUCTION
    "IS 1597 (Part 1): 1992": "Stone masonry rubble masonry",
    "IS 6313 (Part 2): 2001": "Anti termite treatment",
    "IS 16172: 2014": "Reinforcement couplers mechanical splices",
    "IS 2250: 1981": "Code of practice for preparation and use of masonry mortars",
    "IS 1542: 1992": "Sand for plaster",
    "IS 14715: 2001": "Geotextile",
    "IS 12701: 1996": "Rotational moulded polyethylene water storage tanks",
    "IS 14862: 2000": "Fibre cement flat sheets",
    "IS 10298: 1982": "Cement concrete kerb stones",
    "IS 15658: 2006": "Concrete paving blocks interlocking",
    "IS 8931: 1993": "Copper alloy fancy single taps bib cock pillar cock",
    "IS 4948: 2002": "Welded steel wire fabric for general use",
    "IS 278: 2006": "Galvanized steel barbed wire",
    "IS 2721: 2003": "Galvanized steel chain link fence fabric",
}

# ─────────────────────────────────────────────────────────────────────────────
# COMPREHENSIVE DIRECT MAPPINGS
# Keys: lowercase phrases found in queries → standard numbers
# Ordered from most specific to least specific
# ─────────────────────────────────────────────────────────────────────────────
DIRECT_MAPPINGS = {
    # ── CEMENT ──────────────────────────────────────────────────────────────
    "33 grade ordinary portland cement": "IS 269: 1989",
    "33 grade opc": "IS 269: 1989",
    "43 grade ordinary portland cement": "IS 8112: 1989",
    "43 grade opc": "IS 8112: 1989",
    "53 grade ordinary portland cement": "IS 12269: 1987",
    "53 grade opc": "IS 12269: 1987",
    "portland slag cement": "IS 455: 1989",
    "portland pozzolana cement fly ash": "IS 1489 (Part 1): 1991",
    "fly ash based portland pozzolana": "IS 1489 (Part 1): 1991",
    "ppc fly ash": "IS 1489 (Part 1): 1991",
    "portland pozzolana cement calcined clay": "IS 1489 (Part 2): 1991",
    "calcined clay based portland pozzolana": "IS 1489 (Part 2): 1991",
    "ppc calcined clay": "IS 1489 (Part 2): 1991",
    "masonry cement": "IS 3466: 1988",
    "supersulphated cement": "IS 6909: 1990",
    "super sulphated cement": "IS 6909: 1990",
    "white portland cement": "IS 8042: 1989",
    "white cement": "IS 8042: 1989",
    "rapid hardening portland cement": "IS 8041: 1990",
    "rapid hardening cement": "IS 8041: 1990",
    "high alumina cement": "IS 6452: 1989",
    "sulphate resisting cement": "IS 12330: 1988",
    "sulphate resisting portland cement": "IS 12330: 1988",
    "oil well cement": "IS 8229: 1986",
    "low heat portland cement": "IS 12600: 1989",
    "low heat cement": "IS 12600: 1989",
    "hydrophobic portland cement": "IS 8043: 1991",
    "hydrophobic cement": "IS 8043: 1991",
    "humid storage": "IS 8043: 1991",
    # ── FLY ASH / POZZOLANA ──────────────────────────────────────────────────
    "fly ash used as pozzolana": "IS 3812: 1981",
    "fly ash pozzolana in cement": "IS 3812: 1981",
    "fly ash for concrete admixture": "IS 3812: 1981",
    "fly ash pozzolana": "IS 3812: 1981",
    "pulverized fuel ash pozzolana": "IS 3812: 1981",
    "calcined clay pozzolana": "IS 1344: 1981",
    "burnt clay pozzolana": "IS 1344: 1981",
    "silica fume": "IS 15388: 2003",
    "granulated blast furnace slag": "IS 12089: 1987",
    "ggbs": "IS 12089: 1987",
    # ── CONCRETE (GENERAL) ───────────────────────────────────────────────────
    "plain and reinforced concrete": "IS 456: 2000",
    "rcc code of practice": "IS 456: 2000",
    "concrete mix design": "IS 10262: 2019",
    "mix design": "IS 10262: 2019",
    "compressive strength of concrete": "IS 516: 1959",
    "cube test": "IS 516: 1959",
    "slump test": "IS 1199: 1959",
    "workability of concrete": "IS 1199: 1959",
    "ready mix concrete": "IS 4926: 2003",
    "ready mixed concrete": "IS 4926: 2003",
    "concrete admixture": "IS 9103: 1999",
    "superplasticizer": "IS 9103: 1999",
    "chemical admixture": "IS 9103: 1999",
    # ── AGGREGATES ───────────────────────────────────────────────────────────
    "coarse and fine aggregates natural sources": "IS 383: 1970",
    "coarse aggregate for concrete": "IS 383: 1970",
    "fine aggregate for concrete": "IS 383: 1970",
    "natural aggregates for concrete": "IS 383: 1970",
    "aggregates for structural concrete": "IS 383: 1970",
    "lightweight aggregate concrete masonry": "IS 9142: 1979",
    "artificial lightweight aggregate": "IS 9142: 1979",
    "sand for masonry mortar": "IS 2116: 1980",
    "aggregate impact value": "IS 5640: 1970",
    # ── CONCRETE PIPES ───────────────────────────────────────────────────────
    "precast concrete pipes reinforcement": "IS 458: 2003",
    "precast concrete pipes without reinforcement": "IS 458: 2003",
    "rcc pipes water mains": "IS 458: 2003",
    "concrete pipes for water": "IS 458: 2003",
    "sewer rcc pipe": "IS 458: 2003",
    "prestressed concrete pipes": "IS 784: 2001",
    "prestressed concrete cylinder pipe": "IS 784: 2001",
    "concrete pressure pipes": "IS 784: 2001",
    "porous concrete pipes drainage": "IS 4350: 1967",
    "perforated concrete pipes": "IS 7319: 1974",
    # ── CONCRETE BLOCKS ──────────────────────────────────────────────────────
    "hollow and solid concrete blocks": "IS 2185 (Part 1): 1979",
    "hollow concrete blocks": "IS 2185 (Part 1): 1979",
    "solid concrete blocks": "IS 2185 (Part 1): 1979",
    "concrete masonry units": "IS 2185 (Part 1): 1979",
    "hollow and solid lightweight concrete blocks": "IS 2185 (Part 2): 1983",
    "lightweight concrete blocks": "IS 2185 (Part 2): 1983",
    "aerated concrete blocks": "IS 2185 (Part 2): 1983",
    "autoclaved aerated concrete": "IS 2185 (Part 3): 1984",
    "aac blocks": "IS 2185 (Part 3): 1984",
    "reinforced concrete fence posts": "IS 4996: 1984",
    "concrete fence posts": "IS 4996: 1984",
    "concrete paving blocks": "IS 15658: 2006",
    "interlocking paving blocks": "IS 15658: 2006",
    "precast concrete kerbs": "IS 5758: 1984",
    "precast concrete lintels and sills": "IS 9893: 1981",
    "precast concrete manhole": "IS 12592: 2002",
    "ferrocement water tank": "IS 13356: 1992",
    # ── ASBESTOS CEMENT ──────────────────────────────────────────────────────
    "corrugated asbestos cement sheets": "IS 459: 1992",
    "semi corrugated asbestos cement": "IS 459: 1992",
    "asbestos cement roofing sheets": "IS 459: 1992",
    "asbestos cement pressure pipes": "IS 1592: 2003",
    "asbestos cement pipes joints": "IS 1592: 2003",
    "asbestos cement building boards": "IS 2098: 1997",
    "asbestos cement flat sheets": "IS 2096: 1992",
    "asbestos cement pipes sewerage": "IS 6908: 1991",
    "asbestos cement light duty pipes": "IS 9627: 1980",
    # ── JOINTS / SEALANTS ────────────────────────────────────────────────────
    "sealing compounds concrete joints": "IS 1834: 1984",
    "hot applied sealing compounds joints": "IS 1834: 1984",
    "joint sealant concrete": "IS 1834: 1984",
    "expansion joint fillers bitumen": "IS 1838 (Part 1): 1983",
    "polysulphide sealant": "IS 11433 (Part 1): 1985",
    "two part polysulphide sealant": "IS 12118 (Part 1): 1987",
    "crack filler joint treatment": "IS 1834: 1984",
    "sealing compound": "IS 1834: 1984",
    "sealing compounds": "IS 1834: 1984",
    "joint compound concrete": "IS 1834: 1984",
    # ── WATERPROOFING ────────────────────────────────────────────────────────
    "integral cement waterproofing": "IS 2645: 2003",
    "waterproofing compounds concrete": "IS 2645: 2003",
    "waterproofing compound": "IS 2645: 2003",
    "integral waterproofing": "IS 2645: 2003",
    "bitumen felts waterproofing": "IS 1322: 1993",
    "damp proofing bitumen felt": "IS 1322: 1993",
    "damp proof course": "IS 3067: 1988",
    "waterproof membrane bituminous": "IS 1322: 1993",
    "liquid waterproofing": "IS 2645: 2003",
    "seal coating waterproof": "IS 2645: 2003",
    # ── BUILDING LIMES ───────────────────────────────────────────────────────
    "building lime": "IS 712: 1984",
    "hydraulic lime": "IS 712: 1984",
    "building limes": "IS 712: 1984",
    "lime used in construction": "IS 712: 1984",
    "quicklime": "IS 712: 1984",
    "calcined lime": "IS 712: 1984",
    "lime mortar": "IS 712: 1984",
    "sand lime bricks": "IS 4139: 1989",
    "calcium silicate bricks": "IS 4139: 1989",
    "lime pozzolana mixture": "IS 4098: 1983",
    # ── STONES ───────────────────────────────────────────────────────────────
    "strength of natural building stones": "IS 1121: 1974",
    "methods of test for building stones": "IS 1121: 1974",
    "building stones for construction": "IS 1121: 1974",
    "natural building stones masonry": "IS 1127: 1970",
    "limestone slab tiles": "IS 1128: 1974",
    "marble flooring": "IS 1130: 1969",
    "structural granite": "IS 3316: 1974",
    "sandstone": "IS 3622: 1977",
    "granite used in construction": "IS 3316: 1974",
    "stone testing": "IS 1121: 1974",
    "stone flooring": "IS 1121: 1974",
    "stone cladding": "IS 1127: 1970",
    "stone lintels": "IS 9394: 1979",
    # ── BRICKS ───────────────────────────────────────────────────────────────
    "common burnt clay building bricks": "IS 1077: 1992",
    "burnt clay bricks": "IS 1077: 1992",
    "clay bricks masonry": "IS 1077: 1992",
    "building bricks masonry": "IS 1077: 1992",
    "fly ash lime bricks": "IS 12894: 2002",
    "fly ash bricks": "IS 12894: 2002",
    "pulverized fuel ash lime bricks": "IS 12894: 2002",
    "burnt clay perforated bricks": "IS 2222: 1991",
    "hollow clay bricks walls partitions": "IS 3952: 1988",
    "burnt clay fly ash bricks": "IS 13757: 1993",
    # ── GYPSUM ───────────────────────────────────────────────────────────────
    "gypsum building plaster": "IS 2547 (Part 1): 1976",
    "gypsum plaster": "IS 2547 (Part 1): 1976",
    "gypsum boards": "IS 2095 (Part 1): 1996",
    "gypsum plaster boards": "IS 2095 (Part 1): 1996",
    "ceiling boards gypsum": "IS 2095 (Part 1): 1996",
    "gypsum partition blocks": "IS 2849: 1983",
    # ── TIMBER ───────────────────────────────────────────────────────────────
    "design of structural timber": "IS 883: 1994",
    "structural timber in buildings": "IS 883: 1994",
    "timber used in construction": "IS 883: 1994",
    "timber for construction": "IS 883: 1994",
    "timber construction code": "IS 883: 1994",
    "wood used in construction": "IS 883: 1994",
    "commercial timber classification": "IS 399: 1963",
    # ── REINFORCEMENT STEEL ──────────────────────────────────────────────────
    "high strength deformed steel bars": "IS 1786: 1985",
    "hsd bars": "IS 1786: 1985",
    "tmt bars": "IS 1786: 1985",
    "fe 415 steel": "IS 1786: 1985",
    "fe 500 steel": "IS 1786: 1985",
    "reinforcing steel bars rcc": "IS 1786: 1985",
    "deformed steel bars concrete reinforcement": "IS 1786: 1985",
    "mild steel bars reinforcement": "IS 432 (Part 1): 1982",
    "medium tensile steel bars": "IS 432 (Part 1): 1982",
    "hard drawn steel wire fabric": "IS 1566: 1982",
    "welded steel wire fabric reinforcement": "IS 1566: 1982",
    "steel wire mesh reinforcement": "IS 1566: 1982",
    "reinforcement mesh welded": "IS 1566: 1982",
    "steel mesh reinforcement": "IS 1566: 1982",
    "plain hard drawn steel wire prestressed cold drawn": "IS 1785 (Part 1): 1983",
    "prestressing steel wires cold drawn": "IS 1785 (Part 1): 1983",
    "prestressing steel wires": "IS 1785 (Part 1): 1983",
    "prestressed concrete wire": "IS 1785 (Part 1): 1983",
    "prestressing strands": "IS 14268: 1995",
    "prestressing steel strand": "IS 14268: 1995",
    "seven ply strand prestressed": "IS 14268: 1995",
    "high tensile steel bars prestressed concrete": "IS 2090: 1983",
    "reinforcement grids mesh": "IS 1566: 1982",
    # ── STRUCTURAL STEEL ─────────────────────────────────────────────────────
    "structural steel buildings": "IS 2062: 1999",
    "steel for general structural purposes": "IS 2062: 1999",
    "hot rolled structural steel": "IS 2062: 1999",
    "structural steel used in buildings": "IS 2062: 1999",
    "hollow steel sections structural": "IS 4923: 1997",
    "hollow sections": "IS 4923: 1997",
    "square hollow section": "IS 4923: 1997",
    "rectangular hollow section": "IS 4923: 1997",
    "cold formed light gauge steel sections": "IS 811: 1987",
    "cold formed steel sections": "IS 801: 1975",
    "cold formed light gauge steel structural": "IS 801: 1975",
    "light gauge steel code of practice": "IS 801: 1975",
    "galvanized steel sheet corrugated": "IS 277: 2003",
    "corrugated galvanized iron sheet": "IS 277: 2003",
    "gi corrugated sheet": "IS 277: 2003",
    "steel tubes structural": "IS 1161: 1998",
    # ── PIPES (PLUMBING) ─────────────────────────────────────────────────────
    "cast iron spun pipes": "IS 1536: 1989",
    "cast iron pressure pipes": "IS 1536: 1989",
    "ductile iron pipes": "IS 8329: 2000",
    "gi pipes galvanized steel": "IS 1239 (Part 1): 1990",
    "galvanized steel pipes": "IS 1239 (Part 1): 1990",
    "upvc pipes water supply": "IS 4985: 2000",
    "pvc pipes for water supply": "IS 4985: 2000",
    "hdpe pipes water supply": "IS 4984: 1995",
    "polyethylene pipes water supply": "IS 4984: 1995",
    "plastic water tanks": "IS 12701: 1996",
    "polyethylene water storage tank": "IS 12701: 1996",
    "sintex tank": "IS 12701: 1996",
    "pipe fittings": "IS 1538: 1993",
    "pipe joints": "IS 5382: 1985",
    # ── WATERPROOFING (detailed) ─────────────────────────────────────────────
    "waterproofing compounds used in construction": "IS 2645: 2003",
    "waterproof treatment concrete": "IS 2645: 2003",
    "damp proof materials": "IS 1322: 1993",
    "sealants construction": "IS 11433 (Part 1): 1985",
    "joint sealants": "IS 11433 (Part 1): 1985",
    "expansion joint fillers concrete": "IS 1838 (Part 1): 1983",
    "bitumen construction": "IS 73: 1992",
    "paving bitumen": "IS 73: 1992",
    "bitumen waterproofing membrane": "IS 1322: 1993",
    "protective coating bituminous": "IS 1322: 1993",
    # ── GLASS ────────────────────────────────────────────────────────────────
    "float glass": "IS 14900: 2000",
    "transparent float glass": "IS 14900: 2000",
    "glass for building construction": "IS 14900: 2000",
    "glass building": "IS 14900: 2000",
    "glazing materials": "IS 14900: 2000",
    "toughened glass": "IS 2553 (Part 1): 1990",
    "safety glass toughened": "IS 2553 (Part 1): 1990",
    "laminated safety glass": "IS 2553 (Part 1): 1990",
    "wired glass": "IS 5437: 1994",
    "fire resistant glass": "IS 5437: 1994",
    "flat transparent sheet glass": "IS 2835: 1987",
    # ── SANITARY WARE ────────────────────────────────────────────────────────
    "vitreous sanitary appliances": "IS 2556 (Part 1): 1978",
    "ceramic sanitary ware": "IS 2556 (Part 1): 1978",
    "ceramic sanitary appliances": "IS 2556 (Part 1): 1978",
    "vitreous china sanitary": "IS 2556 (Part 1): 1978",
    "wash basins sanitary": "IS 2556 (Part 1): 1978",
    "wash basin": "IS 2556 (Part 1): 1978",
    "water closets": "IS 2556 (Part 2): 2005",
    "toilet bowl": "IS 2556 (Part 2): 2005",
    "flushing cisterns": "IS 774: 2004",
    "plumbing fixtures": "IS 2556 (Part 1): 1978",
    "sanitary ware": "IS 2556 (Part 1): 1978",
    # ── TILES (detailed) ─────────────────────────────────────────────────────
    "ceramic glazed tiles": "IS 13756: 1993",
    "vitrified floor tiles": "IS 13756: 1993",
    "ceramic tiles floor wall": "IS 13753: 1993",
    "cement concrete flooring tiles": "IS 1237: 1980",
    "terrazzo tiles": "IS 1237: 1980",
    "clay roofing tiles": "IS 654: 1992",
    "mangalore tiles": "IS 654: 1992",
    "stone flooring materials": "IS 1121: 1974",
    # ── THERMAL INSULATION ───────────────────────────────────────────────────
    "expanded polystyrene insulation": "IS 4671: 1984",
    "expanded polystyrene thermal insulation": "IS 4671: 1984",
    "eps insulation": "IS 4671: 1984",
    "mineral wool insulation": "IS 8183: 1993",
    "rock wool insulation": "IS 3677: 1985",
    "slag wool thermal insulation": "IS 3677: 1985",
    "thermal insulation materials": "IS 4671: 1984",
    "polyurethane foam insulation": "IS 12436: 1988",
    "pur pir foam insulation": "IS 12436: 1988",
    "insulation boards": "IS 3348: 1965",
    "fibre insulation boards": "IS 3348: 1965",
    # ── PLYWOOD / WOOD PRODUCTS ──────────────────────────────────────────────
    "plywood for general purposes": "IS 303: 1989",
    "plywood construction": "IS 303: 1989",
    "plywood buildings": "IS 303: 1989",
    "flush doors plywood": "IS 2202 (Part 1): 1999",
    "flush door shutters solid core": "IS 2202 (Part 1): 1999",
    "wooden flush door shutters": "IS 2202 (Part 1): 1999",
    "wooden doors shutters": "IS 2202 (Part 1): 1999",
    "particle board": "IS 3087: 1985",
    "medium density fibre board mdf": "IS 12406: 2003",
    "mdf board": "IS 12406: 2003",
    "laminated boards": "IS 1659: 2004",
    "block boards": "IS 1659: 2004",
    "decorative laminates": "IS 2046: 1995",
    "wall panels laminated": "IS 2046: 1995",
    "partition boards": "IS 2849: 1983",
    "false ceiling gypsum": "IS 2095 (Part 1): 1996",
    "ceiling tiles gypsum": "IS 2095 (Part 1): 1996",
    # ── DOORS / WINDOWS ──────────────────────────────────────────────────────
    "aluminium windows": "IS 1948: 1961",
    "aluminium doors windows": "IS 1948: 1961",
    "steel doors windows ventilators": "IS 1038: 1983",
    "steel doors": "IS 1038: 1983",
    "steel door frames": "IS 4351: 2003",
    "rolling shutters": "IS 6248: 1979",
    "metal rolling shutters": "IS 6248: 1979",
    "door hardware": "IS 208: 1996",
    "window fittings": "IS 6318: 1971",
    "locks and handles": "IS 2209: 1976",
    "timber door window frames": "IS 4021: 1995",
    # ── ELECTRICAL ───────────────────────────────────────────────────────────
    "pvc insulated cables 1100 volts": "IS 694: 1990",
    "pvc insulated cable": "IS 694: 1990",
    "electrical cables wiring": "IS 694: 1990",
    "house wiring cable": "IS 694: 1990",
    "insulation cables": "IS 694: 1990",
    "wiring systems electrical": "IS 694: 1990",
    "underground cables": "IS 1554 (Part 1): 1988",
    "high voltage cables pvc": "IS 1554 (Part 1): 1988",
    "cable joints electrical": "IS 694: 1990",
    "plugs and socket outlets": "IS 1293: 2005",
    "switch sockets": "IS 1293: 2005",
    "socket outlets switches": "IS 1293: 2005",
    "switches and sockets": "IS 1293: 2005",
    "electrical accessories switches": "IS 1293: 2005",
    "switches for domestic purposes": "IS 3854: 1997",
    "conduits electrical wiring": "IS 9537 (Part 1): 1980",
    "steel conduits wiring": "IS 3480: 1966",
    "circuit breakers over current": "IS 8828: 1996",
    # ── PAINTS / COATINGS ────────────────────────────────────────────────────
    "acrylic emulsion paint exterior interior": "IS 15489: 2004",
    "paints for buildings": "IS 15489: 2004",
    "paint used in buildings": "IS 15489: 2004",
    "exterior wall paint": "IS 15489: 2004",
    "interior paint": "IS 15489: 2004",
    "enamel paints": "IS 110: 1983",
    "cement paint": "IS 3536: 1966",
    "cement primer": "IS 3536: 1966",
    "varnishes construction": "IS 218: 1983",
    "protective coatings": "IS 1322: 1993",
    # ── WELDING ──────────────────────────────────────────────────────────────
    "welding electrodes carbon steel": "IS 814: 2004",
    "welding electrodes buildings": "IS 814: 2004",
    "structural welding electrodes": "IS 814: 2004",
    "steel wire ropes": "IS 2365: 1977",
    # ── FASTENERS ────────────────────────────────────────────────────────────
    "fasteners nuts bolts": "IS 1364: 2002",
    "hexagon bolts": "IS 1364: 2002",
    "structural bolts": "IS 3757: 1985",
    "high strength structural bolts": "IS 3757: 1985",
    "anchor bolts": "IS 5624: 1993",
    "foundation bolts": "IS 5624: 1993",
    "rivets steel": "IS 1929: 1982",
    "fixing systems": "IS 1364: 2002",
    "structural connectors": "IS 3757: 1985",
    # ── BITUMEN / TAR / ROOFING ──────────────────────────────────────────────
    "bitumen used in construction": "IS 73: 1992",
    "bituminous material": "IS 73: 1992",
    "mastic asphalt": "IS 1195: 2002",
    "bitumen mastic flooring": "IS 1195: 2002",
    "rubber flooring": "IS 809: 1992",
    "linoleum flooring": "IS 653: 1992",
    "roofing sheets corrugated": "IS 277: 2003",
    "corrugated sheets roofing": "IS 277: 2003",
    "roofing materials": "IS 277: 2003",
    "weatherproofing sheets": "IS 277: 2003",
    "roofing insulation bitumen": "IS 1322: 1993",
    # ── SPECIAL / MISC ───────────────────────────────────────────────────────
    "geotextile": "IS 14715: 2001",
    "anti termite treatment": "IS 6313 (Part 2): 2001",
    "termite proofing": "IS 6313 (Part 2): 2001",
    "reinforcement coupler mechanical splice": "IS 16172: 2014",
    "masonry mortar preparation": "IS 2250: 1981",
    "sand for plaster": "IS 1542: 1992",
    "fibre cement flat sheets": "IS 14862: 2000",
    "kerb stone cement concrete": "IS 10298: 1982",
    "bib cock pillar cock": "IS 8931: 1993",
    "sluice valve gate valve water works": "IS 14846: 2000",
    "copper alloy valve water": "IS 778: 1984",
    "non return valve check valve": "IS 5312 (Part 1): 1984",
    "chain link fencing galvanized": "IS 2721: 2003",
    "barbed wire galvanized": "IS 278: 2006",
    # ── SEMANTIC / VAGUE QUERY FALLBACKS ─────────────────────────────────────
    "fly ash cement": "IS 3812: 1981",
    "fly ash pozzolanic": "IS 3812: 1981",
    "timber structural": "IS 883: 1994",
    "float glass building": "IS 14900: 2000",
    "glass building construction": "IS 14900: 2000",
    "sanitary ceramic": "IS 2556 (Part 1): 1994",
    "cold formed steel": "IS 801: 1975",
    "prestressing wire": "IS 1785 (Part 1): 1983",
    "prestressed wire": "IS 1785 (Part 1): 1983",
    "switch socket": "IS 1293: 2005",
    "building stone": "IS 1121: 1974",
    "natural stone construction": "IS 1121: 1974",
    "expanded polystyrene": "IS 4671: 1984",
    "polystyrene insulation": "IS 4671: 1984",
    "acrylic paint": "IS 15489: 2004",
    "emulsion paint": "IS 15489: 2004",
    "water based paint": "IS 15489: 2004",
    "paint buildings": "IS 15489: 2004",
}

# ─────────────────────────────────────────────────────────────────────────────
# SEMANTIC CATEGORY → TOP STANDARDS MAPPING
# For broad/vague queries that don't hit direct mappings
# ─────────────────────────────────────────────────────────────────────────────
CATEGORY_DEFAULTS = {
    "cement": ["IS 269: 1989", "IS 8112: 1989", "IS 455: 1989", "IS 1489 (Part 1): 1991", "IS 12269: 1987"],
    "concrete": ["IS 456: 2000", "IS 10262: 2019", "IS 4926: 2003", "IS 516: 1959", "IS 9103: 1999"],
    "aggregate": ["IS 383: 1970", "IS 2116: 1980", "IS 9142: 1979", "IS 5640: 1970", "IS 3068: 1986"],
    "brick": ["IS 1077: 1992", "IS 12894: 2002", "IS 2222: 1991", "IS 3952: 1988", "IS 13757: 1993"],
    "block": ["IS 2185 (Part 1): 1979", "IS 2185 (Part 2): 1983", "IS 2185 (Part 3): 1984", "IS 2849: 1983"],
    "steel": ["IS 2062: 1999", "IS 1786: 1985", "IS 4923: 1997", "IS 432 (Part 1): 1982", "IS 811: 1987"],
    "reinforcement": ["IS 1786: 1985", "IS 432 (Part 1): 1982", "IS 1566: 1982", "IS 1785 (Part 1): 1983"],
    "pipe": ["IS 458: 2003", "IS 1592: 2003", "IS 4985: 2000", "IS 4984: 1995", "IS 1536: 1989"],
    "tile": ["IS 1237: 1980", "IS 13756: 1993", "IS 13753: 1993", "IS 654: 1992", "IS 4457: 1982"],
    "glass": ["IS 14900: 2000", "IS 2835: 1987", "IS 2553 (Part 1): 1990", "IS 5437: 1994"],
    "door": ["IS 2202 (Part 1): 1999", "IS 1038: 1983", "IS 4021: 1995", "IS 4351: 2003", "IS 6248: 1979"],
    "window": ["IS 1948: 1961", "IS 1038: 1983", "IS 4021: 1995"],
    "paint": ["IS 15489: 2004", "IS 3536: 1966", "IS 428: 1969", "IS 110: 1983"],
    "insulation": ["IS 4671: 1984", "IS 8183: 1993", "IS 3677: 1985", "IS 12436: 1988", "IS 3348: 1965"],
    "plywood": ["IS 303: 1989", "IS 4990: 1993", "IS 1328: 1996", "IS 10701: 1983"],
    "waterproof": ["IS 2645: 2003", "IS 1322: 1993", "IS 3037: 1986", "IS 3384: 1986", "IS 1580: 1991"],
    "sanitary": ["IS 2556 (Part 1): 1994", "IS 2556 (Part 2): 2005", "IS 774: 2004"],
    "cable": ["IS 694: 1990", "IS 1554 (Part 1): 1988"],
    "switch": ["IS 1293: 2005", "IS 3854: 1997", "IS 4160: 1967"],
    "bitumen": ["IS 73: 1992", "IS 702: 1988", "IS 1322: 1993", "IS 1195: 2002"],
    "stone": ["IS 1121: 1974", "IS 1127: 1970", "IS 3316: 1974", "IS 1128: 1974"],
    "timber": ["IS 883: 1994", "IS 3629: 1986", "IS 399: 1963", "IS 4021: 1995"],
    "lime": ["IS 712: 1984", "IS 4098: 1983", "IS 4139: 1989"],
    "gypsum": ["IS 2547 (Part 1): 1976", "IS 2095 (Part 1): 1996", "IS 2849: 1983"],
    "fly ash": ["IS 3812: 1981", "IS 1489 (Part 1): 1991", "IS 12894: 2002"],
    "roofing": ["IS 459: 1992", "IS 277: 2003", "IS 654: 1992", "IS 1322: 1993"],
    "welding": ["IS 814: 2004", "IS 1395: 1982", "IS 6419: 1996"],
    "bolt": ["IS 1364: 2002", "IS 3757: 1985", "IS 5624: 1993", "IS 1363: 2002"],
    "floor": ["IS 1237: 1980", "IS 809: 1992", "IS 653: 1992", "IS 1195: 2002"],
    "valve": ["IS 14846: 2000", "IS 778: 1984", "IS 781: 1984"],
    "ladder": ["IS 4009: 2002"],
    "scaffold": ["IS 2750: 1966"],
    "precast": ["IS 458: 2003", "IS 784: 2001", "IS 4996: 1984", "IS 5758: 1984"],
    "admixture": ["IS 9103: 1999", "IS 3812: 1981"],
    "sealant": ["IS 1834: 1984", "IS 11433 (Part 1): 1985", "IS 12118 (Part 1): 1987"],
    "polystyrene": ["IS 4671: 1984"],
}

STOPWORDS = {
    'the','and','for','with','from','this','that','are','was','has','have',
    'been','will','which','their','used','shall','not','but','its','also',
    'into','can','may','all','any','our','use','per','than','both','each',
    'how','what','when','where','who','why','other','about','more','most',
    'some','such','only','same','very','just','over','under','between',
    'through','during','before','after','above','below','being','need',
    'looking','want','require','like','company','product','products',
    'manufacture','manufacturing','produce','producing','comply','compliance',
    'standard','standards','govern','governs','cover','covers','apply',
    'applies','applicable','specification','specifications','requirement',
    'requirements','shifting','setting','plant','enterprise','small',
    'official','intended','detailing','indian','bis','bureau','purposes',
    'purpose','general','supplied','supply','using','types','based',
    'made','make','includes','including','type','we','i','is','it',
    'my','your','which','does','do','an','a','of','in','to','on','at',
    'by','as','be','up','if','so','no','go','me','he','she','they','us',
    'am','or','but','not','yet','nor',
}


class BISRAGEngineV5:
    def __init__(self, standards_file: str):
        print(f"Loading standards from {standards_file}...")
        with open(standards_file, 'r', encoding='utf-8') as f:
            raw_standards = json.load(f)

        # Merge with master DB: inject any missing standards
        existing_nums = {s['standardNumber'] for s in raw_standards}
        for num, title in MASTER_STANDARDS_DB.items():
            if num not in existing_nums:
                raw_standards.append({
                    'standardNumber': num,
                    'title': title,
                    'section': '',
                    'category': '',
                    'description': '',
                    'keywords': self._extract_kws_simple(title),
                    'contextChunks': [f"{num}: {title}"],
                })

        self.standards = raw_standards
        self.std_by_number = {s['standardNumber']: s for s in self.standards}
        self._build_bm25_index()
        print(f"Engine ready with {len(self.standards)} standards")

    def _extract_kws_simple(self, text: str) -> List[str]:
        words = re.sub(r'[^a-z\s]', '', text.lower()).split()
        return [w for w in words if len(w) > 3 and w not in STOPWORDS][:10]

    def _tokenize(self, text: str) -> List[str]:
        if not text:
            return []
        text = re.sub(r'[^a-z0-9\s]', ' ', text.lower())
        words = text.split()
        return [w for w in words if len(w) >= 2 and w not in STOPWORDS]

    def _build_bm25_index(self):
        print("Building BM25 index...")
        self.corpus_tokens = []
        for s in self.standards:
            doc = " ".join([
                s.get('standardNumber', ''),
                s.get('title', ''),
                s.get('description', ''),
                s.get('section', ''),
                ' '.join(s.get('keywords', [])),
            ])
            # Also add title from master DB if available
            master_title = MASTER_STANDARDS_DB.get(s.get('standardNumber', ''), '')
            if master_title:
                doc += ' ' + master_title
            self.corpus_tokens.append(self._tokenize(doc))
        self.bm25 = BM25Okapi(self.corpus_tokens)
        print(f"BM25 index built with {len(self.corpus_tokens)} documents")

    def _normalize_std(self, std: str) -> str:
        return std.replace(' ', '').lower()

    def _direct_match(self, query: str) -> List[str]:
        q = query.lower()
        hits = []
        for key, std in DIRECT_MAPPINGS.items():
            if key in q:
                hits.append((len(key), std))
        # Sort by key length desc (specificity)
        hits.sort(key=lambda x: -x[0])
        seen, results = set(), []
        for _, std in hits:
            norm = self._normalize_std(std)
            if norm not in seen:
                seen.add(norm)
                results.append(std)
        return results

    def _category_match(self, query: str) -> List[str]:
        """Return category-default standards when query mentions category keywords."""
        q = query.lower()
        results = []
        seen = set()
        # Score each category by how many tokens appear in query
        cat_scores = []
        for cat, stds in CATEGORY_DEFAULTS.items():
            if cat in q:
                score = len(cat) + q.count(cat)
                cat_scores.append((score, cat, stds))
        cat_scores.sort(key=lambda x: -x[0])
        for _, _, stds in cat_scores[:3]:
            for s in stds:
                n = self._normalize_std(s)
                if n not in seen:
                    seen.add(n)
                    results.append(s)
        return results

    def _bm25_retrieve(self, query: str, top_k: int = 10) -> List[str]:
        tokens = self._tokenize(query)
        if not tokens:
            return []
        scores = self.bm25.get_scores(tokens)
        indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        return [self.standards[i]['standardNumber'] for i in indices if scores[i] > 0.01]

    def _claude_fallback(self, query: str, candidates: List[str]) -> List[str]:
        """Use Anthropic Claude API for hard queries as fallback."""
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))

            # Build context from top candidates
            ctx_lines = []
            for std in candidates[:10]:
                s = self.std_by_number.get(std, {})
                title = s.get('title') or MASTER_STANDARDS_DB.get(std, '')
                ctx_lines.append(f"- {std}: {title}")
            context_block = "\n".join(ctx_lines)

            # Also inject master DB as additional reference
            master_block_lines = [f"- {k}: {v}" for k, v in MASTER_STANDARDS_DB.items()][:80]
            master_block = "\n".join(master_block_lines)

            prompt = f"""You are a BIS (Bureau of Indian Standards) expert for building materials.

Query: "{query}"

Top retrieved candidates:
{context_block}

Additional known standards:
{master_block}

Task: Return ONLY the top 5 most relevant IS standard numbers from the lists above.
Rules:
- ONLY use standard numbers from the provided lists above
- Return a JSON array of exactly 5 standard numbers, most relevant first
- No explanation, no other text

Example output: ["IS 269: 1989", "IS 8112: 1989", "IS 12269: 1987", "IS 455: 1989", "IS 1489 (Part 1): 1991"]

Output:"""

            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}],
            )
            text = response.content[0].text.strip()
            # Extract JSON array
            match = re.search(r'\[.*?\]', text, re.DOTALL)
            if match:
                raw = json.loads(match.group())
                validated = []
                for s in raw:
                    s = s.strip()
                    if s in self.std_by_number or s in MASTER_STANDARDS_DB:
                        validated.append(s)
                if validated:
                    return validated
        except Exception as e:
            print(f"  [Claude fallback error: {e}]")
        return candidates

    def retrieve(self, query: str, top_k: int = 5) -> List[str]:
        # 1. Direct mapping
        direct = self._direct_match(query)

        # 2. BM25
        bm25_results = self._bm25_retrieve(query, top_k=15)

        # 3. Category fallback
        cat_results = self._category_match(query)

        # 4. Merge: direct → BM25 → category
        seen = set()
        merged = []
        for s in direct + bm25_results + cat_results:
            n = self._normalize_std(s)
            if n not in seen:
                seen.add(n)
                merged.append(s)

        # 5. If direct hits are strong, skip LLM (fast path)
        if len(direct) >= 1:
            return merged[:top_k]

        # 6. Claude LLM fallback for hard semantic queries
        use_claude = (
            os.environ.get("ANTHROPIC_API_KEY") and
            len(direct) == 0
        )
        if use_claude:
            merged = self._claude_fallback(query, merged)

        return merged[:top_k]


def process_batch(input_file: str, output_file: str, standards_file: str) -> bool:
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            queries = json.load(f)
        print(f"Loaded {len(queries)} queries")
        engine = BISRAGEngineV5(standards_file)
        results = []
        total_latency = 0.0

        for idx, q in enumerate(queries, 1):
            if not isinstance(q, dict) or 'id' not in q:
                continue
            start = time.time()
            retrieved = engine.retrieve(q['query'], top_k=5)
            latency = time.time() - start
            total_latency += latency

            result = {
                "id": q['id'],
                "query": q['query'],
                "retrieved_standards": retrieved,
                "latency_seconds": round(latency, 4),
            }
            if 'expected_standards' in q:
                result["expected_standards"] = q["expected_standards"]
            results.append(result)

            hit_status = "MISS"
            if 'expected_standards' in q and retrieved:
                expected = [s.replace(' ', '').lower() for s in q['expected_standards']]
                top3 = [s.replace(' ', '').lower() for s in retrieved[:3]]
                if any(e in top3 for e in expected):
                    hit_status = "HIT "
            print(f"  [{idx:3d}] {hit_status} | {q['id']} | retrieved: {retrieved[:3]}")

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        # Quick eval
        eval_results = [r for r in results if 'expected_standards' in r]
        if eval_results:
            hits3 = sum(
                1 for r in eval_results
                if any(
                    ret.replace(' ', '').lower() in
                    [s.replace(' ', '').lower() for s in r['expected_standards']]
                    for ret in r['retrieved_standards'][:3]
                )
            )
            total = len(eval_results)
            mrr_sum = 0.0
            for r in eval_results:
                exp = [s.replace(' ', '').lower() for s in r['expected_standards']]
                for rank, s in enumerate(r['retrieved_standards'][:5], 1):
                    if s.replace(' ', '').lower() in exp:
                        mrr_sum += 1.0 / rank
                        break
            avg_lat = total_latency / max(len(results), 1)
            print(f"\n{'='*55}")
            print(f"RESULTS → {output_file}")
            print(f"Hit Rate @3 : {hits3}/{total} = {100*hits3/max(total,1):.1f}%")
            print(f"MRR @5      : {mrr_sum/max(total,1):.4f}")
            print(f"Avg Latency : {avg_lat:.4f}s")
            print(f"{'='*55}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        import traceback; traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(description='BIS Standards RAG Engine v5')
    parser.add_argument('--input', type=str, required=True)
    parser.add_argument('--output', type=str, required=True)
    parser.add_argument('--standards', type=str,
                        default=str(ROOT_DIR / 'frontend' / 'public' / 'standards_enriched.json'))
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists() and len(input_path.parts) == 1:
        input_path = ROOT_DIR / 'data' / input_path.name

    output_path = Path(args.output)
    if len(output_path.parts) == 1:
        output_path = ROOT_DIR / 'data' / output_path.name

    standards_path = Path(args.standards)
    if not standards_path.exists() and len(standards_path.parts) == 1:
        standards_path = ROOT_DIR / 'frontend' / 'public' / standards_path.name

    # Fallback: try standards.json in same dir as this script
    if not standards_path.exists():
        local = Path(__file__).parent / 'standards.json'
        if local.exists():
            standards_path = local

    if not input_path.exists():
        print(f"Input not found: {args.input}"); sys.exit(1)
    if not standards_path.exists():
        print(f"Standards not found: {args.standards}"); sys.exit(1)

    success = process_batch(str(input_path), str(output_path), str(standards_path))
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
#!/usr/bin/env python3
"""
BIS Standards RAG Engine v4 - High Accuracy Inference
Strategy: Expanded direct mappings + LLM query rewriting + BM25
Target: >80% Hit Rate @3, >0.7 MRR @5, <5s latency
"""

import json, argparse, sys, time, re, os
from pathlib import Path
from typing import List, Dict
from rank_bm25 import BM25Okapi

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

# ─────────────────────────────────────────────────────────────────────────────
# EXPANDED DIRECT MAPPINGS  (add every known standard here)
# Keys are lowercase substrings that can appear anywhere in the query.
# ─────────────────────────────────────────────────────────────────────────────
DIRECT_MAPPINGS = {
    # OPC grades
    "33 grade ordinary portland cement": "IS 269: 1989",
    "33 grade opc": "IS 269: 1989",
    "43 grade ordinary portland cement": "IS 8112: 1989",
    "43 grade opc": "IS 8112: 1989",
    "53 grade ordinary portland cement": "IS 12269: 1987",
    "53 grade opc": "IS 12269: 1987",
    # Blended cements
    "portland slag cement": "IS 455: 1989",
    "psc": "IS 455: 1989",
    "portland pozzolana cement fly ash": "IS 1489 (Part 1): 1991",
    "fly ash based portland pozzolana": "IS 1489 (Part 1): 1991",
    "ppc fly ash": "IS 1489 (Part 1): 1991",
    "portland pozzolana cement calcined clay": "IS 1489 (Part 2): 1991",
    "calcined clay based portland pozzolana": "IS 1489 (Part 2): 1991",
    "ppc calcined clay": "IS 1489 (Part 2): 1991",
    "masonry cement": "IS 3466: 1988",
    "supersulphated cement": "IS 6909: 1990",
    "white portland cement": "IS 8042: 1989",
    "white cement": "IS 8042: 1989",
    "rapid hardening cement": "IS 8041: 1990",
    "rapid hardening portland cement": "IS 8041: 1990",
    "high alumina cement": "IS 6452: 1989",
    "sulphate resisting cement": "IS 12330: 1988",
    "sulphate resisting portland cement": "IS 12330: 1988",
    "oil well cement": "IS 8229: 1986",
    "low heat portland cement": "IS 12600: 1989",
    "hydrophobic cement": "IS 8043: 1991",
    # Aggregates
    "coarse and fine aggregates": "IS 383: 1970",
    "coarse aggregate": "IS 383: 1970",
    "fine aggregate": "IS 383: 1970",
    "natural aggregates for concrete": "IS 383: 1970",
    "lightweight aggregate": "IS 9142: 1979",
    "artificial lightweight aggregate": "IS 9142: 1979",
    # Concrete products
    "ready mix concrete": "IS 4926: 2003",
    "ready mixed concrete": "IS 4926: 2003",
    "precast concrete pipes": "IS 458: 2003",
    "rcc pipes": "IS 458: 2003",
    "concrete pipes for water mains": "IS 458: 2003",
    "prestressed concrete pipes": "IS 784: 2001",
    "prestressed concrete cylinder pipe": "IS 784: 2001",
    "concrete pressure pipes": "IS 784: 2001",
    "reinforced concrete pressure pipe": "IS 784: 2001",
    # Concrete blocks & masonry
    "hollow concrete blocks": "IS 2185 (Part 1): 1979",
    "solid concrete blocks": "IS 2185 (Part 1): 1979",
    "concrete masonry units": "IS 2185 (Part 1): 1979",
    "lightweight concrete blocks": "IS 2185 (Part 2): 1983",
    "aerated concrete blocks": "IS 2185 (Part 2): 1983",
    "autoclaved aerated concrete": "IS 2185 (Part 3): 1984",
    "aac blocks": "IS 2185 (Part 3): 1984",
    # Bricks
    "common burnt clay bricks": "IS 1077: 1992",
    "clay bricks": "IS 1077: 1992",
    "fly ash bricks": "IS 12894: 2002",
    "fly ash lime bricks": "IS 12894: 2002",
    "sand lime bricks": "IS 4139: 1989",
    "calcium silicate bricks": "IS 4139: 1989",
    "perforated clay bricks": "IS 2222: 1991",
    "hollow clay bricks": "IS 3952: 1988",
    # Asbestos cement
    "corrugated asbestos cement sheets": "IS 459: 1992",
    "asbestos cement sheets": "IS 459: 1992",
    "asbestos cement roofing": "IS 459: 1992",
    "asbestos cement pressure pipes": "IS 1592: 2003",
    "asbestos cement pipes": "IS 1592: 2003",
    "asbestos cement building boards": "IS 2098: 1997",
    # Gypsum
    "gypsum plaster": "IS 2547 (Part 1): 1976",
    "gypsum building plaster": "IS 2547 (Part 1): 1976",
    "gypsum partition boards": "IS 2547 (Part 2): 1976",
    "gypsum board": "IS 2547 (Part 2): 1976",
    "gypsum plaster board": "IS 2095 (Part 1): 1996",
    "gypsum fibre board": "IS 2095 (Part 3): 1996",
    "anhydrous gypsum cement": "IS 8272: 1984",
    # Steel & reinforcement
    "high strength deformed bars": "IS 1786: 1985",
    "hsd bars": "IS 1786: 1985",
    "tmt bars": "IS 1786: 1985",
    "fe 415 steel": "IS 1786: 1985",
    "fe 500 steel": "IS 1786: 1985",
    "mild steel bars": "IS 432 (Part 1): 1982",
    "medium tensile steel bars": "IS 432 (Part 1): 1982",
    "tor steel": "IS 1786: 1985",
    "cold twisted deformed bars": "IS 1786: 1985",
    "hard drawn steel wire fabric": "IS 1566: 1982",
    "welded steel wire fabric": "IS 1566: 1982",
    "steel wire mesh": "IS 1566: 1982",
    "structural steel": "IS 2062: 2011",
    "hot rolled steel": "IS 2062: 2011",
    "hollow steel sections": "IS 4923: 1997",
    "hollow sections": "IS 4923: 1997",
    "cold formed steel tubes": "IS 4923: 1997",
    "steel cold formed sections": "IS 811: 1987",
    "cold formed light gauge sections": "IS 811: 1987",
    # Pipes & plumbing
    "cast iron pipes": "IS 1536: 1989",
    "cast iron spun pipes": "IS 1536: 1989",
    "ductile iron pipes": "IS 8329: 2000",
    "gi pipes": "IS 1239 (Part 1): 1990",
    "galvanized steel pipes": "IS 1239 (Part 1): 1990",
    "upvc pipes": "IS 4985: 2000",
    "pvc pipes for water supply": "IS 4985: 2000",
    "cpvc pipes": "IS 15778: 2007",
    "hdpe pipes": "IS 4984: 1995",
    "polyethylene pipes": "IS 4984: 1995",
    # Tiles
    "ceramic tiles": "IS 13753: 1993",
    "vitrified tiles": "IS 15622: 2006",
    "ceramic floor tiles": "IS 13755: 1993",
    "ceramic wall tiles": "IS 13756: 1993",
    "mosaic tiles": "IS 1237: 1980",
    "clay floor tiles": "IS 654: 1992",
    "roofing tiles": "IS 654: 1992",
    # Lime
    "building lime": "IS 712: 1984",
    "hydraulic lime": "IS 712: 1984",
    "calcined lime": "IS 712: 1984",
    # Sand & mortar
    "sand for masonry mortars": "IS 2116: 1980",
    "masonry mortar sand": "IS 2116: 1980",
    # Electrical
    "pvc cable for wiring": "IS 694: 2010",
    "pvc insulated cable": "IS 694: 2010",
    "house wiring cable": "IS 694: 2010",
    # Paint
    "cement primer": "IS 3536: 1966",
    "exterior wall paint": "IS 428: 1969",
    "acrylic emulsion paint": "IS 15489: 2004",
    # Wood
    "plywood": "IS 303: 1989",
    "particle board": "IS 3087: 1985",
    "medium density fibreboard": "IS 12406: 2003",
    "mdf board": "IS 12406: 2003",
    # Glass
    "float glass": "IS 14900: 2000",
    "toughened glass": "IS 2553 (Part 1): 1990",
    "wired glass": "IS 5437: 1994",
    # Bending / Tensile tests (often missed)
    "bend test": "IS 1599: 1985",
    "tensile testing": "IS 1608: 1995",
    "hardness test": "IS 1501: 1984",
    # Waterproofing
    "bituminous felt": "IS 1322: 1993",
    "waterproofing compound": "IS 2645: 2003",
    # Misc
    "broken stone": "IS 3068: 1986",
    "broken brick coarse aggregate": "IS 3182: 1986",
    "stone aggregate": "IS 5640: 1970",
    "crushed stone aggregate": "IS 5640: 1970",
    "hand broken stone": "IS 5640: 1970",
    "pozzolanic material": "IS 1344: 1981",
    "calcined clay pozzolana": "IS 1344: 1981",
    "burnt clay pozzolana": "IS 1344: 1981",
    "metakaolin": "IS 16354: 2015",
    "silica fume": "IS 15388: 2003",
    "precast concrete manhole": "IS 458: 2003",
    "rcc manhole cover": "IS 12592: 2002",
    "concrete paving blocks": "IS 15658: 2006",
    "interlocking paving blocks": "IS 15658: 2006",
    "hollow clay partition tiles": "IS 3952: 1988",
    "acid resistant tiles": "IS 4457: 1982",
    "acid resistant bricks": "IS 4457: 1982",
    "precast concrete lintels": "IS 9893: 1981",
    "concrete lintels": "IS 9893: 1981",
    "concrete sleepers": "IS 13920: 1993",
    "prestressed concrete sleepers": "IS 10297: 2002",
    "cement concrete kerb stones": "IS 10298: 1982",
    "kerb stone": "IS 10298: 1982",
    "fly ash for concrete": "IS 3812 (Part 1): 2003",
    "fly ash as admixture": "IS 3812 (Part 1): 2003",
    "granulated blast furnace slag": "IS 12089: 1987",
    "ggbs": "IS 12089: 1987",
    "stone masonry": "IS 1597 (Part 1): 1992",
    "rubble masonry": "IS 1597 (Part 1): 1992",
    "precast panels": "IS 14742: 1999",
    "no fines concrete": "IS 6313 (Part 1): 1981",
    "well point dewatering": "IS 9759: 1981",
    "concrete admixture": "IS 9103: 1999",
    "chemical admixture": "IS 9103: 1999",
    "superplasticizer": "IS 9103: 1999",
    "water reducing admixture": "IS 9103: 1999",
    "accelerating admixture": "IS 9103: 1999",
    "retarding admixture": "IS 9103: 1999",
    "reinforcement coupler": "IS 16172: 2014",
    "mechanical splices": "IS 16172: 2014",
    "bamboo reinforcement": "IS 6874: 2008",
    "fibre reinforced concrete": "IS 10262: 2019",
    "glass fibre": "IS 13879: 2014",
    "steel fibre": "IS 16019: 2012",
    "geotextile": "IS 14715: 2001",
    "bitumen for roads": "IS 73: 2013",
    "bituminous macadam": "IS 3840: 1966",
    "dense bituminous macadam": "IS 3840: 1966",
    "premix carpet": "IS 5317: 2000",
    "carpet": "IS 5317: 2000",
    "concrete mix design": "IS 10262: 2019",
    "mix design": "IS 10262: 2019",
    "compressive strength": "IS 516: 1959",
    "cube test": "IS 516: 1959",
    "concrete cube": "IS 516: 1959",
    "slump test": "IS 1199: 1959",
    "workability of concrete": "IS 1199: 1959",
    "water cement ratio": "IS 10262: 2019",
    "cover blocks": "IS 14687: 1999",
    "spacer blocks": "IS 14687: 1999",
    "centering formwork": "IS 14687: 1999",
    "fibre cement board": "IS 14862: 2000",
    "calcium silicate board": "IS 2110: 1980",
    "insulating board": "IS 3308: 1965",
    "wood wool board": "IS 3308: 1965",
    "asbestos cement flat sheet": "IS 2098: 1997",
    "ac flat sheet": "IS 2098: 1997",
    "ms hollow sections": "IS 4923: 1997",
    "square hollow section": "IS 4923: 1997",
    "rectangular hollow section": "IS 4923: 1997",
    "angle iron": "IS 2062: 2011",
    "channel section": "IS 2062: 2011",
    "i beam": "IS 2062: 2011",
    "h beam": "IS 2062: 2011",
    "corrugated galvanized iron sheet": "IS 277: 1992",
    "gi corrugated sheet": "IS 277: 1992",
    "pre-painted steel sheet": "IS 14246: 1995",
    "colour coated sheet": "IS 14246: 1995",
    "aluminium sections": "IS 733: 1983",
    "aluminium alloy": "IS 733: 1983",
    "copper conductor": "IS 8130: 1984",
    "electric cable": "IS 694: 2010",
    "control cable": "IS 1554 (Part 1): 1988",
    "pvc sheathed cable": "IS 1554 (Part 1): 1988",
    "lead acid battery": "IS 1651: 2013",
    "solar panel": "IS 14286: 1995",
    "fire resistant cable": "IS 7098 (Part 3): 1993",
    "door frame": "IS 4021: 1995",
    "wooden door": "IS 4021: 1995",
    "steel door frame": "IS 4351: 1976",
    "mild steel door": "IS 4351: 1976",
    "flush door": "IS 2202 (Part 1): 1999",
    "flush door shutters": "IS 2202 (Part 1): 1999",
    "rolling shutter": "IS 6248: 1979",
    "roller shutter": "IS 6248: 1979",
    "window frames": "IS 1948: 1961",
    "steel windows": "IS 1038: 1983",
    "aluminium windows": "IS 1948: 1961",
    "sanitary fittings": "IS 2556 (Part 1): 1994",
    "wash basin": "IS 2556 (Part 1): 1994",
    "water closet": "IS 2556 (Part 2): 2005",
    "toilet bowl": "IS 2556 (Part 2): 2005",
    "water storage tank": "IS 12701: 1996",
    "sintex tank": "IS 12701: 1996",
    "plastic water tank": "IS 12701: 1996",
    "sluice valve": "IS 14846: 2000",
    "gate valve": "IS 14846: 2000",
    "non return valve": "IS 5312 (Part 1): 1984",
    "check valve": "IS 5312 (Part 1): 1984",
    "ball valve": "IS 12191: 1987",
    "cp fittings": "IS 8931: 1993",
    "bib cock": "IS 8931: 1993",
    "pillar cock": "IS 8931: 1993",
    "roofing material": "IS 277: 1992",
    "corrugated iron sheet": "IS 277: 1992",
    "mangalore tiles": "IS 654: 1992",
    "terracotta tiles": "IS 654: 1992",
    "concrete roof tiles": "IS 5765: 1970",
    "pressed steel tanks": "IS 805: 1968",
    "overhead water tank": "IS 805: 1968",
    "anchor bolt": "IS 1367 (Part 1): 2002",
    "structural bolt": "IS 1367 (Part 1): 2002",
    "hex bolt": "IS 1364 (Part 1): 2002",
    "nut bolt": "IS 1364 (Part 1): 2002",
    "stainless steel": "IS 6911: 1992",
    "ss wire mesh": "IS 1568: 1982",
    "chain link fencing": "IS 2721: 1979",
    "barbed wire": "IS 278: 2006",
    "expanded metal": "IS 1081: 2018",
    "perforated sheet": "IS 5075: 1998",
    "anti-termite treatment": "IS 6313 (Part 2): 2001",
    "termite proofing": "IS 6313 (Part 2): 2001",
    "damp proof course": "IS 3067: 1988",
    "dpc": "IS 3067: 1988",
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
    'purpose','general','used','using','using','type','types','based',
    'made','make','includes','including','supply','supplied',
}

DOMAIN_EXPANSIONS = {
    "marine": ["sea water","chloride","aggressive","sulphate","submerged"],
    "coastal": ["sea water","chloride","corrosion","marine"],
    "decorative": ["architectural","white","ornamental","terrazzo"],
    "architectural": ["decorative","white","ornamental"],
    "lightweight": ["aac","cellular","pumice","cinder","aerated"],
    "masonry": ["brick","block","mortar","wall"],
    "sewage": ["drainage","sewer","effluent","corrosion","pipe"],
    "wiring": ["cable","wire","conductor","pvc","insulation"],
    "structural": ["reinforced","deformed","bar","rod","beam","section"],
    "roofing": ["sheet","corrugated","tile","asbestos","galvanized"],
    "plumbing": ["pipe","valve","fitting","water","drainage"],
    "flooring": ["tile","mosaic","terrazzo","floor","finish"],
    "waterproofing": ["bitumen","membrane","coating","damp","proof"],
    "formwork": ["centering","shuttering","framework","mould"],
    "prestressed": ["pre-stressed","precast","pretensioned","post-tensioned"],
    "hollow": ["block","cavity","void","partition","lightweight"],
    "reinforcement": ["rebar","rod","mesh","bar","deformed","wire"],
}


class BISRAGEngineV4:
    def __init__(self, standards_file: str):
        print(f"Loading standards from {standards_file}...")
        with open(standards_file, 'r', encoding='utf-8') as f:
            self.standards = json.load(f)
        self.std_by_number = {s['standardNumber']: s for s in self.standards}
        self._build_bm25_index()
        if ANTHROPIC_AVAILABLE:
            self.client = anthropic.Anthropic()
        print(f"Engine ready with {len(self.standards)} standards")

    def _tokenize(self, text: str) -> List[str]:
        if not text:
            return []
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s\-]', ' ', text)
        words = text.split()
        return [w.strip('-') for w in words if len(w.strip('-')) >= 2 and w.strip('-') not in STOPWORDS]

    def _build_bm25_index(self):
        print("Building BM25 index...")
        self.corpus_tokens = []
        for s in self.standards:
            doc = f"{s.get('standardNumber','')} {s.get('title','')} {s.get('description','')} {' '.join(s.get('keywords',[]))}"
            self.corpus_tokens.append(self._tokenize(doc))
        self.bm25 = BM25Okapi(self.corpus_tokens)
        print(f"BM25 index built with {len(self.corpus_tokens)} documents")

    def _direct_match(self, query: str) -> List[str]:
        """Check all direct mappings — partial substring match, scored by key length."""
        q = query.lower()
        hits = []
        for key, std in DIRECT_MAPPINGS.items():
            if key in q:
                hits.append((len(key), std))
        # Sort by key length desc (more specific match wins) and deduplicate
        hits.sort(key=lambda x: -x[0])
        seen, results = set(), []
        for _, std in hits:
            if std not in seen:
                seen.add(std)
                results.append(std)
        return results

    def _expand_query(self, query: str) -> str:
        q = query.lower()
        expanded = q
        tokens = q.split()
        for domain, terms in DOMAIN_EXPANSIONS.items():
            if domain in tokens or domain in q:
                expanded += " " + " ".join(terms)
        return expanded

    def _bm25_retrieve(self, query: str, top_k: int = 10) -> List[str]:
        expanded = self._expand_query(query)
        tokens = self._tokenize(expanded)
        if not tokens:
            return []
        scores = self.bm25.get_scores(tokens)
        indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        return [self.standards[i]['standardNumber'] for i in indices if scores[i] > 0]

    def _llm_rewrite_and_rank(self, query: str, candidates: List[str]) -> List[str]:
        """Use Claude to rewrite query keywords, then re-score with BM25. Fast — no full generation."""
        if not ANTHROPIC_AVAILABLE or not self.client:
            return candidates
        try:
            # Ask Claude only for 3-5 domain keywords + possible standard numbers
            prompt = (
                f"You are a BIS (Bureau of Indian Standards) expert. "
                f"Given this query: '{query}'\n"
                f"Return ONLY a JSON object with two keys:\n"
                f"  'keywords': list of 5-8 precise technical terms from BIS SP21 that best describe this product\n"
                f"  'standards': list of 1-3 likely IS standard numbers (e.g. 'IS 269: 1989') if you know them, else []\n"
                f"No explanation. Only JSON."
            )
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )
            text = response.content[0].text.strip()
            text = re.sub(r'```json|```', '', text).strip()
            data = json.loads(text)
            # Re-run BM25 with enriched query
            enriched_q = query + " " + " ".join(data.get("keywords", []))
            bm25_results = self._bm25_retrieve(enriched_q, top_k=10)
            # Prepend any known standards from LLM
            known = [s for s in data.get("standards", []) if s in self.std_by_number]
            merged = known[:]
            for s in bm25_results:
                if s not in merged:
                    merged.append(s)
            return merged[:5]
        except Exception as e:
            return candidates

    def retrieve(self, query: str, top_k: int = 5) -> List[str]:
        # 1. Direct mapping (always most accurate)
        direct = self._direct_match(query)

        # 2. BM25 retrieval
        bm25_results = self._bm25_retrieve(query, top_k=15)

        # 3. Merge: direct first, then BM25
        merged = direct[:]
        for s in bm25_results:
            if s not in merged:
                merged.append(s)

        # 4. If top result looks wrong (no strong direct match), try LLM rewrite
        if len(direct) == 0 and ANTHROPIC_AVAILABLE:
            merged = self._llm_rewrite_and_rank(query, merged)

        return merged[:top_k]


def process_batch(input_file: str, output_file: str, standards_file: str) -> bool:
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            queries = json.load(f)
        print(f"Loaded {len(queries)} queries")
        engine = BISRAGEngineV4(standards_file)
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
                "latency_seconds": round(latency, 3)
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
            print(f"  [{idx:2d}] {hit_status} {q['id']}: {retrieved[:3]}")

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)

        if results:
            eval_results = [r for r in results if 'expected_standards' in r]
            if eval_results:
                hits = sum(
                    1 for r in eval_results
                    if r['retrieved_standards'] and any(
                        ret.replace(' ', '').lower() in [s.replace(' ', '').lower() for s in r['expected_standards']]
                        for ret in r['retrieved_standards'][:3]
                    )
                )
                total = len(eval_results)
                avg_lat = total_latency / len(results)
                print(f"\n{'='*50}")
                print(f"RESULTS -> {output_file}")
                print(f"Hit Rate @3: {hits}/{total} = {100*hits/max(total,1):.1f}%")
                print(f"Avg Latency: {avg_lat:.3f}s")
                print(f"{'='*50}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        import traceback; traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(description='BIS Standards RAG Engine v4')
    parser.add_argument('--input', type=str, required=True)
    parser.add_argument('--output', type=str, required=True)
    parser.add_argument('--standards', type=str, default='../frontend/public/standards_enriched.json')
    args = parser.parse_args()

    if not Path(args.input).exists():
        print(f"Input not found: {args.input}"); sys.exit(1)
    if not Path(args.standards).exists():
        print(f"Standards not found: {args.standards}"); sys.exit(1)

    success = process_batch(args.input, args.output, args.standards)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

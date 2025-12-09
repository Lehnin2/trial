"""
EXTRACTEUR COMPLET ET EXHAUSTIF
- Extrait TOUS les champs sur TOUS les slides
- Résultat: found=true/false + value ou null
- Règles générales appliquées partout
"""

import json
import os
import time
import pickle
import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent.parent / ".env")
except ImportError:
    pass

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class CompleteExtraction:
    """Résultat d'extraction COMPLET (toujours présent)"""
    field_name: str
    found: bool  # True si trouvé, False sinon
    value: Optional[str]  # Valeur ou None
    confidence: float
    reasoning: str
    rule_id: str


@dataclass
class SlideCompleteResult:
    """Résultat COMPLET d'un slide (tous les champs)"""
    slide_number: int
    extractions: List[CompleteExtraction]  # Tous les champs, trouvés ou non
    language: str
    model_used: str
    processing_time_ms: float
    from_cache: bool = False


class SlideCache:
    """Cache par slide"""
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_file = cache_dir / "complete_cache.pkl"
        self.cache = self._load()

    def _load(self) -> Dict:
        if not self.cache_file.exists():
            return {}
        try:
            with open(self.cache_file, 'rb') as f:
                return pickle.load(f)
        except Exception:
            return {}

    def _save(self):
        with open(self.cache_file, 'wb') as f:
            pickle.dump(self.cache, f)

    def _get_key(self, slide_num: int, slide_content: List[Dict]) -> str:
        content_str = json.dumps(slide_content, sort_keys=True)
        content_hash = hashlib.md5(content_str.encode('utf-8')).hexdigest()
        return f"slide_{slide_num}_{content_hash}"

    def get(self, slide_num: int, slide_content: List[Dict]) -> Optional[SlideCompleteResult]:
        key = self._get_key(slide_num, slide_content)
        return self.cache.get(key)

    def put(self, slide_num: int, slide_content: List[Dict], result: SlideCompleteResult):
        key = self._get_key(slide_num, slide_content)
        self.cache[key] = result
        self._save()


class CompleteExtractor:
    """
    Extracteur qui analyse TOUS les champs sur CHAQUE slide
    Retourne TOUJOURS tous les champs (found=true/false)
    """
    
    def __init__(self, api_key: str, model: str):
        if not GROQ_AVAILABLE:
            raise ImportError("pip install groq")
        self.client = Groq(api_key=api_key)
        self.model = model
        logger.info(f"🤖 Extracteur Complet: {model}")

    def analyze_slide_complete(
        self, 
        slide_num: int, 
        slide_content: List[Dict], 
        all_fields: Dict[str, Dict],
        total_slides: int
    ) -> SlideCompleteResult:
        """
        Analyse UN slide pour TOUS les champs
        Retourne TOUS les champs (trouvés ou non)
        """
        start_time = time.time()
        
        slide_text = self._prepare_slide_text(slide_content)
        
        if not slide_text.strip():
            # Slide vide: tous les champs = non trouvés
            empty_extractions = [
                CompleteExtraction(
                    field_name=fname,
                    found=False,
                    value=None,
                    confidence=0.0,
                    reasoning="Slide vide",
                    rule_id=fspec.get("rule_id", "unknown")
                )
                for fname, fspec in all_fields.items()
            ]
            return SlideCompleteResult(slide_num, empty_extractions, "unknown", self.model, 0)

        logger.info(f"  📝 {len(slide_text)} caractères à analyser")
        logger.info(f"  🔍 {len(all_fields)} champs à vérifier")

        prompt = self._build_complete_prompt(slide_num, slide_text, all_fields, total_slides)

        try:
            ai_response = self._call_groq_api(prompt)
            parsed = self._parse_ai_response(ai_response)

            # Créer un dict des extractions retournées par l'IA
            found_fields = {
                item["field_name"]: item 
                for item in parsed.get("extractions", [])
            }

            # Construire la liste COMPLETE (tous les champs)
            complete_extractions = []
            
            for field_name, field_spec in all_fields.items():
                if field_name in found_fields:
                    # Champ trouvé par l'IA
                    ai_data = found_fields[field_name]
                    complete_extractions.append(CompleteExtraction(
                        field_name=field_name,
                        found=ai_data.get("found", False),
                        value=ai_data.get("value"),
                        confidence=ai_data.get("confidence", 0.0),
                        reasoning=ai_data.get("reasoning", ""),
                        rule_id=field_spec.get("rule_id", "unknown")
                    ))
                else:
                    # Champ NON trouvé par l'IA
                    complete_extractions.append(CompleteExtraction(
                        field_name=field_name,
                        found=False,
                        value=None,
                        confidence=0.0,
                        reasoning="Non trouvé dans ce slide",
                        rule_id=field_spec.get("rule_id", "unknown")
                    ))

            processing_time = (time.time() - start_time) * 1000
            
            found_count = sum(1 for e in complete_extractions if e.found)
            logger.info(f"  ✅ {found_count}/{len(complete_extractions)} champs trouvés")
            
            return SlideCompleteResult(
                slide_number=slide_num,
                extractions=complete_extractions,
                language=parsed.get("language", "unknown"),
                model_used=self.model,
                processing_time_ms=processing_time
            )

        except Exception as e:
            logger.error(f"❌ Erreur slide {slide_num}: {e}")
            # En cas d'erreur, retourner tous les champs comme non trouvés
            error_extractions = [
                CompleteExtraction(
                    field_name=fname,
                    found=False,
                    value=None,
                    confidence=0.0,
                    reasoning=f"Erreur: {str(e)}",
                    rule_id=fspec.get("rule_id", "unknown")
                )
                for fname, fspec in all_fields.items()
            ]
            return SlideCompleteResult(slide_num, error_extractions, "error", self.model, 0)

    def _prepare_slide_text(self, slide_content: List[Dict]) -> str:
        """Extrait texte du slide"""
        texts = []
        for element in slide_content:
            content = element.get("content", "").strip()
            if content:
                texts.append(content)
        return "\n".join(texts)

    def _build_complete_prompt(
        self, 
        slide_num: int, 
        slide_text: str, 
        all_fields: Dict[str, Dict],
        total_slides: int
    ) -> str:
        """
        Prompt pour extraction COMPLETE
        L'IA doit vérifier TOUS les champs
        """
        
        # Liste complète des champs
        fields_list = []
        for field_name, field_spec in all_fields.items():
            desc = field_spec.get('field_description', 'N/A')
            keywords = ', '.join(field_spec.get('search_keywords', []))
            rule_id = field_spec.get('rule_id', '')
            
            fields_list.append(f"- **{field_name}** (Règle: {rule_id})")
            fields_list.append(f"  Description: {desc}")
            fields_list.append(f"  Mots-clés: {keywords}")
            fields_list.append("")

        fields_str = "\n".join(fields_list)

        return f"""Tu es un auditeur expert analysant un document financier réglementaire.

**MISSION CRITIQUE:**
Tu dois vérifier la présence de **TOUS** les champs listés ci-dessous dans le contenu du slide.
Pour CHAQUE champ, tu DOIS indiquer s'il est trouvé ou non.

**CONTEXTE:**
- Slide: {slide_num}/{total_slides}
- Nombre de champs à vérifier: {len(all_fields)}

**LISTE COMPLÈTE DES CHAMPS À VÉRIFIER:**
{fields_str}

**CONTENU DU SLIDE:**
═══════════════════════════════════════════════════════════════════
{slide_text}
═══════════════════════════════════════════════════════════════════

**INSTRUCTIONS ABSOLUES:**

1. **PARCOURS LA LISTE COMPLÈTE** des champs ci-dessus
2. **POUR CHAQUE CHAMP**, détermine:
   - Est-il présent dans le slide? → found: true/false
   - Si présent: extrais la valeur EXACTE
   - Si absent: value: null

3. **RÈGLES D'EXTRACTION:**
   - Valeur = COPIE EXACTE du texte du slide
   - NE PAS inventer ou halluciner
   - NE PAS interpréter ou reformuler
   - Confiance:
     * 0.9-1.0 = Information explicite et claire
     * 0.6-0.8 = Information implicite mais évidente
     * 0.3-0.5 = Information ambiguë
     * 0.0 = Non trouvé

4. **IMPORTANT:**
   - Tu DOIS retourner TOUS les champs dans extractions[]
   - Même les champs non trouvés (found: false, value: null)
   - Nombre d'extractions = {len(all_fields)} (tous les champs)

**FORMAT JSON OBLIGATOIRE:**
```json
{{
  "language": "fra" | "eng" | "deu",
  "extractions": [
    {{
      "field_name": "nom_fonds",
      "found": true,
      "value": "ODDO BHF US Equity Active UCITS ETF",
      "confidence": 0.95,
      "reasoning": "Nom trouvé en titre du slide"
    }},
    {{
      "field_name": "date_document",
      "found": true,
      "value": "September 2025",
      "confidence": 0.9,
      "reasoning": "Date mentionnée en bas de slide"
    }},
    {{
      "field_name": "glossaire",
      "found": false,
      "value": null,
      "confidence": 0.0,
      "reasoning": "Aucune mention de glossaire sur ce slide"
    }},
    ... (TOUS les autres champs)
  ]
}}
```

**VÉRIFICATION FINALE:**
Avant de répondre, assure-toi que:
- ✅ Tu as vérifié TOUS les {len(all_fields)} champs
- ✅ Chaque champ a found: true OU false
- ✅ Les valeurs sont des copies exactes du slide
- ✅ Aucun champ n'est oublié

RÉPONDS UNIQUEMENT EN JSON.
"""

    def _call_groq_api(self, prompt: str) -> str:
        """Appel API Groq"""
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Tu es un expert en extraction exhaustive de données financières. Tu vérifies TOUS les champs demandés et réponds UNIQUEMENT en JSON valide. Tu ne jamais inventer d'informations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=4000,  # Augmenté pour réponse complète
                response_format={"type": "json_object"}
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"🚨 Erreur API: {e}")
            raise

    def _parse_ai_response(self, response_str: str) -> Dict:
        """Parse JSON"""
        try:
            # Nettoyage markdown
            response_str = response_str.strip()
            if response_str.startswith("```json"):
                response_str = response_str[7:]
            if response_str.startswith("```"):
                response_str = response_str[3:]
            if response_str.endswith("```"):
                response_str = response_str[:-3]
            
            response_str = response_str.strip()
            return json.loads(response_str)
        except json.JSONDecodeError as e:
            logger.error(f"🛑 Erreur JSON: {e}")
            logger.error(f"Réponse: {response_str[:1000]}")
            return {"extractions": []}


class CompletePipeline:
    """
    Pipeline qui extrait TOUS les champs sur TOUS les slides
    """

    def __init__(
        self, 
        pptx_path: Path, 
        checklist_path: Path, 
        cache_dir: Path, 
        api_key: str, 
        model: str
    ):
        logger.info("🚀 Initialisation Pipeline Complet...")
        
        self.pptx_path = pptx_path
        self.pptx_data = self._load_json(pptx_path)
        self.checklist_data = self._load_json(checklist_path)
        
        self.slides_content = self._group_slides()
        self.total_slides = len(self.slides_content)
        
        # TOUS les champs de TOUTES les règles
        self.all_fields = self._get_all_fields_with_rules()
        
        self.cache = SlideCache(cache_dir)
        self.extractor = CompleteExtractor(api_key, model)

        logger.info(f"✅ {self.total_slides} slides")
        logger.info(f"✅ {len(self.all_fields)} champs uniques à extraire")

    def run(self):
        """Lance extraction complète"""
        logger.info("\n" + "="*70)
        logger.info("🔥 EXTRACTION COMPLÈTE ET EXHAUSTIVE")
        logger.info("="*70)
        
        start_time = time.time()
        all_results = []

        # Pour CHAQUE slide
        for slide_num in sorted(self.slides_content.keys()):
            slide_content = self.slides_content[slide_num]
            
            logger.info(f"\n{'='*70}")
            logger.info(f"📄 SLIDE {slide_num}/{self.total_slides}")
            logger.info(f"{'='*70}")
            
            # Récupérer SEULEMENT les champs applicables à ce slide
            applicable_fields = self._get_applicable_fields_for_slide(slide_num)
            logger.info(f"  📋 {len(applicable_fields)} champs applicables")
            
            # Cache
            cached = self.cache.get(slide_num, slide_content)
            if cached and len(cached.extractions) == len(applicable_fields):
                logger.info("  🎯 CACHE HIT (complet)")
                cached.from_cache = True
                all_results.append(cached)
                continue
            
            # Analyse IA complète
            logger.info("  🤖 Analyse IA complète...")
            result = self.extractor.analyze_slide_complete(
                slide_num, 
                slide_content, 
                applicable_fields,
                self.total_slides
            )
            
            all_results.append(result)
            
            # Cache si la réponse est valide (même avec 0 champs)
            found_count = sum(1 for e in result.extractions if e.found)
            
            # Vérifier si la réponse est structurellement valide
            is_valid_response = (
                result.language != "error" and 
                len(result.extractions) == len(applicable_fields) and
                all(hasattr(e, 'found') for e in result.extractions)
            )
            
            if is_valid_response:
                self.cache.put(slide_num, slide_content, result)
                if found_count > 0:
                    logger.info(f"  💾 Cache OK ({found_count} champs trouvés)")
                else:
                    logger.info(f"  💾 Cache OK (slide vide: 0 champs)")
            else:
                logger.warning(f"  ⚠️ Réponse invalide: NON mis en cache")

        total_time = time.time() - start_time
        
        logger.info("\n" + "="*70)
        logger.info(f"✅ EXTRACTION TERMINÉE en {total_time:.1f}s")
        logger.info("="*70)
        
        # Rapport final
        final_report = self._format_complete_report(all_results)
        
        output_filename = self.pptx_path.stem.replace('_extraction', '') + '.complete_extraction.json'
        output_path = self.pptx_path.parent / output_filename
        
        self.save_results(final_report, output_path)

    def _get_applicable_fields_for_slide(self, slide_num: int) -> Dict[str, Dict]:
        """
        Récupère SEULEMENT les champs applicables à ce slide
        - Règles générales: tous les slides
        - Règles page_de_garde: slide 1 SEULEMENT
        - Règles slide_2: slide 2 SEULEMENT
        - Règles pages_suivantes: slides 3 à N-1
        - Règles page_finale: slide N SEULEMENT
        """
        applicable = {}
        
        for field_name, field_spec in self.all_fields.items():
            slide_location = field_spec.get("slide_location", "regles_generales")
            
            # Déterminer si ce champ s'applique à ce slide
            applies = False
            
            if slide_location == "regles_generales":
                # S'applique à TOUS les slides
                applies = True
            elif slide_location == "page_de_garde" and slide_num == 1:
                # S'applique SEULEMENT au slide 1
                applies = True
            elif slide_location == "slide_2" and slide_num == 2:
                # S'applique SEULEMENT au slide 2
                applies = True
            elif slide_location == "pages_suivantes" and 2 < slide_num < self.total_slides:
                # S'applique aux slides 3 à N-1
                applies = True
            elif slide_location == "page_finale" and slide_num == self.total_slides:
                # S'applique SEULEMENT au dernier slide
                applies = True
            
            if applies:
                applicable[field_name] = field_spec
        
        return applicable

    def _get_all_fields_with_rules(self) -> Dict[str, Dict]:
        """
        Récupère TOUS les champs de TOUTES les règles
        (générales + spécifiques)
        """
        all_fields = {}
        
        for category, rules in self.checklist_data.get("compliance_checklist", {}).items():
            for rule in rules:
                rule_id = rule["rule_id"]
                
                for field in rule.get("fields_to_extract", []):
                    field_name = field["field_name"]
                    
                    if field_name not in all_fields:
                        all_fields[field_name] = {
                            **field,
                            "rule_id": rule_id,
                            "rule_description": rule["rule_description"],
                            "slide_location": rule.get("slide_location", "regles_generales")
                        }
        
        return all_fields

    def _group_slides(self) -> Dict[int, List[Dict]]:
        """Regroupe par slides"""
        slides = {}
        for element in self.pptx_data.get("elements", []):
            page = element.get("page_number")
            if page:
                if page not in slides:
                    slides[page] = []
                slides[page].append(element)
        return slides

    def _format_complete_report(self, all_results: List[SlideCompleteResult]) -> Dict:
        """Génère rapport complet"""
        
        # Statistiques
        total_checks = sum(len(r.extractions) for r in all_results)
        total_found = sum(sum(1 for e in r.extractions if e.found) for r in all_results)
        cache_hits = sum(1 for r in all_results if r.from_cache)
        
        report = {
            "metadata": {
                "source_file": self.pptx_data.get("filename"),
                "extraction_strategy": "complete_exhaustive",
                "timestamp": datetime.now().isoformat(),
                "total_slides": len(all_results),
                "total_fields": len(self.all_fields),
                "total_checks": total_checks,
                "total_found": total_found,
                "total_missing": total_checks - total_found,
                "cache_hits": cache_hits,
                "success_rate": f"{(total_found/total_checks)*100:.1f}%"
            },
            "results_by_field": {},
            "results_by_slide": {}
        }

        # Par champ
        by_field = {}
        by_slide = {}
        
        for result in all_results:
            by_slide[result.slide_number] = []
            
            for extraction in result.extractions:
                field_name = extraction.field_name
                
                # Par champ
                if field_name not in by_field:
                    by_field[field_name] = []
                
                ext_dict = asdict(extraction)
                ext_dict["slide_number"] = result.slide_number
                by_field[field_name].append(ext_dict)
                
                # Par slide
                by_slide[result.slide_number].append(ext_dict)
        
        report["results_by_field"] = by_field
        report["results_by_slide"] = by_slide
        
        return report

    def save_results(self, report: Dict, output_path: Path):
        """Sauvegarde rapport"""
        logger.info(f"\n💾 Sauvegarde: {output_path}")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # Stats
        meta = report['metadata']
        logger.info("\n" + "="*70)
        logger.info("📊 STATISTIQUES FINALES")
        logger.info("="*70)
        logger.info(f"Slides analysés: {meta['total_slides']}")
        logger.info(f"Champs uniques: {meta['total_fields']}")
        logger.info(f"Total vérifications: {meta['total_checks']}")
        logger.info(f"✅ Trouvés: {meta['total_found']}")
        logger.info(f"❌ Manquants: {meta['total_missing']}")
        logger.info(f"🎯 Taux de succès: {meta['success_rate']}")
        logger.info(f"💾 Cache hits: {meta['cache_hits']}")
        logger.info("="*70)
        
        # Détail des champs
        logger.info("\n📋 RÉSUMÉ PAR CHAMP:")
        for field_name, extractions in report["results_by_field"].items():
            found_count = sum(1 for e in extractions if e["found"])
            logger.info(f"  • {field_name}: {found_count}/{len(extractions)} slides")

    def _load_json(self, path: Path) -> Dict:
        """Charge JSON"""
        if not path.exists():
            raise FileNotFoundError(f"{path}")
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)


# --- Main ---

if __name__ == "__main__":
    
    base_dir = Path(__file__).parent.parent.parent
    data_dir = base_dir / "DATA" / "extracted"
    cache_dir = base_dir / "scripts" / "extraction" / "cache_complete"

    pptx_path = data_dir / "XXX-PRS-GB-ODDO BHF US Equity Active ETF-20250630_6PN_extraction.json"
    checklist_path = data_dir / "compliance_checklist.json"

    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        logger.error("❌ GROQ_API_KEY manquante")
        exit(1)

    cache_dir.mkdir(exist_ok=True, parents=True)

    try:
        pipeline = CompletePipeline(
            pptx_path=pptx_path,
            checklist_path=checklist_path,
            cache_dir=cache_dir,
            api_key=groq_api_key,
            model="llama-3.3-70b-versatile"
        )
        pipeline.run()
        
        logger.info("\n✅ EXTRACTION COMPLÈTE TERMINÉE!")
        
    except Exception as e:
        logger.error(f"💥 Erreur: {e}", exc_info=True)
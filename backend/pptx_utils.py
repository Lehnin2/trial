import json
import win32com.client
from pathlib import Path
import sys

def add_compliance_comments(json_file, pptx_file):
    """
    Ajoute des commentaires natifs PowerPoint avec surlignage automatique
    
    Args:
        json_file: Chemin vers CONSOLIDATED_VIOLATIONS.json
        pptx_file: Chemin vers le fichier PowerPoint
    """
    print("=" * 80)
    print("🚀 GÉNÉRATEUR DE COMMENTAIRES DE CONFORMITÉ")
    print("=" * 80)
    
    # Vérifier que les fichiers existent
    if not Path(json_file).exists():
        print(f"❌ Erreur: {json_file} n'existe pas!")
        return
    
    if not Path(pptx_file).exists():
        print(f"❌ Erreur: {pptx_file} n'existe pas!")
        return
    
    # Charger les violations
    print(f"\n📂 Chargement des violations depuis: {json_file}")
    with open(json_file, 'r', encoding='utf-8') as f:
        violations_data = json.load(f)
    
    metadata = violations_data.get("metadata", {})
    print(f"   ✅ {metadata.get('total_violations', 0)} violations trouvées")
    print(f"   🔴 Critiques: {metadata.get('critical_violations', 0)}")
    print(f"   🟠 Majeures: {metadata.get('major_violations', 0)}")
    print(f"   🟡 Mineures: {metadata.get('minor_violations', 0)}")
    
    # Afficher la distribution des violations par page
    violations_by_page = violations_data.get("violations_by_page", {})
    print(f"\n📊 Distribution des violations par page:")
    for page_num_str in sorted(violations_by_page.keys(), key=lambda x: int(x)):
        count = len(violations_by_page[page_num_str])
        page_label = "Document-wide" if page_num_str == "0" else f"Page {page_num_str}"
        print(f"   • {page_label}: {count} violations")
    
    # Ouvrir PowerPoint
    print(f"\n📊 Ouverture de PowerPoint...")
    try:
        powerpoint = win32com.client.Dispatch("PowerPoint.Application")
        powerpoint.Visible = True
    except Exception as e:
        print(f"❌ Erreur lors de l'ouverture de PowerPoint: {e}")
        print("   💡 Assurez-vous que PowerPoint est installé et que pywin32 est installé:")
        print("   pip install pywin32")
        return
    
    # Ouvrir la présentation
    print(f"📄 Ouverture de la présentation: {pptx_file}")
    try:
        presentation = powerpoint.Presentations.Open(str(Path(pptx_file).absolute()))
    except Exception as e:
        print(f"❌ Erreur lors de l'ouverture de la présentation: {e}")
        return
    
    print(f"   ✅ {presentation.Slides.Count} slides trouvées")
    
    # Traiter chaque page
    violations_by_page = violations_data.get("violations_by_page", {})
    
    print("\n" + "=" * 80)
    print("📝 AJOUT DES COMMENTAIRES")
    print("=" * 80)
    
    total_comments = 0
    total_highlights = 0
    
    # Traiter d'abord les violations document-wide (page "0")
    if "0" in violations_by_page:
        doc_violations = violations_by_page["0"]
        print(f"\n📄 Violations DOCUMENT-WIDE (page 0):")
        print(f"   └─ {len(doc_violations)} violations détectées")
        print(f"   💡 Ces violations seront ajoutées à la première slide")
        
        # Ajouter à la slide 1 (première slide)
        if presentation.Slides.Count > 0:
            slide = presentation.Slides(1)
            comment_text = build_comment_text(0, doc_violations, is_document_wide=True)
            
            try:
                comment = slide.Comments.Add(
                    Left=50,
                    Top=150,  # Position différente pour distinguer
                    Author="Compliance AI - Document",
                    AuthorInitials="CA",
                    Text=comment_text
                )
                total_comments += 1
                print(f"   ✅ Commentaire document-wide ajouté à slide 1")
            except Exception as e:
                print(f"   ❌ Erreur ajout commentaire: {e}")
    
    # Traiter les pages normales
    for page_num_str, violations in violations_by_page.items():
        page_num = int(page_num_str)
        
        # Ignorer page 0 (déjà traitée) et pages inexistantes
        if page_num == 0:
            continue
            
        if page_num > presentation.Slides.Count:
            print(f"\n⚠️  Page {page_num}: N'existe pas dans PowerPoint (seulement {presentation.Slides.Count} slides)")
            continue
        
        slide = presentation.Slides(page_num)
        
        print(f"\n📄 Page {page_num}:")
        print(f"   └─ {len(violations)} violations détectées")
        
        # Construire le texte du commentaire
        comment_text = build_comment_text(page_num, violations)
        
        # Ajouter le commentaire natif
        try:
            # Position du commentaire (en haut à gauche de la slide)
            comment = slide.Comments.Add(
                Left=50,
                Top=50,
                Author="Compliance AI",
                AuthorInitials="CA",
                Text=comment_text
            )
            total_comments += 1
            print(f"   ✅ Commentaire ajouté")
            
        except Exception as e:
            print(f"   ❌ Erreur ajout commentaire: {e}")
        
        # Surligner les phrases exactes
        highlighted_count = 0
        for violation in violations:
            exact_phrase = violation.get("exact_phrase", "").strip()
            
            # Ignorer les phrases vides ou trop courtes
            if not exact_phrase or len(exact_phrase) < 15:
                continue
            
            # Ignorer certains types de phrases techniques non surlignables
            skip_phrases = [
                "Field check:",
                "Missing:",
                "Consistency issue:",
                "from Document**:",
                "Checked**:"
            ]
            
            if any(skip in exact_phrase for skip in skip_phrases):
                continue
            
            # Limiter à 300 caractères pour éviter les erreurs
            phrase_to_search = exact_phrase[:300]
            
            if highlight_text_in_slide(slide, phrase_to_search):
                highlighted_count += 1
                total_highlights += 1
        
        if highlighted_count > 0:
            print(f"   🎨 {highlighted_count} phrase(s) surlignée(s) en jaune")
    
    # Sauvegarder
    print("\n" + "=" * 80)
    print("💾 SAUVEGARDE")
    print("=" * 80)
    
    try:
        presentation.Save()
        print(f"✅ Présentation sauvegardée avec succès!")
        print(f"\n📊 RÉSUMÉ:")
        print(f"   • {total_comments} commentaires ajoutés")
        print(f"   • {total_highlights} phrases surlignées")
        print(f"\n💡 Ouvrez PowerPoint et cliquez sur 'Révision' > 'Afficher les commentaires'")
        print(f"   pour voir tous les commentaires dans la barre latérale droite.")
        
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde: {e}")
    
    print("\n" + "=" * 80)

def build_comment_text(page_num, violations, is_document_wide=False):
    """
    Construit le texte formaté du commentaire
    """
    if is_document_wide:
        lines = [f"🌐 VIOLATIONS DOCUMENT-WIDE"]
        lines.append("=" * 40)
        lines.append("Ces violations concernent l'ensemble")
        lines.append("du document et non une page spécifique")
    else:
        lines = [f"📋 VIOLATIONS - PAGE {page_num}"]
        lines.append("=" * 40)
    
    # Grouper par sévérité
    by_severity = {
        "critical": [],
        "major": [],
        "minor": [],
        "warning": []
    }
    
    for v in violations:
        severity = v.get("severity", "unknown")
        by_severity.setdefault(severity, []).append(v)
    
    # Icônes et labels
    severity_info = {
        "critical": ("🔴", "CRITIQUE"),
        "major": ("🟠", "MAJEURE"),
        "minor": ("🟡", "MINEURE"),
        "warning": ("⚠️", "AVERTISSEMENT")
    }
    
    # Ajouter les violations par sévérité
    for severity in ["critical", "major", "minor", "warning"]:
        violations_list = by_severity[severity]
        if not violations_list:
            continue
        
        icon, label = severity_info[severity]
        lines.append(f"\n{icon} {label} ({len(violations_list)})")
        lines.append("-" * 40)
        
        # Limiter à 3 violations par sévérité pour éviter un commentaire trop long
        for v in violations_list[:3]:
            rule_id = v.get("rule_id", "N/A")
            module = v.get("module", "")
            location = v.get("location", "")
            
            # Extraire le message principal
            comment = v.get("violation_comment", "")
            
            # Nettoyer le commentaire des patterns techniques
            if comment.startswith("["):
                # Format: [RULE_ID] message
                parts = comment.split("]", 1)
                if len(parts) > 1:
                    comment = parts[1].strip()
            
            if len(comment) > 200:
                comment = comment[:200] + "..."
            
            lines.append(f"\n[{rule_id}] {module}")
            if location and location != "document-wide":
                lines.append(f"📍 {location}")
            lines.append(f"📝 {comment}")
            
            # Action requise
            action = v.get("required_action", "")
            if action and action != "Review and correct violation":
                if len(action) > 150:
                    action = action[:150] + "..."
                lines.append(f"➜ {action}")
        
        # Si plus de 3 violations, indiquer le nombre restant
        if len(violations_list) > 3:
            lines.append(f"\n... et {len(violations_list) - 3} autre(s) {label.lower()}(s)")
    
    return "\n".join(lines)

def highlight_text_in_slide(slide, phrase_to_highlight):
    """
    Surligne du texte dans une slide
    """
    try:
        phrase_clean = phrase_to_highlight.strip()
        if not phrase_clean:
            return False
        
        found = False
        
        # Parcourir toutes les formes de la slide
        for shape in slide.Shapes:
            # Vérifier si la forme a du texte
            if not shape.HasTextFrame:
                continue
            
            try:
                text_range = shape.TextFrame.TextRange
                
                # Chercher la phrase (insensible à la casse)
                search_result = text_range.Find(
                    FindWhat=phrase_clean,
                    MatchCase=False,
                    WholeWords=False
                )
                
                if search_result:
                    # Surligner en jaune (wdYellow = 7 ou RGB)
                    # Pour PowerPoint, utiliser la propriété Highlight
                    try:
                        # Format RGB pour jaune: 255 (Red) + 255*256 (Green) + 0*65536 (Blue)
                        search_result.Font.Highlight.RGB = 65535  # Jaune
                        found = True
                    except:
                        # Alternative: utiliser la couleur de fond
                        search_result.Font.Fill.ForeColor.RGB = 0  # Noir
                        search_result.Font.Fill.BackColor.RGB = 65535  # Fond jaune
                        found = True
                
            except Exception as e:
                # Ignorer les formes qui ne peuvent pas être traitées
                continue
        
        return found
        
    except Exception as e:
        print(f"      ⚠️  Erreur surlignage: {e}")
        return False

def main():
    """
    Point d'entrée principal
    """
    if len(sys.argv) < 3:
        print("Usage: python script.py <violations.json> <presentation.pptx>")
        print("\nExemple:")
        print("  python script.py CONSOLIDATED_VIOLATIONS.json document.pptx")
        return
    
    json_file = sys.argv[1]
    pptx_file = sys.argv[2]
    
    add_compliance_comments(json_file, pptx_file)

if __name__ == "__main__":
    # Pour utilisation directe
    json_file = "CONSOLIDATED_VIOLATIONS.json"
    pptx_file = "pptx.pptx"
    
    add_compliance_comments(json_file, pptx_file)
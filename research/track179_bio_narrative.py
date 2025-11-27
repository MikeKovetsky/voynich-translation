import json
import os

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def main():
    verb_morphology = load_json('results/verb_morphology.json')
    
    # Define Bio pages (f75r-f84v)
    bio_pages = []
    for i in range(75, 85):
        bio_pages.append(f"f{i}r")
        bio_pages.append(f"f{i}v")
    
    bio_items = [item for item in verb_morphology if item.get('page') in bio_pages]
    
    # Define Recipes items (section="Recipes")
    recipes_items = [item for item in verb_morphology if item.get('section') == 'Recipes']
    
    # 1. Sentence Segmentation
    sentences = []
    current_sentence = []
    
    for i, item in enumerate(bio_items):
        current_sentence.append(item)
        
        # Check for sentence end
        # Split by 'dy' suffix or paragraph break (page change)
        is_dy = item.get('suffix') == 'dy'
        
        # Check for page change
        next_item = bio_items[i+1] if i + 1 < len(bio_items) else None
        page_change = next_item and next_item.get('page') != item.get('page')
        
        if is_dy or page_change or next_item is None:
            sentences.append({
                'id': len(sentences) + 1,
                'tokens': current_sentence,
                'page': item.get('page')
            })
            current_sentence = []

    # 2. Subject Tracking & 3. Action Chain
    narrative_steps = []
    actions = []
    
    previous_subject = None
    
    for sent in sentences:
        sent_verbs = [t for t in sent['tokens'] if t.get('prefix') == 'qok']
        
        # If no verbs, it might be a descriptive sentence or continuation
        if not sent_verbs:
            narrative_steps.append({
                'sentence_id': sent['id'],
                'page': sent['page'],
                'text': " ".join([t['original'] for t in sent['tokens']]),
                'type': 'Description',
                'subject': previous_subject,
                'actions': []
            })
            continue
            
        # For each verb, find its subject
        sent_actions = []
        current_sent_subject = None
        
        for verb_idx, verb in enumerate(sent_verbs):
            # Find verb position in sentence tokens
            # Note: verb is the dictionary object from verb_morphology
            # We need to find its index in sent['tokens']
            # Since there might be duplicate words, we need to be careful.
            # But we are iterating through unique objects if we use 'is' or keep track of index.
            # Let's iterate through tokens to find verbs.
            
            pass # logic below covers this
        
        # iterate through tokens to handle order correctly
        last_noun_candidate = None
        
        sentence_narrative = {
             'sentence_id': sent['id'],
             'page': sent['page'],
             'text': " ".join([t['original'] for t in sent['tokens']]),
             'type': 'Action',
             'steps': []
        }
        
        first_verb_encountered = False
        
        for t_idx, token in enumerate(sent['tokens']):
            is_verb = token.get('prefix') == 'qok'
            
            if is_verb:
                verb_stem = token.get('stem')
                subject = last_noun_candidate if last_noun_candidate else (previous_subject if not first_verb_encountered else "Implicit")
                
                action = {
                    'verb': token['original'],
                    'root': verb_stem,
                    'subject': subject,
                    'suffix': token.get('suffix')
                }
                sentence_narrative['steps'].append(action)
                sent_actions.append(action)
                actions.append(action) # For global graph
                
                previous_subject = subject # Update context
                first_verb_encountered = True
                last_noun_candidate = None # Reset local noun after verb consumes it? Or does it persist?
                                         # "The Water flows and mixes". "Water" is subject for both.
                                         # "Water flows. It mixes."
                                         # Simple heuristic: Reset last_noun_candidate.
                
            else:
                # Potential noun
                # Exclude obvious particles if we knew them.
                # For now, any non-verb is a noun candidate.
                last_noun_candidate = token['original']
                
                # Special handling: if we have a "Noun" right before a verb, it's the subject.
                # If we have multiple nouns, the last one is the most likely subject?
        
        if current_sent_subject is None and sent_actions:
            # Try to infer sentence level subject from first action
            current_sent_subject = sent_actions[0]['subject']

        narrative_steps.append(sentence_narrative)

    # 4. Terminology Check
    bio_terms = set(item.get('stem') for item in bio_items if item.get('stem'))
    recipe_terms = set(item.get('stem') for item in recipes_items if item.get('stem'))
    
    common_terms = bio_terms.intersection(recipe_terms)
    
    # Generate Outputs
    
    # Output 1: bio_narrative_flow.md
    with open('results/bio_narrative_flow.md', 'w') as f:
        f.write("# Bio Narrative Flow (f75r-f84v)\n\n")
        for step in narrative_steps:
            f.write(f"### Sentence {step['sentence_id']} ({step['page']})\n")
            f.write(f"**Text:** `{step['text']}`\n\n")
            
            if step.get('type') == 'Action':
                for action in step['steps']:
                    subj = action['subject']
                    verb = action['verb']
                    root = action['root']
                    f.write(f"- **Action:** `{root}` ({verb})\n")
                    f.write(f"  - **Subject:** `{subj}`\n")
            else:
                f.write("_Descriptive passage_\n")
            f.write("\n")

    # Output 2: bio_process_graph.json
    # We need a directed graph. Nodes = Actions/States? Or just verbs?
    # "Directed graph of the actions" -> Node = Verb Root? Edge = Sequence?
    
    graph_nodes = []
    graph_edges = []
    
    # Simple linear chain for now, maybe condense repeated nodes
    # Node: {id: "root", label: "root"}
    # Edge: {source: "root1", target: "root2", type: "next_step"}
    
    unique_roots = set(a['root'] for a in actions if a['root'])
    nodes_dict = {root: {'id': root, 'label': root, 'count': 0} for root in unique_roots}
    
    for a in actions:
        if a['root']:
            nodes_dict[a['root']]['count'] += 1
            
    graph_nodes = list(nodes_dict.values())
    
    for i in range(len(actions) - 1):
        u = actions[i].get('root')
        v = actions[i+1].get('root')
        if u and v:
            graph_edges.append({'source': u, 'target': v, 'relation': 'next'})
            
    # Condense edges
    edge_counts = {}
    for e in graph_edges:
        key = (e['source'], e['target'])
        edge_counts[key] = edge_counts.get(key, 0) + 1
        
    final_edges = [{'source': k[0], 'target': k[1], 'weight': v} for k, v in edge_counts.items()]
    
    graph_data = {
        'nodes': graph_nodes,
        'edges': final_edges
    }
    
    with open('results/bio_process_graph.json', 'w') as f:
        json.dump(graph_data, f, indent=2)

    # Output 3: track-179-results_summary.md
    with open('results/track-179-results_summary.md', 'w') as f:
        f.write("# Track 179: Bio Narrative Analysis Summary\n\n")
        f.write(f"- **Total Sentences:** {len(sentences)}\n")
        f.write(f"- **Total Actions (Verbs):** {len(actions)}\n")
        f.write(f"- **Unique Processes:** {len(unique_roots)}\n\n")
        
        f.write("## Common Terms with Recipes\n")
        f.write(f"Found {len(common_terms)} shared terms between Bio and Recipes.\n\n")
        f.write("| Term | Bio Occurrences | Recipe Occurrences |\n")
        f.write("|---|---|---|\n")
        
        # Sort by frequency in Bio
        sorted_common = sorted(list(common_terms), 
                             key=lambda t: sum(1 for i in bio_items if i.get('stem') == t), 
                             reverse=True)
        
        for term in sorted_common[:20]: # Top 20
            bio_count = sum(1 for i in bio_items if i.get('stem') == term)
            recipe_count = sum(1 for i in recipes_items if i.get('stem') == term)
            f.write(f"| `{term}` | {bio_count} | {recipe_count} |\n")

if __name__ == "__main__":
    main()

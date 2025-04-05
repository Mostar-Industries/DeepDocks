"""
DeepCAL++ Commentary Engine
This module generates human-readable explanations for logistics decisions
"""
from typing import List, Dict, Any

def generate_commentary(
    results: List[Dict[str, Any]], 
    forwarders: List[Dict[str, Any]]
) -> str:
    """
    Generate a human-readable commentary for TOPSIS analysis results
    
    Args:
        results: List of dictionaries containing ranked results
        forwarders: List of dictionaries containing forwarder details
        
    Returns:
        Markdown-formatted commentary
    """
    if not results or len(results) == 0:
        return "No results available for commentary."
    
    # Start with overview
    commentary = f"""
## Decision Analysis Commentary

Based on the TOPSIS analysis of {len(results)} logistics forwarders, **{results[0]['name']}** 
has been identified as the optimal choice with a score of **{results[0]['score']:.3f}**.
"""
    
    # Add ranking overview
    commentary += "\n### Ranking Summary\n\n"
    for i, result in enumerate(results):
        star_rating = "★" * min(5, max(1, round(result['score'] * 5)))
        commentary += f"{i+1}. **{result['name']}** ({star_rating}) - Score: {result['score']:.3f}\n"
    
    # Top performer analysis
    top_performer = results[0]
    commentary += f"\n### Why {top_performer['name']} Ranks First\n\n"
    
    strengths = []
    weaknesses = []
    
    # Analyze factors if available
    if all(k in top_performer for k in ['cost_factor', 'time_factor', 'reliability_factor']):
        # Determine strengths and weaknesses
        if top_performer['cost_factor'] < 0.3:  # Lower cost factor is better
            strengths.append("competitive pricing")
        elif top_performer['cost_factor'] > 0.7:
            weaknesses.append("higher cost compared to alternatives")
        
        if top_performer['time_factor'] < 0.3:  # Lower time factor is better
            strengths.append("fast delivery timeframe")
        elif top_performer['time_factor'] > 0.7:
            weaknesses.append("longer delivery time")
        
        if top_performer['reliability_factor'] > 0.7:
            strengths.append("excellent reliability")
        elif top_performer['reliability_factor'] < 0.3:
            weaknesses.append("lower reliability score")
        
        # Get raw values if available
        if all(k in top_performer for k in ['cost', 'time', 'reliability']):
            commentary += f"{top_performer['name']} offers a balance of "
            commentary += f"**${top_performer['cost']}** cost, "
            commentary += f"**{top_performer['time']} days** delivery time, and "
            commentary += f"**{top_performer['reliability']}%** reliability.\n\n"
        
        # Add strengths and weaknesses
        if strengths:
            commentary += "**Key strengths**: " + ", ".join(strengths) + ".\n\n"
        if weaknesses:
            commentary += "**Areas for consideration**: " + ", ".join(weaknesses) + ".\n\n"
    
    # Compare to alternatives
    if len(results) > 1:
        runner_up = results[1]
        commentary += f"\n### Comparison with {runner_up['name']} (Rank 2)\n\n"
        
        # Calculate differences
        if all(k in top_performer for k in ['cost', 'time', 'reliability']) and \
           all(k in runner_up for k in ['cost', 'time', 'reliability']):
            
            cost_diff = top_performer['cost'] - runner_up['cost']
            time_diff = top_performer['time'] - runner_up['time']
            reliability_diff = top_performer['reliability'] - runner_up['reliability']
            
            commentary += "Compared to the second-ranked option:\n\n"
            
            if cost_diff > 0:
                commentary += f"- {top_performer['name']} is **${abs(cost_diff):.2f} more expensive**\n"
            else:
                commentary += f"- {top_performer['name']} is **${abs(cost_diff):.2f} cheaper**\n"
            
            if time_diff > 0:
                commentary += f"- {top_performer['name']} is **{abs(time_diff)} days slower**\n"
            else:
                commentary += f"- {top_performer['name']} is **{abs(time_diff)} days faster**\n"
            
            if reliability_diff > 0:
                commentary += f"- {top_performer['name']} is **{abs(reliability_diff):.1f}% more reliable**\n"
            else:
                commentary += f"- {top_performer['name']} is **{abs(reliability_diff):.1f}% less reliable**\n"
    
    # Add final recommendation
    commentary += "\n### Recommendation\n\n"
    
    if top_performer['score'] > 0.8:
        confidence = "strongly recommend"
    elif top_performer['score'] > 0.6:
        confidence = "recommend"
    else:
        confidence = "suggest"
    
    commentary += f"Based on the comprehensive analysis, we {confidence} proceeding with **{top_performer['name']}**"
    
    if 'tracking' in forwarders[0]:
        top_tracking = next((f.get('tracking', False) for f in forwarders 
                            if f['name'] == top_performer['name']), False)
        if top_tracking:
            commentary += ", which also offers real-time shipment tracking"
    
    commentary += "."
    
    return commentary

def generate_voice_summary(results: List[Dict[str, Any]]) -> str:
    """
    Generate a concise voice-friendly summary of the analysis results
    
    Args:
        results: List of dictionaries containing ranked results
        
    Returns:
        Voice-friendly summary text
    """
    if not results or len(results) == 0:
        return "No results available for summary."
    
    # Create a simple, easy-to-listen summary
    top_result = results[0]
    
    summary = f"Analysis complete. {top_result['name']} is the recommended forwarder "
    summary += f"with a score of {top_result['score']:.2f}. "
    
    if len(results) > 1:
        runner_up = results[1]
        summary += f"The second option is {runner_up['name']} "
        summary += f"with a score of {runner_up['score']:.2f}. "
    
    # Add key factors if available
    if all(k in top_result for k in ['cost', 'time', 'reliability']):
        summary += f"{top_result['name']} offers delivery in {top_result['time']} days "
        summary += f"at a cost of ${top_result['cost']} "
        summary += f"with {top_result['reliability']}% reliability."
    
    return summary


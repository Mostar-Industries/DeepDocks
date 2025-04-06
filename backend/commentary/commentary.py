"""
DeepCAL++ Commentary Engine
This module generates human-readable explanations for logistics decisions
"""
from typing import List, Dict, Any
import random

def generate_commentary(
   results: List[Dict[str, Any]], 
   forwarders: List[Dict[str, Any]]
) -> str:
   """
   Generate a human-readable commentary for neutrosophic analysis results
   
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
Based on the neutrosophic multi-criteria analysis of {len(results)} logistics forwarders, **{results[0]['name']}** 
has been identified as the optimal choice with a score of **{results[0]['score']:.3f}**.
"""
   
   # Add ranking overview
   commentary += """

### Ranking Summary

"""
   for i, result in enumerate(results):
       star_rating = "★" * min(5, max(1, round(result['score'] * 5)))
       commentary += f"{i+1}. **{result['name']}** ({star_rating}) - Score: {result['score']:.3f}\n"
   
   # Top performer analysis
   top_performer = results[0]
   commentary += f"""

### Why {top_performer['name']} Ranks First

"""
   
   strengths = []
   weaknesses = []
   
   # Analyze factors if available
   if all(k in top_performer for k in ['costFactor', 'timeFactor', 'reliabilityFactor']):
       # Determine strengths and weaknesses
       if top_performer['costFactor'] < 0.3:  # Lower cost factor is better
           strengths.append("competitive pricing")
       elif top_performer['costFactor'] > 0.7:
           weaknesses.append("higher cost compared to alternatives")
       
       if top_performer['timeFactor'] < 0.3:  # Lower time factor is better
           strengths.append("fast delivery timeframe")
       elif top_performer['timeFactor'] > 0.7:
           weaknesses.append("longer delivery time")
       
       if top_performer['reliabilityFactor'] > 0.7:
           strengths.append("excellent reliability")
       elif top_performer['reliabilityFactor'] < 0.3:
           weaknesses.append("lower reliability score")
       
       # Get raw values if available
       if all(k in top_performer for k in ['cost', 'deliveryTime', 'reliability']):
           commentary += f"{top_performer['name']} offers a balance of "
           commentary += f"**${top_performer['cost']}** cost, "
           commentary += f"**{top_performer['deliveryTime']} days** delivery time, and "
           commentary += f"**{top_performer['reliability']}%** reliability.\n"
       
       # Add strengths and weaknesses
       if strengths:
           commentary += "**Key strengths**: " + ", ".join(strengths) + ".\n"
       if weaknesses:
           commentary += "**Areas for consideration**: " + ", ".join(weaknesses) + ".\n"
   
   # Compare to alternatives
   if len(results) > 1:
       runner_up = results[1]
       commentary += f"""

### Comparison with {runner_up['name']} (Rank 2)

"""
       
       # Calculate differences
       if all(k in top_performer for k in ['cost', 'deliveryTime', 'reliability']) and \
          all(k in runner_up for k in ['cost', 'deliveryTime', 'reliability']):
           
           cost_diff = top_performer['cost'] - runner_up['cost']
           time_diff = top_performer['deliveryTime'] - runner_up['deliveryTime']
           reliability_diff = top_performer['reliability'] - runner_up['reliability']
           
           commentary += "Compared to the second-ranked option:\n"
           
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
   
   # Add neutrosophic analysis insight
   commentary += """

### Neutrosophic Analysis Insight

"""
   commentary += f"The neutrosophic analysis considers uncertainty and incomplete information in the decision-making process. "
   commentary += f"This approach is particularly valuable for African logistics where data may be incomplete or imprecise. "
   
   # Add criterion contributions if available
   if 'criterionContributions' in top_performer:
       contributions = top_performer['criterionContributions']
       criteria_names = ['Cost', 'Time', 'Reliability', 'Tracking']
       
       # Find the highest contribution
       max_contribution_idx = contributions.index(max(contributions))
       max_criterion = criteria_names[max_contribution_idx]
       
       commentary += f"For {top_performer['name']}, the **{max_criterion.lower()}** factor had the most significant impact on its ranking.\n"
   
   # Add final recommendation
   commentary += """

### Recommendation

"""
   
   if top_performer['score'] > 0.8:
       confidence = "strongly recommend"
   elif top_performer['score'] > 0.6:
       confidence = "recommend"
   else:
       confidence = "suggest"
   
   commentary += f"Based on the comprehensive neutrosophic analysis, we {confidence} proceeding with **{top_performer['name']}**"
   
   if 'hasTracking' in top_performer:
       if top_performer['hasTracking']:
           commentary += ", which also offers real-time shipment tracking"
   
   commentary += "."
   
   # Add a touch of humor
   humor_lines = [
       f" Our quantum logistics algorithm is practically doing a victory dance for {top_performer['name']}!",
       f" If logistics were a sport, {top_performer['name']} would definitely be taking home the gold medal here.",
       f" I'd bet my last processing cycle that this is the optimal route for your needs.",
       f" This solution is so elegant, it deserves its own logistics award.",
       f" I calculated that faster than a caffeinated logistics manager on a Monday morning!"
   ]
   
   # Add humor 30% of the time
   if random.random() < 0.3:
       commentary += random.choice(humor_lines)
   
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
   if all(k in top_result for k in ['cost', 'deliveryTime', 'reliability']):
       summary += f"{top_result['name']} offers delivery in {top_result['deliveryTime']} days "
       summary += f"at a cost of ${top_result['cost']} "
       summary += f"with {top_result['reliability']}% reliability."
   
   return summary


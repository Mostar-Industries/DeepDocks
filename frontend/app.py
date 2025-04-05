import streamlit as st
import pandas as pd
import requests
import json

# Streamlit app title
st.title("Freight Forwarder Recommendation System")

# Sidebar for user inputs
st.sidebar.header("Shipment Details")

# User inputs
shipment_volume = st.sidebar.number_input("Shipment Volume (CBM)", min_value=1, value=10)
shipment_weight = st.sidebar.number_input("Shipment Weight (KG)", min_value=1, value=1000)
origin_country = st.sidebar.text_input("Origin Country", value="China")
destination_country = st.sidebar.text_input("Destination Country", value="USA")
distance = st.sidebar.number_input("Distance (KM)", min_value=1, value=10000)
cost_sensitivity = st.sidebar.slider("Cost Sensitivity", min_value=0.0, max_value=1.0, value=0.5)
time_sensitivity = st.sidebar.slider("Time Sensitivity", min_value=0.0, max_value=1.0, value=0.5)
reliability_sensitivity = st.sidebar.slider("Reliability Sensitivity", min_value=0.0, max_value=1.0, value=0.5)

# API endpoint
API_ENDPOINT = "http://localhost:8000/recommend"

# Function to make API request
def get_recommendations(volume, weight, origin, destination, distance, cost_sensitivity, time_sensitivity, reliability_sensitivity):
    payload = {
        "volume": volume,
        "weight": weight,
        "origin": origin,
        "destination": destination,
        "distance": distance,
        "cost_sensitivity": cost_sensitivity,
        "time_sensitivity": time_sensitivity,
        "reliability_sensitivity": reliability_sensitivity
    }
    response = requests.post(API_ENDPOINT, data=json.dumps(payload))
    return response.json()

# Button to trigger the recommendation
if st.sidebar.button("Get Recommendations"):
    try:
        # Call the API
        results = get_recommendations(shipment_volume, shipment_weight, origin_country, destination_country, distance, cost_sensitivity, time_sensitivity, reliability_sensitivity)
        
        # Check if results is valid and has data
        if results and isinstance(results, list) and len(results) > 0:
            # Ensure the first result has the required fields
            best_forwarder = results[0].get('name', 'Unknown')
            best_score = results[0].get('score', 0)
            
            commentary = f"Based on your inputs, the recommended forwarder is **{best_forwarder}**. "
            commentary += f"This forwarder offers a good balance of cost, time, and reliability for your shipment from {origin_country} to {destination_country}."
            
            # Display results
            st.header("Analysis Results")
            
            # Create a results dataframe for display
            results_df = pd.DataFrame(results)
            if 'rank' in results_df.columns:
                results_df.set_index('rank', inplace=True)
            
            # Display the table with only columns that exist
            available_columns = [col for col in ['name', 'score', 'cost_factor', 'time_factor', 'reliability_factor'] 
                                if col in results_df.columns]
            if available_columns:
                st.dataframe(results_df[available_columns])
            else:
                st.dataframe(results_df)
            
            # Display the commentary
            st.subheader("Analysis Commentary")
            st.markdown(commentary)
            
            # Add recommendation box
            st.success(f"**Recommended Forwarder: {best_forwarder}**\n\n{best_forwarder} achieved the highest TOPSIS score of {best_score:.3f}, making it the optimal choice for this shipment.")
        else:
            st.header("Analysis Results")
            st.warning("No valid recommendations could be generated based on the provided inputs. Please adjust your parameters and try again.")
    except Exception as e:
        st.error(f"An error occurred while processing your request: {str(e)}")
        st.info("Please check your input data and try again.")


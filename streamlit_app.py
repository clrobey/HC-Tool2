import streamlit as st
import numpy as np
import altair as alt
import pandas as pd

def calculate_probability(Hct_initial, Hct_nadir, Plt_initial, Plt_nadir, GH_days):
    if GH_days <= 0 or Hct_initial <= 0 or Plt_initial <= 0:
        return None  # Avoid division errors
    
    # Calculate percent change per day
    pct_change_Hct = ((Hct_initial - Hct_nadir) / (Hct_initial * GH_days)) * 100
    pct_change_Plt = ((Plt_initial - Plt_nadir) / (Plt_initial * GH_days)) * 100
    
    # Apply logistic regression formula
    logit = -1.994634 + (0.663276 * pct_change_Plt) - (0.769649 * pct_change_Hct)
    probability = 1 / (1 + np.exp(-logit))
    
    return probability, pct_change_Hct, pct_change_Plt

def plot_probability_meter(probability):
    df = pd.DataFrame({"Probability": [probability * 100]})
    
    # Define color based on probability value
    df["Color"] = df["Probability"].apply(lambda x: "red" if x > 70 else "yellow" if x > 30 else "green")
    
    chart = alt.Chart(df).mark_bar(size=30).encode(
        x=alt.X("Probability:Q", scale=alt.Scale(domain=[0, 100]), title="Probability (%)"),
        y=alt.value(10),
        color=alt.Color("Color:N", scale=None)  # Using precomputed color
    ).properties(width=500, height=50)
    
    st.altair_chart(chart)

# Streamlit App
st.title("Measurable Clot Probability Calculator")
st.write("Enter the patient's lab values and duration of gross hematuria.")

# User Inputs
Hct_initial = st.number_input("Hematocrit at GH onset", min_value=0.0, format="%.2f")
Hct_nadir = st.number_input("Hematocrit nadir", min_value=0.0, format="%.2f")
Plt_initial = st.number_input("Platelet count at GH onset", min_value=0, format="%d")
Plt_nadir = st.number_input("Platelet count nadir", min_value=0, format="%d")
GH_days = st.number_input("Duration of Gross Hematuria (days)", min_value=1, format="%d")

# Compute Probability
if st.button("Calculate Probability"):
    result = calculate_probability(Hct_initial, Hct_nadir, Plt_initial, Plt_nadir, GH_days)
    if result is not None:
        probability, pct_change_Hct, pct_change_Plt = result
        st.write(f"### Probability of Measurable Clot: {probability:.2%}")
        st.write(f"#### Percent Decrease in Hematocrit per Day: {pct_change_Hct:.2f}%")
        st.write(f"#### Percent Decrease in Platelet Count per Day: {pct_change_Plt:.2f}%")
        plot_probability_meter(probability)
    else:
        st.error("Invalid input values. Please ensure all inputs are positive and GH duration is at least 1 day.")

import matplotlib.pyplot as plt
import streamlit as st

def generate_pie_chart(data_column, start_value, end_value):
    # Slice the data based on the selected range
    selected_data = data_column.iloc[start_value-1:end_value]  # Adjusting to 0-based index
    
    # Count the occurrences of each category (e.g., country) in the sliced data
    category_counts = selected_data.value_counts()
    
    # Check if there is data to plot
    if category_counts.empty:
        return "No data available to plot."
    
    # Generate the pie chart based on category counts
    fig, ax = plt.subplots()
    wedges, texts, autotexts = ax.pie(
        category_counts, 
        labels=category_counts.index, 
        autopct='%1.1f%%', 
        startangle=90
    )

    # Add legend
    ax.legend(wedges, category_counts.index, title="Categories", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    ax.set_title("Pie Chart")
    
    # Display the pie chart in Streamlit
    st.pyplot(fig)

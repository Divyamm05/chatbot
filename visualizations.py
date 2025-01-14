import matplotlib.pyplot as plt

def generate_pie_chart(data_column, start_value, end_value):
    # Slice the data based on the selected range
    selected_data = data_column.iloc[start_value-1:end_value]  # Adjusting to 0-based index
    
    # Count the occurrences of each category (e.g., country) in the sliced data
    category_counts = selected_data.value_counts()
    
    # Generate the pie chart based on category counts
    fig, ax = plt.subplots()
    wedges, texts, autotexts = ax.pie(category_counts, labels=category_counts.index, autopct='%1.1f%%')
    ax.legend(wedges, category_counts.index,
              title="Categories",
              loc="center left",
              bbox_to_anchor=(1, 0, 0.5, 1))
    plt.show()

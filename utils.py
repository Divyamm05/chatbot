import json
import os
import pandas as pd

CHAT_HISTORY_FILE = 'chat_history.json'

def load_chat_history():
    try:
        if os.path.exists(CHAT_HISTORY_FILE):
            with open(CHAT_HISTORY_FILE, 'r') as file:
                return json.load(file)
        return []  # Return an empty list if the file doesn't exist
    except json.JSONDecodeError as e:
        return []  # Return an empty list if the file is corrupted

def save_chat_history(messages):
    with open(CHAT_HISTORY_FILE, 'w') as file:
        json.dump(messages, file)

def generate_chart_description(chart_type, data):
    if isinstance(data, pd.Series):
        values = data.tolist()
        categories = data.index.tolist()
    else:
        categories = list(data.columns)
        values = data.iloc[0].tolist()

    if chart_type == "pie":
        total = sum(values)
        percentages = [f"{value:.1f}% ({value}/{total})" for value in values]
        description = f"Pie Chart: {', '.join([f'{category}: {percentage}' for category, percentage in zip(categories, percentages)])}"
    elif chart_type == "bar":
        description = f"Bar Chart: Values for categories: {', '.join([f'{category}: {value}' for category, value in zip(categories, values)])}"
    else:
        description = "Chart type not supported."

    return description

import json 
from datetime import date
from pathlib import Path

PLATFORMS = ("UberEats", "DoorDash")
DATA_FILE = Path(__file__).with_name("deliveries.json")

# Calculating earnings after costs
def calculate_earnings(payment, distance, minutes, cost_per_km=0.25): #defining the function
    # Generating error if user defines non acceptable value 
    if payment < 0 or distance <=0 or minutes <= 0 or cost_per_km < 0:
        raise ValueError("Payment, distance, minutes, and cost per km must be positive values.")

    # calculating expense incured by the driver and calculating net earnings 
    expenses = distance * cost_per_km
    after_costs = payment - expenses

    # returning variables
    return {
        "expenses": expenses,
        "after_costs": after_costs,
        "gross_per_hour": after_costs / minutes * 60,
        "gross_per_km": payment / distance, 
        "after_costs_per_hour": after_costs / minutes * 60,
    }

# JSON data storage
def load_deliveries(): #defining json file 
    # if there is no data file that exists just return empty
    if not DATA_FILE.exists():
        return[]

    #open file in read mode and save it under the variable name file
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        deliveries = json.load(file) #convert Json content to python objects 

    return deliveries # return the deliveries 

# function to save deliveries 
def save_deliveries(deliveries): 
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(deliveries, file, indent=4)

# fucntion to add delivery 
def add_delivery(deliveries, platform, payment, distance, minutes, delivery_date):
    # condition to check if the platform is valid
    if platform not in PLATFORMS:
        raise ValueError("Choose either UberEats or Doordash")

    calculate_earnings(payment, distance, minutes)

    # condition to check if the delivery date is valid 
    if not isinstance(delivery_date, date):
        raise ValueError("Delivery date must be valid")

    new_delivery = {
        "date": delivery_date.isoformat(),
        "payment": payment,
        "platform": platform,
        "distance": distance,
        "minutes": minutes,
    }

    updated_deliveries  = deliveries + [new_delivery]
    save_deliveries(updated_deliveries)
    return updated_deliveries

# function for Reports and Comparisons
def summarize_deliveries(deliveries, cost_per_km=0.25):
    count = len(deliveries)
    gross = sum(record["payment"] for record in deliveries)
    distance = sum(record["distance"] for record in deliveries)
    minutes = sum(record["minutes"] for record in deliveries)
    expenses = distance * cost_per_km

    return {
        "count": count,
        "gross": gross,
        "distance": distance,
        "minutes": minutes,
        "expensess": expenses,
        "after_costs": gross - expenses,
        "average_payment": gross / count if count else 0,
        "gross_per_hour": gross / minutes * 60 if minutes else 0,
    }

# Function to return platform deliveries 
def platform_deliveries(deliveries, platform):
    return [record for record in deliveries if record["platform"] == platform]
    


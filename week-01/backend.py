import json 
from datetime import date
from pathlib import Path

Platforms = ("UberEats", "DoorDash")
Data_File = Path(__file__).with_name("deliveries.json")

# Calculating earnings after costs
def calculate_earnings(payment, distance, time, cost_per_km=0.25): #defining the function
    # Generating error if user defines non acceptable value 
    if payment < 0 or distance <=0 or time <= 0 or cost_per_km < 0:
        raise ValueError("Payment, distance, time, and cost per km must be positive values.")

    # calculating expense incured by the driver and calculating net earnings 
    drivers_Expense = distance * cost_per_km
    net_earnings = payment - drivers_Expense

    # returning variables
    return {
        "drivers_Expense": drivers_Expense,
        "net_earnings": net_earnings,
        "gross_per_hour": net_earnings / time * 60,
        "gross_per_km": payment / distance, 
        "after_costs_per_hour": net_earnings / time * 60,
    }

# JSON data storage
def load_deliveries(): #defining json file 
    # if there is no data file that exists just return empty
    if not Data_File.exists():
        return[]

    #open file in read mode and save it under the variable name file
    with open(Data_File, "r", encoding="utf-8") as file:
        deliveries = json.load(file) #convert Json content to python objects 

    return deliveries # return the deliveries 

# function to save deliveries 
def save_deliveries(deliveries): 
    with open(Data_File, "w", encoding="utf-8") as file:
        json.dump(deliveries, file, indent=4)

# fucntion to add delivery 
def add_delivery(deliveries, platform, payment, distance, time, delivery_date):
    # condition to check if the platform is valid
    if platform not in Platforms:
        raise ValueError("Choose either UberEats or Doordash")

    calculate_earnings(payment, distance, time)

    # condition to check if the delivery date is valid 
    if not isinstance(delivery_date, date):
        raise ValueError("Delivery date must be valid")

    
    





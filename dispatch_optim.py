from typing import List, Dict, Tuple

# Goal : solve a simple economic dispatch problem
# ------------------------------------------------------- Description -------------------------------------------------------------------------------------
# The load is the continuous demand of power. 
# The total load at each moment in time is forecasted. For instance for Belgium you can see the load forecasted by the grid operator here.
# At any moment in time, all available powerplants need to generate the power to exactly match the load. The cost of generating power can 
# be different for every powerplant and is dependent on external factors: The cost of producing power using a turbojet, that runs on kerosine, 
# is higher compared to the cost of generating power using a gas-fired powerplant because of gas being cheaper compared to kerosine and because of 
# the thermal efficiency of a gas-fired powerplant being around 50% (2 units of gas will generate 1 unit of electricity) while that of a turbojet is
# only around 30%. The cost of generating power using windmills however is zero. Thus deciding which powerplants to activate is dependent on the merit-order.

def compute_cost(fuels: dict, plants: dict)->float:
    """
    Compute cost for a plant according to it's type.
    """
    if plants["type"] == "gasfired":
        cost = fuels["gas(euro/MWh)"] / plants["efficiency"]
    elif plants["type"] == "turbojet":
        cost = fuels["kerosine(euro/MWh)"] / plants["efficiency"]
    else:
        cost = 0 #Wind are considered generating power at zero price.
    return cost


def dp_solving(payload: dict) -> List[Dict[str, (str | float)]]:
  """
  Dynamic programming approach to find the least-cost operation of dispatching 
  power generation between a given set of plants and s.t. their pmin and pmax.
  """
  # Merit Order sorting: windturbine first (due to zero cost) then based on cost
  sorted_plants = sorted(payload["powerplants"], key=lambda x: (x["type"]=="windturbine", compute_cost(payload["fuels"], x)))

  # Convert load to steps (multiples of 0.1 MWh) for easier DP calculations
  load_steps = int(round(payload["load"] * 10))

  # Initialize DP: {total allocation steps: (total cost, list of allocations for each plant)}
  dp: Dict[int, Tuple[float, List[float]]] = {0: (0.0, [])}
  
  # For each plant we construct all possibles allocation values
  for plant in sorted_plants:
    # Declaration of the update Dict
    new_dp: Dict[int, Tuple[float, List[float]]] = {}

    if plant["type"]=="windturbine":
      wind_prod = round(plant["pmax"] * payload["fuels"]["wind(%)"]/100, 1)
      allocations = [0.0, wind_prod]

    else:
      allocations = [0.0]
      current = plant["pmin"]

      while current <= plant["pmax"]:
        allocations.append(round(current, 1))
        current += 0.1
    
    # For each possible total allocation in the current DP state
    for steps in dp:
      current_cost, current_allocations = dp[steps]

      # Iteration over possibles values of allocation for the new plant
      for alloc in allocations:
        # Calculate the new cost and total allocation based on the current allocation and the plant's cost
        new_cost = current_cost + (alloc * compute_cost(payload["fuels"], plant))
        new_steps = steps + int(round((alloc * 10)))

        if new_steps > load_steps:
          continue
        
        # Update DP if the new allocation is better (lower cost or new total allocation)
        if new_steps not in new_dp or new_cost < new_dp[new_steps][0]:
          temp_allocations = current_allocations.copy()
          temp_allocations.append(alloc)
          new_dp[new_steps] = (new_cost, temp_allocations)
    #update the dp dictionnary for next plant
    dp = new_dp

  if load_steps not in dp:
    raise ValueError("Impossible to find a solution.")
  
  _, allocations = dp[load_steps]

  mapping = {p["name"]: a for p, a in zip(sorted_plants, allocations)}
  return [
    {"name": p["name"], "p": mapping[p["name"]]} for p in payload["powerplants"]
  ]


if __name__ == "__main__":
   
    payload = {
    "load": 910,
    "fuels":
    {
        "gas(euro/MWh)": 13.4,
        "kerosine(euro/MWh)": 50.8,
        "co2(euro/ton)": 20,
        "wind(%)": 60
    },
    "powerplants": [
        {
        "name": "gasfiredbig1",
        "type": "gasfired",
        "efficiency": 0.53,
        "pmin": 100,
        "pmax": 460
        },
        {
        "name": "gasfiredbig2",
        "type": "gasfired",
        "efficiency": 0.53,
        "pmin": 100,
        "pmax": 460
        },
        {
        "name": "gasfiredsomewhatsmaller",
        "type": "gasfired",
        "efficiency": 0.37,
        "pmin": 40,
        "pmax": 210
        },
        {
        "name": "tj1",
        "type": "turbojet",
        "efficiency": 0.3,
        "pmin": 0,
        "pmax": 16
        },
        {
        "name": "windpark1",
        "type": "windturbine",
        "efficiency": 1,
        "pmin": 0,
        "pmax": 150
        },
        {
        "name": "windpark2",
        "type": "windturbine",
        "efficiency": 1,
        "pmin": 0,
        "pmax": 36
        }
    ]
    }

    results = dp_solving(payload=payload)
    print(results)


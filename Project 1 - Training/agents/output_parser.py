from langchain_core.runnables import RunnableLambda

def final_parser(state):
    output = {
        "is_anomaly": state.get("is_anomaly", False),
    }

    if state.get("is_anomaly"):
        output["reason"] = state.get("reason", "Anomali tidak diketahui")
        return output
    
    output["image_for_batch_expiry"] = state.get("image_for_batch_expiry", [])
    output["image_for_quantity"] = state.get("image_for_quantity", [])
    output["item_name"] = state.get("item_name", "")

    return output

final_parser = RunnableLambda(final_parser)

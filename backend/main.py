from fastapi import FastAPI, HTTPException, Depends, Query # Importing FastAPI, HTTPException, Depends, and Query
from fastapi.middleware.cors import CORSMiddleware # Importing CORSMiddleware
from pydantic import BaseModel # Importing BaseModel
from typing import Dict, List, Optional # Importing Dict, List, and Optional
import re # Importing re for regular expressions
import json # Importing json

# Creating a FastAPI instance
app = FastAPI()

# CORS middleware to allow requests from a frontend (e.g., localhost for testing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Function to load JSON data from a file
def load_json(filename: str) -> dict:
    with open(filename, 'r') as f:
        return json.load(f)
    
users_db = load_json('users.json') # Load Test user data from JSON files
orders = load_json('orders.json') # Load Test order data from JSON files
payment_history = load_json('payments.json') # Load Test payment history data from JSON files

# Load product data from a JSON file
with open('products.json', 'r') as f:
    products = json.load(f)

# Product list to filter by (provided list)
product_list = [
   "Gaming Console", "Fitness Tracker", "coffee maker", "Coffee Makers",
      "Bag", "Bags", "watch", "watches", "shoe", "shoes", "headphone", "headphones", "laptop", "laptops", 
      "smartphone", "smartphones", "tablet", "tablets", "smartwatch", "smartwatches", 
      "speaker", "speakers", "television", "televisions", "camera", "cameras", "keyboard", "keyboards", 
      "mouse", "console", "consoles", "tracker", "trackers", "bag", "bags", "oven", "ovens", 
      "refrigerator", "refrigerators", "conditioner", "conditioners", "fan", "fans", "toaster", "toasters"
]

# User model
class User(BaseModel):
    username: str
    email: str

# Chat request and response models
class ChatRequest(BaseModel):
    message: str

# Chat response model
class ChatResponse(BaseModel):
    response: str
    confidence: float
    products: Optional[List[Dict]] = None

# Function to simulate user authentication (using user_id as query param for now)
def get_current_user(user_id: str = Query(..., description="User ID")):
    user = users_db.get(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated")
    return user

# Function to get orders for a specific user
def get_orders_for_user(user: Dict) -> List[Dict]:
    return [order for order in orders.values() if order['user_id'] == user['username']]

# Function to handle order-related queries
def handle_order_query(message: str, user: Dict) -> tuple[str, float]:
    message = message.lower()
    
    # Get all orders for the user
    user_orders = get_orders_for_user(user)

    # If the user has no orders, return no orders found message
    if not user_orders:
        return "No orders found for your account.", 0.7
    
    # Handle specific queries based on the user's message
    if "last order" in message:
        last_order = sorted(user_orders, key=lambda x: x['eta'] or '0', reverse=True)[0]  # Sort by ETA
        response = f"Your last order is {last_order['status']}. "
        if last_order['eta']:
            response += f"Estimated delivery in {last_order['eta']}."
        return response, 0.9

    # Check for order status or tracking queries
    if "order status" in message or "tracking" in message:
        response = "\n".join([f"Order {order_id} is {order['status']}" + (f". Estimated delivery in {order['eta']}." if order['eta'] else "") for order_id, order in orders.items() if order['user_id'] == user['username']])
        return response, 0.9

    # Check for last order status or tracking queries
    if "last order status" in message or "last order tracking" in message:
        last_order = sorted(user_orders, key=lambda x: x['eta'] or '0', reverse=True)[0]
        response = f"Your last order ({last_order['status']}) is {last_order['status']}. "
        if last_order['eta']:
            response += f"Estimated delivery in {last_order['eta']}."
        return response, 0.9
    
    # Match order ID from message (e.g., ORD123)
    order_match = re.search(r'\bord\d+\b', message)
    if order_match:
        order_id = order_match.group().upper()
        order = orders.get(order_id)
        if order and order['user_id'] == user['username']:
            response = f"Order {order_id} is {order['status']}. "
            if order['eta']:
                response += f"Estimated delivery in {order['eta']}."
            return response, 0.9
        else:
            return f"Order {order_id} not found for your account.", 0.7
    
    # If no matching query is found, ask for the order ID
    return "Please provide your order number (e.g., ORD123) to check its status.", 0.7

# Helper function to get user's payment history
def get_payment_history(user: Dict) -> str:
    history = payment_history.get(user['username'], [])
    if history:
        return "\n".join([f"Order {item['order_id']}: ${item['amount']} - {item['status']} on {item['date']}" for item in history])
    return "No payment history found."

# Function to check for payment status by order ID
def check_payment_status(order_id: str, user: Dict) -> str:
    payment = next((p for p in payment_history.get(user['username'], []) if p['order_id'] == order_id), None)
    if payment:
        return f"Payment for order {order_id}: ${payment['amount']} - Status: {payment['status']} on {payment['date']}"
    return f"No payment information found for order {order_id}."

# Function to handle payment failure reasons
def payment_failure_reasons() -> str:
    return """
Possible reasons for payment failure:
1. Insufficient funds in your account.
2. Invalid payment details (credit card information).
3. Payment gateway timeout or issues.
4. Network connectivity problems.
5. Expired payment method.
Please ensure your payment details are correct and try again. If the problem persists, contact support.
"""

# Function to handle the payment-related queries
def handle_payment_query(message: str, user: Dict) -> tuple[str, float]:
    message = message.lower()
    
    # Last payment query
    if "last payment" in message:
        last_payment = sorted(payment_history.get(user['username'], []), key=lambda x: x['date'], reverse=True)[0]
        return f"Your last payment was for order {last_payment['order_id']}, amount: ${last_payment['amount']} on {last_payment['date']}. Status: {last_payment['status']}", 0.9
    
    # All payments query
    if "all payments" in message or "payment history" in message:
        return get_payment_history(user), 0.9
    
    # Payment status by order ID
    order_match = re.search(r'\bord\d+\b', message)
    if order_match:
        order_id = order_match.group().upper()
        return check_payment_status(order_id, user), 0.9
    
    # Payment failure reasons
    if "payment failed" in message:
        return payment_failure_reasons(), 0.8
    
    # Contact support query
    if "contact support" in message:
        return "For any payment-related issues, please contact our support team at support@example.com.", 0.9
    
    return "Sorry, I didn't understand your payment query. Please specify your request.", 0.6


# Function to return the return policy
def get_return_policy() -> str:
    return """
• Items can be returned within 30 days of delivery
• Must be in original condition with tags attached
• Free returns on eligible items
• Refund will be processed within 5-7 business days
"""

# Enhanced product filter function using the new product list
def filter_products(message: str) -> List[Dict]:
    message = message.lower()
    filtered_products = []

    # Loop through the product list and check if the product name is in the message
    matched_product_name = None
    for product_name in product_list:
        if product_name.lower() in message:
            matched_product_name = product_name.lower()
            # Filter products by name if there's a match
            filtered_products = [p for p in products if product_name.lower() in p["name"].lower()]
            break  # If one product is matched, we break out of the loop

    # If the product is mentioned but no matching products are found, return an unavailable message
    if matched_product_name and not filtered_products:
        return f"Sorry, the {matched_product_name} is currently unavailable at the moment."

    # Filter by rating if the user asks for highly rated products
    if "highly rated" in message or "best rated" in message:
        product_mentioned = any(product.lower() in message for product in product_list)
        if not product_mentioned:
            return "Please specify a product or category for highly rated recommendations."
        
        # Filter products by rating (4.5 or higher)
        matched_product_name = None  
        for product_name in product_list:
            if product_name.lower() in message:
                matched_product_name = product_name.lower()
                # Filter products by name if there's a match
                filtered_products = [p for p in products if product_name.lower() in p["name"].lower()]
                if filtered_products:
                    filtered_products = [p for p in filtered_products if p["rating"] >= 4.5]
                    break
                else:
                    return f"Sorry, the {matched_product_name} is currently unavailable at the moment."

    return filtered_products

# Route to handle chat requests
@app.post("/chat", response_model=ChatResponse)
# Function to handle chat requests
async def chat(request: ChatRequest, user: Dict = Depends(get_current_user)):
    message = request.message.lower() # Convert message to lowercase for easier matching
    response = "" # Default response
    confidence = 0.0 # Default confidence level
    recommended_products = [] # Default recommended products list

    # Check for return, refund, order, or payment-related queries
    if any(word in message for word in ["return", "refund"]):
        response = get_return_policy()
        confidence = 0.9

    # Check for order-related queries
    elif any(word in message for word in ["order", "tracking", "status", "shipment", "delivery", "order number", "order id", ]):
        response, confidence = handle_order_query(message, user)
    
    # Check for payment-related queries
    elif any(word in message for word in ["payment", "history", "payment status", "payment failed", "payment issues", "payment details", "payment method", "payment "]):
        response, confidence = handle_payment_query(message, user)
    
    # Check for product-related queries
    elif any(word in message for word in ["recommend", "suggest", "show", "products", "items", "shop", "buy", "browse", "product", "search"]):
        filtered_products = filter_products(message)
        if isinstance(filtered_products, list):
            if filtered_products:
                response = f"Here are some products that match for you"
                recommended_products = filtered_products
                confidence = 0.9
            else:
                response = "I couldn't find any products matching your keyword. Try browsing our general collection"
                confidence = 0.7
        else:
            response = filtered_products  # This is the unavailable product message
            confidence = 0.6
    
    # Greeting response
    elif any(word in message for word in ["hello", "hi", "hey"]):
        response = """Hello! 👋 I'm your AI shopping assistant. How can I help you today? You can ask me about:
• Product recommendations (e.g., "Show me women's bags" or "Highly rated products")
• Order status
• Return policy"""
        confidence = 0.9
    
    # Thank you response
    elif any(word in message for word in ["thanks", "thank", "thank you", "appreciate", "grateful", "helpful", "nice"]):
        response = "You're welcome! If you have any more questions, feel free to ask!"
        confidence = 0.9

    # General assistance request
    elif "help" in message:
        response = "Of course! What do you need assistance with? You can ask me about products, orders, or any other inquiries you may have."
        confidence = 0.9
    # Default response for unrecognized queries
    else:
        response = "I'm not sure I understand. You can ask me to show products, check order status, or learn about our return policy."
        confidence = 0.5

    # Return the chat response
    return ChatResponse(
        response=response,
        confidence=confidence,
        products=recommended_products if recommended_products else None
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

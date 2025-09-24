import vertexai
from vertexai.preview.generative_models import GenerativeModel, Tool, FunctionDeclaration, AutomaticFunctionCallingResponder
from datetime import datetime, timezone
from urllib.parse import quote_plus
import random

# First, create functions that the model can use to answer your questions.
def get_current_weather(location: str, unit: str = "centigrade"):
    """Gets weather in the specified location.

    Args:
        location: The location for which to get the weather.
        unit: Optional. Temperature unit. Can be Centigrade or Fahrenheit. Defaults to Centigrade.
    """
    return dict(
        widget="weather",
        props=dict(
            location=location,
            unit=unit,
            summary="Super nice, but maybe a bit hot.",
        ),
    )

# Add an additional tool-enabled function to provide current time
def get_current_time(timezone_name: str = "UTC"):
    """Gets the current time in ISO 8601 format.

    Args:
        timezone_name: Optional. Name of timezone (informational only). Defaults to UTC.
    """
    now = datetime.now(timezone.utc)
    return dict(
        widget="watch",
        props=dict(
            timezone=timezone_name,
            iso_time=now.isoformat(),
        ),
    )

# Stock price widget tool
def get_stock_quote(symbol: str, currency: str = "USD"):
    """Gets a mock stock quote for the given symbol.

    Args:
        symbol: Stock ticker symbol, e.g., AAPL, GOOGL
        currency: Optional. Currency code. Defaults to USD.
    """
    price = round(random.uniform(10, 1000), 2)
    as_of = datetime.now(timezone.utc).isoformat()
    return dict(
        widget="stock",
        props=dict(
            symbol=symbol.upper(),
            price=price,
            currency=currency,
            as_of=as_of,
        ),
    )

# Photo widget tool
def get_photo(query: str):
    """Returns a representative image URL for the given query.

    Args:
        query: Subject to search for a photo.
    """
    seed = quote_plus(query.strip()) or "default"
    url = f"https://picsum.photos/seed/{seed}/600/400"
    return dict(
        widget="photo",
        props=dict(
            query=query,
            url=url,
        ),
    )

# Infer function schema
get_current_weather_func = FunctionDeclaration.from_func(get_current_weather)

# Time tool
get_current_time_func = FunctionDeclaration.from_func(get_current_time)

get_stock_quote_func = FunctionDeclaration.from_func(get_stock_quote)

get_photo_func = FunctionDeclaration.from_func(get_photo)

# Consolidate all functions into a single Tool (Vertex AI requires this unless all are search tools)
widget_tool = Tool(
    function_declarations=[
        get_current_weather_func,
        get_current_time_func,
        get_stock_quote_func,
        get_photo_func,
    ],
)

# Use tools in chat:
vertexai.init(project='genai-472800', location='us-central1')
model = GenerativeModel(
    "gemini-2.5-flash",
    # You can specify tools when creating a model to avoid having to send them with every request.
    tools=[widget_tool],
)

# Activate automatic function calling:
afc_responder = AutomaticFunctionCallingResponder(
    # Optional:
    max_automatic_function_calls=5,
)
chat = model.start_chat(responder=afc_responder)

# Send a message to the model. The model will choose an appropriate tool and
# respond ONLY with a JSON widget payload: {"widget": <type>, "props": {...}}
# user_query = "Show me AAPL stock price"
# instruction = (
#     "You are a widget router. Based on the user's message, select exactly one widget "
#     "to display and call the appropriate tool. Always respond ONLY with a compact JSON "
#     "object using keys 'widget' and 'props'. No prose."
# )
# print(chat.send_message(f"{instruction}\nUser: {user_query}"))

# user_query = "What is the weather like in Boston?"
# instruction = (
#     "You are a widget router. Based on the user's message, select exactly one widget "
#     "to display and call the appropriate tool. Always respond ONLY with a compact JSON "
#     "object using keys 'widget' and 'props'. No prose."
# )
# print(chat.send_message(f"{instruction}\nUser: {user_query}"))

user_query = "Show me a photo of a sunset over the mountains."
instruction = (
    "You are a widget router. Based on the user's message, select exactly one widget "
    "to display and call the appropriate tool. Always respond ONLY with a compact JSON "
    "object using keys 'widget' and 'props'. No prose."
)
print(chat.send_message(f"{instruction}\nUser: {user_query}"))
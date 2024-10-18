from utils.tools.googleCalender import CreateGoogleCalendarEvent
from utils.tools.indetity import identity
from utils.tools.mailvalidation import validate_email
from langchain_community.tools.gmail.utils import (
    build_resource_service,
    get_gmail_credentials,
)
from langchain_core.output_parsers import JsonOutputParser
from utils.functions import create_agent
from utils.model import (
    ColorTrendVariables,
    ComparisonVariables,
    GetEventsSchema,
    PrechatVariables
)
from langchain_openai import ChatOpenAI
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
)
from utils.prompt import (
    COMPARISON_PROMPT,
    COLOR_TREND_PROMPT,
    GREETING_PROMPT,
    PRECHAT_PROMPT,
    FEEDBACK_PROMPT,
    SCHEDULER_PROMPT,
    FALLBACK_PROMPT,
)


credentials = get_gmail_credentials(
    token_file="token.json",
    scopes=["https://www.googleapis.com/auth/calendar"],
    client_secrets_file="credentials.json",
)

calendar_service = build_resource_service(
    credentials=credentials, service_name="calendar", service_version="v3"
)

createeventtool = CreateGoogleCalendarEvent.from_api_resource(calendar_service)

llm = ChatOpenAI(temperature=0)




comparison_parser = JsonOutputParser(pydantic_object=ComparisonVariables)

comparison_prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            COMPARISON_PROMPT,
        ),
        MessagesPlaceholder(variable_name="messages"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
).partial(format_instructions=comparison_parser.get_format_instructions())

comparison = create_agent(
    llm=llm, tools=[identity], system_prompt=comparison_prompt_template
)


coolortrend_parser = JsonOutputParser(pydantic_object=ColorTrendVariables)

trend_prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            COLOR_TREND_PROMPT,
        ),
        MessagesPlaceholder(variable_name="messages"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
).partial(format_instructions=coolortrend_parser.get_format_instructions())

colortrend = create_agent(llm, [identity], trend_prompt_template)


greet_prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            GREETING_PROMPT,
        ),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)
greet_agent = create_agent(llm, [identity], greet_prompt_template)


prechat_parser = JsonOutputParser(pydantic_object=PrechatVariables)


prechat_prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            PRECHAT_PROMPT,
        ),
        MessagesPlaceholder(variable_name="messages"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
).partial(format_instructions=prechat_parser.get_format_instructions())

prechat_agent = create_agent(llm, [validate_email, identity], prechat_prompt_template)


feedback_prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            FEEDBACK_PROMPT,
        ),
        MessagesPlaceholder(variable_name="messages"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)
feedback_agent = create_agent(llm, [identity], feedback_prompt_template)


scheduler_parser = JsonOutputParser(pydantic_object=GetEventsSchema)

scheduler_prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            SCHEDULER_PROMPT,
        ),
        MessagesPlaceholder(variable_name="messages"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ],
).partial(
    format_instructions=scheduler_parser.get_format_instructions(),
)

scheduler_agent = create_agent(
    llm=llm,
    tools=[createeventtool, validate_email, identity],
    system_prompt=scheduler_prompt_template,
)


fallback_prompt_template = ChatPromptTemplate.from_messages(
[
    (
        "system",
        FALLBACK_PROMPT,
        
    ),
    # MessagesPlaceholder(variable_name="messages"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
],
)

fallback_agent = create_agent(
    llm=llm,
    tools=[identity],
    system_prompt=fallback_prompt_template,
)

# Customer Support Example

A simple example of building a customer support system using LangGraph Swarm. This example demonstrates how to create a system where agents can hand off conversations to other specialized agents.

## Overview

The system consists of two specialized agents:
- **Flight Assistant**: Handles flight search and booking
- **Hotel Assistant**: Handles hotel search and booking

These agents can transfer control to each other using handoff tools, allowing for a seamless customer experience.

## Quickstart

```bash
uvx --refresh --from "langgraph-cli[inmem]" --with-editable . --python 3.11 langgraph dev
```

## Features

- Agent handoff between specialized services
- Mock data for flights and hotels
- Reservation tracking by user ID
- Built with LangGraph Swarm for agent orchestration

## How It Works

1. The system starts with the Flight Assistant as the default agent
2. Agents can pass control using handoff tools (`transfer_to_hotel_assistant` and `transfer_to_flight_assistant`)
3. User context and reservation information is maintained throughout handoffs
4. Agents have access to specific tools related to their domain





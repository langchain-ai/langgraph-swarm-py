# 🏢 Master Services Panama S.A. - Company Simulation

An AI-powered multi-agent simulation system for Master Services Panama S.A., built using LangGraph Swarm. This system simulates different departments of your company to help you make informed decisions about projects, pricing, staffing, and strategy.

## 🎯 Overview

This simulation uses multiple AI agents that represent different departments and functions within Master Services:

- **🏦 Finance Agent** - Financial analysis, cost calculations, and profitability assessment
- **🔧 Operations Manager** - Project management, resource allocation, and scheduling
- **👥 HR Agent** - Employee information, skills management, and staffing
- **📊 Strategy Agent** - Competitive analysis, market positioning, and strategic planning
- **💼 Sales/Bidding Agent** - Project quotes, pricing, and proposal generation

Each agent has access to your complete company data including:
- All 17 employees with their salaries, skills, and experience
- Financial metrics and operating costs
- Service pricing for all service types
- Competitor information
- Recent major projects
- Strategic focus areas

## 🚀 Quick Start

### Prerequisites

1. Python 3.10 or higher
2. OpenAI API key (or other LLM provider)

### Installation

```bash
# Navigate to the project root
cd langgraph-swarm-py

# Install dependencies
pip install -e .
pip install langchain-openai

# Set your API key
export OPENAI_API_KEY='your-key-here'
```

### Run the Simulation

**Interactive Mode** (recommended):
```bash
python examples/master_services/run_simulation.py
```

**Example Scenarios**:
```bash
python examples/master_services/run_simulation.py --examples
```

## 💡 What Can You Do?

### 1. Get Company Information

```
"Give me a company overview"
"What are our recent major projects?"
"What is our strategic focus?"
```

### 2. Employee & HR Queries

```
"Show me all employees in the Maintenance department"
"Who can do tank installation?"
"List employees with electrical work skills"
"How many technicians do we have available?"
```

### 3. Financial Analysis & Pricing

```
"What are our hourly rates for different services?"
"Calculate our monthly operating costs"
"Calculate a quote for 100 hours of station maintenance"
"Quote: Tank installation, 80 hours, $10,000 materials"
```

### 4. Strategic Decision Making

```
"Should we bid on a $15,000 local maintenance project?"
"Analyze this project: Tank installation, 80 hours, $10k materials, Colon, Delta Petroleum"
"How do we compare to Rodrigo Blanco?"
"What types of projects should we focus on?"
```

### 5. Project Management

```
"Who should work on a major electrical project?"
"Find employees for a tank installation in David"
"What projects have we completed recently?"
```

## 📊 Company Data Included

The simulation includes complete data about Master Services:

### Personnel (17 Employees)
- **Maintenance Department**: 8 technicians ($6,318.27/month)
- **Operations Department**: 4 technicians ($3,427.22/month)
- **Administration**: 4 employees ($4,028.37/month)
- **Mechanics**: 1 technician ($782.50/month)

### Financial Metrics
- Monthly Salaries: $14,556.36
- Monthly Payroll (with benefits): $19,461.85
- Total Operating Cost: $25,544.67
- Hourly Cost (no profit): $145.14
- Target Hourly Rate (25% margin): $181.43

### Services Offered
- Station Construction
- Station Maintenance
- Equipment Installation
- Tank Installation
- Leak Testing
- Electrical Work
- Emergency Service (24/7)
- Calibration

### Major Clients
- Delta Petroleum (99% effectiveness)
- Texaco
- Terpel
- Puma Energy
- US Navy
- Panama Canal Commission
- Government of Panama

## 🧠 How It Works

The system uses **LangGraph Swarm** architecture where multiple specialized AI agents collaborate:

1. **You ask a question** - The system analyzes what type of query it is
2. **Agent selection** - Routes to the most appropriate department agent
3. **Agent processing** - The agent uses company data and tools to answer
4. **Agent handoff** - If needed, transfers to another agent with relevant expertise
5. **Response** - You get a comprehensive answer based on real company data

### Example Flow

```
User: "Should we bid on a $50,000 station construction project in Colon?"
  ↓
Strategy Agent analyzes the request
  ↓
Calls Sales Agent to calculate the quote
  ↓
Sales Agent calculates pricing and profitability
  ↓
Strategy Agent evaluates strategic fit
  ↓
Response: Detailed analysis with recommendation
```

## 🎓 Use Cases

### 1. Project Bidding Decisions
Quickly analyze whether a project is worth bidding on based on:
- Profitability (minimum 25% margin target)
- Strategic fit with company focus
- Location (national coverage advantage)
- Client relationship
- Competition from local providers

### 2. Resource Planning
- Find available employees with specific skills
- Estimate labor costs for projects
- Plan staffing for multiple concurrent projects

### 3. Pricing Strategy
- Generate accurate quotes instantly
- Understand cost breakdown
- Compare pricing across service types
- Analyze profit margins

### 4. Competitive Analysis
- Compare rates with competitors
- Understand competitive advantages
- Identify market positioning opportunities

### 5. Strategic Planning
- Evaluate alignment with 2024 strategic focus
- Assess project viability
- Make data-driven business decisions

## 📁 Project Structure

```
examples/master_services/
├── README.md                          # This file
├── run_simulation.py                  # Interactive runner script
└── src/
    ├── data/
    │   ├── __init__.py
    │   └── company_data.py            # All company data and models
    └── agents/
        ├── __init__.py
        └── company_simulation.py      # Agent definitions and swarm
```

## 🔧 Customization

### Changing the LLM

Edit `src/agents/company_simulation.py`:

```python
# Current (OpenAI GPT-4o-mini)
model = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# Change to GPT-4
model = ChatOpenAI(model="gpt-4", temperature=0.7)

# Or use Anthropic Claude
from langchain_anthropic import ChatAnthropic
model = ChatAnthropic(model="claude-3-sonnet-20240229")
```

### Updating Company Data

Edit `src/data/company_data.py` to update:
- Employee information and salaries
- Service pricing
- Financial metrics
- Client list
- Strategic focus

### Adding New Agents

You can add new specialized agents (e.g., Safety Compliance, Quality Control):

```python
safety_agent = create_react_agent(
    model,
    [your_tools_here],
    prompt="You are the Safety Compliance Agent...",
    name="safety_agent",
)

# Add to swarm
workflow = create_swarm(
    [finance_agent, operations_agent, hr_agent, strategy_agent, sales_agent, safety_agent],
    default_active_agent="strategy_agent",
)
```

## 📈 Advanced Features

### 1. Project Viability Analysis

The `analyze_project_viability` tool provides comprehensive scoring based on:
- Profit margin (≥25% target)
- Service type (specialized vs routine)
- Location (national coverage advantage)
- Client relationship (major clients preferred)
- Project size (large projects justify overhead)

### 2. Cost Calculation

Accurate cost breakdowns including:
- Labor hours and rates
- Materials cost with markup
- Internal costs vs quoted price
- Profit margin analysis

### 3. Skills Matching

Find the right employees for any project based on:
- Required technical skills
- Years of experience
- Department and availability
- Current workload

## 🤝 Integration

This simulation can be integrated into other systems:

```python
from examples.master_services.src.agents import app

# Use in your application
config = {"configurable": {"thread_id": "your_session_id"}}
response = app.invoke(
    {"messages": [{"role": "user", "content": "Your question here"}]},
    config
)

answer = response["messages"][-1].content
```

## 📝 Notes

- **Data Privacy**: All company data is local; only queries are sent to the LLM
- **Accuracy**: Responses are based on the data provided in `company_data.py`
- **Updates**: Keep employee and pricing data current for best results
- **Costs**: Uses OpenAI API (GPT-4o-mini is cost-effective)

## 🎯 Strategic Benefits

This simulation helps Master Services:

1. **Make faster decisions** - Get instant analysis instead of manual calculations
2. **Avoid unprofitable projects** - Automated viability scoring
3. **Optimize resource allocation** - Quickly match skills to projects
4. **Compete strategically** - Focus on high-value work that justifies premium pricing
5. **Improve consistency** - Standardized analysis across all decisions
6. **Preserve expertise** - Capture institutional knowledge in AI agents

## 🔮 Future Enhancements

Potential additions:
- [ ] Project tracking database
- [ ] Historical data analysis
- [ ] Predictive scheduling
- [ ] Automated proposal generation
- [ ] Integration with accounting systems
- [ ] Mobile interface
- [ ] Voice interaction
- [ ] Multi-language support (Spanish)

## 📞 Support

For questions or issues:
- Email: operaciones@masterservices.org
- Company: Master Services Panama S.A.
- Founded: 1978 (47 years of excellence)

---

**Built with ❤️ using LangGraph Swarm**

*Transforming 47 years of expertise into AI-powered decision making*

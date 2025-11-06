# 🚀 Master Services Simulation - Quick Start

Get started with the company simulation in 5 minutes!

## Step 1: Install Dependencies

```bash
# From the project root directory
cd langgraph-swarm-py

# Install the package
pip install -e .

# Install OpenAI (or your preferred LLM)
pip install langchain-openai
```

## Step 2: Set Your API Key

```bash
# For OpenAI
export OPENAI_API_KEY='your-api-key-here'

# Or add to your .bashrc / .zshrc
echo 'export OPENAI_API_KEY="your-api-key-here"' >> ~/.bashrc
```

Get your API key from: https://platform.openai.com/api-keys

## Step 3: Run the Simulation

```bash
# Interactive mode
python examples/master_services/run_simulation.py

# Or run example scenarios
python examples/master_services/run_simulation.py --examples
```

## Step 4: Try These Questions

Once the simulation is running, try:

### Basic Information
```
Give me a company overview
Show me all employees
What are our major clients?
```

### Employee Skills
```
Who can do tank installation?
List all maintenance technicians
Show employees with electrical skills
```

### Project Pricing
```
Calculate a quote for 100 hours of maintenance work
Quote: Station Construction, 500 hours, $30,000 materials
What are our service rates?
```

### Strategic Decisions
```
Should we bid on a $20,000 local maintenance project?

Analyze this project:
Service: Tank Installation
Hours: 80
Materials: $10,000
Location: Colon (interior)
Client: Delta Petroleum
```

## Understanding Responses

The system will:
1. Route your question to the right department agent
2. Use real company data to answer
3. Provide detailed analysis and recommendations
4. Transfer between agents if needed for complete answers

## Customization

To update company data, edit:
```
examples/master_services/src/data/company_data.py
```

You can update:
- Employee information
- Salaries and costs
- Service pricing
- Client information
- Strategic focus

## Troubleshooting

**"OPENAI_API_KEY not set"**
- Make sure you've exported the environment variable
- Check: `echo $OPENAI_API_KEY`

**Import errors**
- Install the package: `pip install -e .`
- Install langchain-openai: `pip install langchain-openai`

**Slow responses**
- Using GPT-4o-mini by default (fast and cheap)
- Can upgrade to GPT-4 for better quality (edit `company_simulation.py`)

## What's Next?

1. Read the full [README.md](README.md) for detailed documentation
2. Explore the agents in `src/agents/company_simulation.py`
3. Customize the company data in `src/data/company_data.py`
4. Try different scenarios relevant to your business

## Key Features

✅ **5 Specialized Agents**: Finance, Operations, HR, Strategy, Sales
✅ **Complete Company Data**: All 17 employees, pricing, costs
✅ **Project Analysis**: Automatic viability scoring
✅ **Instant Quotes**: Calculate project pricing in seconds
✅ **Skills Matching**: Find the right people for any job
✅ **Strategic Insights**: Data-driven recommendations

---

**Questions?** Check the [README.md](README.md) or contact operaciones@masterservices.org

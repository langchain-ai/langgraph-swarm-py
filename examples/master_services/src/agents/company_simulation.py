"""Master Services Company Simulation - Multi-Agent System.

This module implements a multi-agent swarm that simulates Master Services Panama S.A.
Each agent represents a different department or function within the company.
"""

import json
from typing import Annotated, Any, Dict, List

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from langgraph_swarm import create_handoff_tool, create_swarm

from ..data import (
    COMPANY_INFO,
    COMPETITORS,
    EMPLOYEES,
    FINANCIAL_DATA,
    MAJOR_CLIENTS,
    RECENT_PROJECTS,
    SERVICE_PRICING,
    STRATEGIC_FOCUS,
    Department,
    ServiceType,
    calculate_project_cost,
    find_employees_with_skill,
    get_company_summary,
    get_department_employees,
    get_total_department_salary,
)

# Initialize the language model
# You can change this to any other model you prefer
model = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# ============================================================================
# TOOLS - Shared across agents
# ============================================================================


@tool
def view_company_info() -> str:
    """Get complete overview of Master Services company information, financials, and structure."""
    return get_company_summary()


@tool
def get_employee_list(department: str | None = None) -> str:
    """Get list of employees, optionally filtered by department.

    Args:
        department: Optional department filter (Maintenance, Operations, Administration, Mechanics)
    """
    if department:
        try:
            dept = Department(department)
            employees = get_department_employees(dept)
            dept_salary = get_total_department_salary(dept)
            result = f"\n{department} Department:\n"
            result += f"Total Monthly Salary: ${dept_salary:,.2f}\n\n"
        except ValueError:
            return f"Invalid department. Valid options: {', '.join(d.value for d in Department)}"
    else:
        employees = list(EMPLOYEES.values())
        result = "\nAll Employees:\n"

    for emp in employees:
        result += f"\n{emp.name}:"
        result += f"\n  Salary: ${emp.monthly_salary:,.2f}/month"
        result += f"\n  Experience: {emp.years_experience} years"
        result += f"\n  Skills: {', '.join(emp.skills)}"

    return result


@tool
def search_employees_by_skill(skill: str) -> str:
    """Find all employees who have a specific skill.

    Args:
        skill: Skill to search for (e.g., 'Tank Installation', 'Electrical Work', 'Maintenance')
    """
    employees = find_employees_with_skill(skill)
    if not employees:
        return f"No employees found with skill: {skill}"

    result = f"\nEmployees with '{skill}' skill:\n"
    for emp in employees:
        result += f"\n{emp.name} ({emp.department.value}):"
        result += f"\n  Experience: {emp.years_experience} years"
        result += f"\n  Salary: ${emp.monthly_salary:,.2f}/month"
        result += f"\n  All skills: {', '.join(emp.skills)}"

    return result


@tool
def calculate_project_quote(
    service_type: str,
    estimated_hours: float,
    materials_cost: float = 0,
) -> str:
    """Calculate pricing quote for a project.

    Args:
        service_type: Type of service (Station Construction, Station Maintenance, Equipment Installation, etc.)
        estimated_hours: Estimated labor hours needed
        materials_cost: Estimated cost of materials before markup
    """
    try:
        svc_type = ServiceType(service_type)
    except ValueError:
        return f"Invalid service type. Valid options:\n" + "\n".join(f"  - {s.value}" for s in ServiceType)

    breakdown = calculate_project_cost(svc_type, estimated_hours, materials_cost)

    result = f"\nPROJECT QUOTE - {service_type}\n"
    result += "=" * 60 + "\n"
    result += f"\nLABOR:"
    result += f"\n  Hours: {breakdown['labor_hours']:.1f}"
    result += f"\n  Rate: ${breakdown['labor_rate']:.2f}/hour"
    result += f"\n  Labor Total: ${breakdown['labor_price']:,.2f}"

    if materials_cost > 0:
        result += f"\n\nMATERIALS:"
        result += f"\n  Cost: ${breakdown['materials_cost']:,.2f}"
        result += f"\n  Markup: {(breakdown['materials_markup'] - 1) * 100:.0f}%"
        result += f"\n  Materials Total: ${breakdown['materials_price']:,.2f}"

    result += f"\n\nTOTAL QUOTE: ${breakdown['total_price']:,.2f}"
    result += f"\n\nPROFITABILITY ANALYSIS:"
    result += f"\n  Internal Cost: ${breakdown['internal_cost']:,.2f}"
    result += f"\n  Estimated Profit: ${breakdown['estimated_profit']:,.2f}"
    result += f"\n  Profit Margin: {breakdown['profit_margin_percent']:.1f}%"

    return result


@tool
def get_service_pricing_info(service_type: str | None = None) -> str:
    """Get pricing information for services offered.

    Args:
        service_type: Optional specific service type to get details for
    """
    if service_type:
        try:
            svc_type = ServiceType(service_type)
            pricing = SERVICE_PRICING[svc_type]
            result = f"\n{service_type} Pricing:\n"
            result += f"  Hourly Rate: ${pricing['hourly_rate']:.2f}"
            result += f"\n  Typical Hours: {pricing['typical_hours']}"
            result += f"\n  Materials Markup: {(pricing['materials_markup'] - 1) * 100:.0f}%"
            result += f"\n  Typical Project Value: ${pricing['hourly_rate'] * pricing['typical_hours']:,.2f}"
            return result
        except (ValueError, KeyError):
            return f"Invalid service type. Valid options:\n" + "\n".join(f"  - {s.value}" for s in ServiceType)

    result = "\nMaster Services - Service Pricing:\n"
    result += "=" * 60 + "\n"
    for svc_type, pricing in SERVICE_PRICING.items():
        result += f"\n{svc_type.value}:"
        result += f"\n  Rate: ${pricing['hourly_rate']:.2f}/hour"
        result += f"\n  Typical: {pricing['typical_hours']} hours"
        result += f"\n  Avg Value: ${pricing['hourly_rate'] * pricing['typical_hours']:,.2f}\n"

    return result


@tool
def view_competitors_info() -> str:
    """Get information about competitors and competitive landscape."""
    result = "\nCOMPETITOR ANALYSIS:\n"
    result += "=" * 60 + "\n"

    for name, info in COMPETITORS.items():
        result += f"\n{name}:"
        result += f"\n  Relationship: {info['relationship']}"
        result += f"\n  Hourly Rate (est.): ${info['estimated_hourly_rate']:.2f}"
        result += f"\n  Strengths: {', '.join(info['strengths'])}"
        result += f"\n  Weaknesses: {', '.join(info['weaknesses'])}"

    result += f"\n\nOur Rate: ${FINANCIAL_DATA['hourly_rate_25percent_margin']:.2f}/hour"
    result += f"\nPrice Difference: {((FINANCIAL_DATA['hourly_rate_25percent_margin'] / COMPETITORS['Rodrigo Blanco']['estimated_hourly_rate']) - 1) * 100:.1f}% higher"

    return result


@tool
def view_strategic_focus() -> str:
    """Get current strategic focus and business priorities."""
    result = "\nSTRATEGIC FOCUS (2024 onwards):\n"
    result += "=" * 60 + "\n"

    for i, focus in enumerate(STRATEGIC_FOCUS, 1):
        result += f"\n{i}. {focus}"

    result += "\n\nRATIONALE:"
    result += "\n- Our costs are higher due to experienced staff, certifications, and national coverage"
    result += "\n- Local competitors (like Rodrigo Blanco) can handle routine maintenance cheaper"
    result += "\n- We should focus on high-value, specialized projects that justify our premium pricing"
    result += "\n- Interior/national projects leverage our unique coverage advantage"

    return result


@tool
def view_recent_projects() -> str:
    """View information about recent major projects completed."""
    result = "\nRECENT MAJOR PROJECTS:\n"
    result += "=" * 60 + "\n"

    for project in RECENT_PROJECTS:
        result += f"\n{project['name']}:"
        result += f"\n  Type: {project['type']}"
        result += f"\n  Scope:"
        for scope_item in project['scope']:
            result += f"\n    - {scope_item}"
        result += "\n"

    return result


@tool
def analyze_project_viability(
    service_type: str,
    estimated_hours: float,
    materials_cost: float,
    location: str,
    client_type: str,
) -> str:
    """Analyze whether we should bid on a project based on strategic fit and profitability.

    Args:
        service_type: Type of service requested
        estimated_hours: Estimated hours needed
        materials_cost: Estimated materials cost
        location: Project location (Panama City, Interior, etc.)
        client_type: Type of client (major petroleum company, small station, government, etc.)
    """
    try:
        svc_type = ServiceType(service_type)
    except ValueError:
        return "Invalid service type specified."

    breakdown = calculate_project_cost(svc_type, estimated_hours, materials_cost)

    result = "\nPROJECT VIABILITY ANALYSIS:\n"
    result += "=" * 60 + "\n"

    result += f"\nProject Details:"
    result += f"\n  Service: {service_type}"
    result += f"\n  Location: {location}"
    result += f"\n  Client: {client_type}"
    result += f"\n  Estimated Value: ${breakdown['total_price']:,.2f}"
    result += f"\n  Profit Margin: {breakdown['profit_margin_percent']:.1f}%"

    # Strategic Assessment
    result += "\n\nStrategic Fit Assessment:"

    score = 0
    max_score = 5

    # Factor 1: Profit margin
    if breakdown['profit_margin_percent'] >= 25:
        result += "\n  ✓ Profit margin meets 25% target"
        score += 1
    else:
        result += f"\n  ✗ Profit margin below 25% target ({breakdown['profit_margin_percent']:.1f}%)"

    # Factor 2: Project type
    specialized_types = [
        ServiceType.STATION_CONSTRUCTION,
        ServiceType.TANK_INSTALLATION,
        ServiceType.EQUIPMENT_INSTALLATION,
    ]
    if svc_type in specialized_types:
        result += "\n  ✓ Specialized/high-value service type"
        score += 1
    else:
        result += "\n  ✗ Routine maintenance - consider delegating to lower-cost providers"

    # Factor 3: Location
    if location.lower() not in ["panama city", "local"]:
        result += "\n  ✓ Interior location leverages our national coverage advantage"
        score += 1
    else:
        result += "\n  ✗ Local work - vulnerable to competition from lower-cost providers"

    # Factor 4: Client type
    if any(
        major_client.lower() in client_type.lower() for major_client in MAJOR_CLIENTS
    ):
        result += "\n  ✓ Major client relationship"
        score += 1
    else:
        result += "\n  - New or small client"

    # Factor 5: Project size
    if breakdown['total_price'] >= 20000:
        result += "\n  ✓ Large project value justifies our overhead"
        score += 1
    else:
        result += "\n  - Small project value"

    # Recommendation
    result += f"\n\nStrategic Score: {score}/{max_score}"
    result += "\n\nRECOMMENDATION: "

    if score >= 4:
        result += "STRONGLY RECOMMEND - Excellent strategic fit"
    elif score >= 3:
        result += "RECOMMEND - Good fit for our capabilities"
    elif score >= 2:
        result += "CONSIDER - Marginal fit, evaluate carefully"
    else:
        result += "DO NOT PURSUE - Poor strategic fit, consider referring to local providers"

    return result


# ============================================================================
# AGENT DEFINITIONS
# ============================================================================

# Define handoff tools
transfer_to_finance = create_handoff_tool(
    agent_name="finance_agent",
    description="Transfer to Finance Agent for financial analysis, cost calculations, and profitability questions",
)

transfer_to_operations = create_handoff_tool(
    agent_name="operations_agent",
    description="Transfer to Operations Manager for project management, resource allocation, and scheduling",
)

transfer_to_hr = create_handoff_tool(
    agent_name="hr_agent",
    description="Transfer to HR Agent for employee information, skills, availability, and staffing questions",
)

transfer_to_strategy = create_handoff_tool(
    agent_name="strategy_agent",
    description="Transfer to Strategic Planning Agent for competitive analysis, market positioning, and strategic decisions",
)

transfer_to_sales = create_handoff_tool(
    agent_name="sales_agent",
    description="Transfer to Sales/Bidding Agent for project quotes, pricing, and proposal generation",
)

# Finance Agent
finance_agent = create_react_agent(
    model,
    [
        view_company_info,
        calculate_project_quote,
        get_service_pricing_info,
        transfer_to_operations,
        transfer_to_hr,
        transfer_to_strategy,
        transfer_to_sales,
    ],
    prompt="""You are the Finance Agent for Master Services Panama S.A.

Your responsibilities:
- Analyze financial metrics and profitability
- Calculate project costs and pricing
- Track company expenses and revenue
- Provide financial insights and recommendations
- Ensure projects meet profit margin targets (25% minimum)

Key Financial Facts:
- Monthly operating cost: $25,544.67
- Hourly cost (no profit): $145.14
- Target hourly rate (25% margin): $181.43
- Total employees: 17
- Monthly payroll: $19,461.85 (including benefits)

Always consider profitability and financial sustainability in your recommendations.
Transfer to other agents when their expertise is needed.""",
    name="finance_agent",
)

# Operations Manager Agent
operations_agent = create_react_agent(
    model,
    [
        view_company_info,
        search_employees_by_skill,
        view_recent_projects,
        transfer_to_finance,
        transfer_to_hr,
        transfer_to_strategy,
        transfer_to_sales,
    ],
    prompt="""You are the Operations Manager for Master Services Panama S.A.

Your responsibilities:
- Manage project execution and scheduling
- Allocate resources and assign technicians
- Coordinate between departments (Maintenance, Operations, Mechanics)
- Ensure projects are staffed with qualified personnel
- Track project progress and completion

Key Resources:
- Maintenance: 8 technicians
- Operations: 4 technicians
- Mechanics: 1 technician
- Fleet: 8 equipped vehicles

Focus on operational efficiency and quality service delivery.
Transfer to other agents when their expertise is needed.""",
    name="operations_agent",
)

# HR Agent
hr_agent = create_react_agent(
    model,
    [
        get_employee_list,
        search_employees_by_skill,
        view_company_info,
        transfer_to_finance,
        transfer_to_operations,
        transfer_to_strategy,
        transfer_to_sales,
    ],
    prompt="""You are the HR Agent for Master Services Panama S.A.

Your responsibilities:
- Manage employee information and records
- Track skills and certifications
- Assess staffing needs and availability
- Provide insights on workforce capabilities
- Support resource allocation decisions

Company has 17 employees across 4 departments:
- Maintenance: 8 technicians
- Operations: 4 technicians
- Administration: 4 employees
- Mechanics: 1 technician

Many employees have 10-20+ years of experience. Focus on leveraging this expertise.
Transfer to other agents when their expertise is needed.""",
    name="hr_agent",
)

# Strategic Planning Agent
strategy_agent = create_react_agent(
    model,
    [
        view_strategic_focus,
        view_competitors_info,
        analyze_project_viability,
        view_company_info,
        transfer_to_finance,
        transfer_to_operations,
        transfer_to_hr,
        transfer_to_sales,
    ],
    prompt="""You are the Strategic Planning Agent for Master Services Panama S.A.

Your responsibilities:
- Analyze competitive landscape
- Evaluate project strategic fit
- Provide recommendations on which projects to pursue
- Guide long-term business direction
- Consider company strengths and market positioning

Key Strategic Points:
- 47 years of experience (founded 1978)
- Higher costs than local competitors but superior capabilities
- Strategic focus: specialized projects, national coverage, high-value work
- Main competitor (Rodrigo Blanco): ex-employee, lower rates, local focus only

Current Strategy (2024+):
- Focus on construction and specialized technical services
- Leverage national coverage advantage
- Delegate routine local maintenance to lower-cost providers
- Target high-value projects that justify premium pricing

Provide strategic insights and viability assessments.
Transfer to other agents when their expertise is needed.""",
    name="strategy_agent",
)

# Sales/Bidding Agent
sales_agent = create_react_agent(
    model,
    [
        calculate_project_quote,
        get_service_pricing_info,
        analyze_project_viability,
        search_employees_by_skill,
        transfer_to_finance,
        transfer_to_operations,
        transfer_to_hr,
        transfer_to_strategy,
    ],
    prompt="""You are the Sales and Bidding Agent for Master Services Panama S.A.

Your responsibilities:
- Generate project quotes and proposals
- Analyze project requirements and pricing
- Assess project viability and strategic fit
- Communicate value proposition to clients
- Ensure quotes are competitive yet profitable

Service Types Offered:
- Station Construction (complete turnkey projects)
- Station Maintenance (preventive and corrective)
- Equipment Installation (tanks, dispensers, monitoring systems)
- Tank Installation (above and below ground)
- Leak Testing and Safety Systems
- Electrical Work and Cabling
- Emergency Services (24/7)
- Calibration Services

Key Differentiators:
- 47 years of experience
- National coverage (entire Panama)
- Highly experienced certified technicians
- Complete insurance and legal compliance
- 24/7 emergency service
- Major clients: Delta Petroleum, Texaco, Terpel, US Navy

When providing quotes, emphasize value and expertise, not just price.
Transfer to other agents when their expertise is needed.""",
    name="sales_agent",
)

# ============================================================================
# CREATE THE SWARM
# ============================================================================


def create_master_services_simulation():
    """Create the Master Services company simulation swarm.

    Returns:
        Compiled multi-agent swarm application ready to use
    """
    # Create the swarm with all agents
    workflow = create_swarm(
        [
            finance_agent,
            operations_agent,
            hr_agent,
            strategy_agent,
            sales_agent,
        ],
        default_active_agent="strategy_agent",  # Start with strategy agent
    )

    # Compile with memory checkpointer
    checkpointer = InMemorySaver()
    app = workflow.compile(checkpointer=checkpointer)

    return app


# Create the app instance
app = create_master_services_simulation()

if __name__ == "__main__":
    # Example usage
    config = {"configurable": {"thread_id": "1"}}

    print("\n" + "=" * 80)
    print("MASTER SERVICES PANAMA S.A. - COMPANY SIMULATION")
    print("=" * 80)
    print("\nWelcome to the Master Services multi-agent simulation!")
    print("\nAvailable agents:")
    print("  - Finance Agent: Financial analysis and cost calculations")
    print("  - Operations Manager: Project management and resource allocation")
    print("  - HR Agent: Employee information and skills management")
    print("  - Strategy Agent: Competitive analysis and strategic planning")
    print("  - Sales/Bidding Agent: Quotes, pricing, and proposals")
    print("\nTry asking questions like:")
    print('  - "Give me a company overview"')
    print('  - "Calculate a quote for 100 hours of station maintenance work"')
    print('  - "Who can do tank installation?"')
    print('  - "Should we bid on a $15,000 local maintenance project?"')
    print('  - "What is our strategic focus?"')
    print("\n" + "=" * 80 + "\n")

    # Example interaction
    response = app.invoke(
        {
            "messages": [
                {"role": "user", "content": "Give me a company overview"}
            ]
        },
        config,
    )

    print("Response:")
    print(response["messages"][-1].content)

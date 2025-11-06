"""Master Services Panama S.A. - Company Data Models and Database.

This module contains all the company data including employees, services,
pricing, and operational metrics for Master Services.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


class Department(str, Enum):
    """Company departments."""

    MAINTENANCE = "Maintenance"
    OPERATIONS = "Operations"
    ADMINISTRATION = "Administration"
    MECHANICS = "Mechanics"


class ServiceType(str, Enum):
    """Types of services offered."""

    STATION_CONSTRUCTION = "Station Construction"
    STATION_MAINTENANCE = "Station Maintenance"
    EQUIPMENT_INSTALLATION = "Equipment Installation"
    TANK_INSTALLATION = "Tank Installation"
    LEAK_TESTING = "Leak Testing"
    ELECTRICAL_WORK = "Electrical Work"
    EMERGENCY_SERVICE = "Emergency Service"
    CALIBRATION = "Calibration"


class ProjectStatus(str, Enum):
    """Project status."""

    PROPOSED = "Proposed"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


@dataclass
class Employee:
    """Employee data."""

    name: str
    department: Department
    monthly_salary: float
    skills: List[str]
    years_experience: int
    active: bool = True


@dataclass
class Project:
    """Project information."""

    project_id: str
    name: str
    client: str
    service_type: ServiceType
    status: ProjectStatus
    estimated_hours: float
    actual_hours: Optional[float] = None
    quoted_price: Optional[float] = None
    actual_cost: Optional[float] = None
    assigned_employees: List[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    notes: str = ""

    def __post_init__(self):
        if self.assigned_employees is None:
            self.assigned_employees = []


# ============================================================================
# COMPANY DATA - Master Services Panama S.A.
# ============================================================================

# Company Information
COMPANY_INFO = {
    "name": "Master Services Panama, S.A.",
    "founded": 1978,
    "general_manager": "Frederick M. Roberts V.",
    "founder": "Armando Campos",
    "location": "Edificio Grupo Master, Vía Domingo Díaz, Villa Lucre, Panamá",
    "phone": "+507 274-0836",
    "email": "operaciones@masterservices.org",
    "website": "masterservices.org",
}

# Employee Database
EMPLOYEES: Dict[str, Employee] = {
    # Maintenance Department (8 technicians)
    "Brandon Benavides": Employee(
        name="Brandon Benavides",
        department=Department.MAINTENANCE,
        monthly_salary=607.36,
        skills=["Maintenance", "Calibration", "Leak Testing"],
        years_experience=5,
    ),
    "Rigoberto Buitrago": Employee(
        name="Rigoberto Buitrago",
        department=Department.MAINTENANCE,
        monthly_salary=607.36,
        skills=["Maintenance", "Equipment Installation"],
        years_experience=6,
    ),
    "Armando Campos": Employee(
        name="Armando Campos",
        department=Department.MAINTENANCE,
        monthly_salary=700.76,
        skills=["Maintenance", "Electrical Work", "Tank Installation"],
        years_experience=15,
    ),
    "Pedro Vergara": Employee(
        name="Pedro Vergara",
        department=Department.MAINTENANCE,
        monthly_salary=679.04,
        skills=["Maintenance", "Calibration", "Dispensers"],
        years_experience=12,
    ),
    "Eugenio Espinosa": Employee(
        name="Eugenio Espinosa",
        department=Department.MAINTENANCE,
        monthly_salary=855.00,
        skills=["Maintenance", "Electrical Work", "Emergency Service"],
        years_experience=18,
    ),
    "Ángel López": Employee(
        name="Ángel López",
        department=Department.MAINTENANCE,
        monthly_salary=1200.00,
        skills=["Maintenance", "Station Construction", "Project Management"],
        years_experience=20,
    ),
    "Luis Madrid": Employee(
        name="Luis Madrid",
        department=Department.MAINTENANCE,
        monthly_salary=705.75,
        skills=["Maintenance", "Calibration", "Leak Testing"],
        years_experience=10,
    ),
    "Rodolfo Ortega": Employee(
        name="Rodolfo Ortega",
        department=Department.MAINTENANCE,
        monthly_salary=963.00,
        skills=["Maintenance", "Tank Installation", "Electrical Work"],
        years_experience=16,
    ),
    # Operations Department (4 technicians)
    "Dagoberto Torres": Employee(
        name="Dagoberto Torres",
        department=Department.OPERATIONS,
        monthly_salary=1355.00,
        skills=["Station Construction", "Equipment Installation", "Project Lead"],
        years_experience=22,
    ),
    "Daniel Torres": Employee(
        name="Daniel Torres",
        department=Department.OPERATIONS,
        monthly_salary=857.50,
        skills=["Station Construction", "Tank Installation", "Electrical Work"],
        years_experience=14,
    ),
    "Víctor Torres": Employee(
        name="Víctor Torres",
        department=Department.OPERATIONS,
        monthly_salary=607.36,
        skills=["Equipment Installation", "Maintenance"],
        years_experience=7,
    ),
    "Omar de Gracia": Employee(
        name="Omar de Gracia",
        department=Department.OPERATIONS,
        monthly_salary=607.36,
        skills=["Equipment Installation", "Tank Installation"],
        years_experience=8,
    ),
    # Administration Department (4 employees)
    "Frederick Roberts": Employee(
        name="Frederick Roberts",
        department=Department.ADMINISTRATION,
        monthly_salary=1467.00,
        skills=["Management", "Strategic Planning", "Client Relations"],
        years_experience=10,
    ),
    "Keyla Domínguez": Employee(
        name="Keyla Domínguez",
        department=Department.ADMINISTRATION,
        monthly_salary=631.37,
        skills=["Administration", "Documentation"],
        years_experience=8,
    ),
    "Gian Troncoso": Employee(
        name="Gian Troncoso",
        department=Department.ADMINISTRATION,
        monthly_salary=900.00,
        skills=["Operations Coordination", "Client Relations"],
        years_experience=12,
    ),
    "Xiomara Osorio": Employee(
        name="Xiomara Osorio",
        department=Department.ADMINISTRATION,
        monthly_salary=1030.00,
        skills=["Administration", "Project Coordination"],
        years_experience=15,
    ),
    # Mechanics Department (1 technician)
    "Edilberto Arauz": Employee(
        name="Edilberto Arauz",
        department=Department.MECHANICS,
        monthly_salary=782.50,
        skills=["Mechanical Repair", "Equipment Maintenance", "Fleet Management"],
        years_experience=20,
    ),
}

# Financial Metrics
FINANCIAL_DATA = {
    "total_monthly_salaries": 14556.36,
    "benefits_percentage": 0.337,  # 33.7% for social security, insurance, etc.
    "total_monthly_payroll": 19461.85,  # Salaries + benefits
    "monthly_operating_cost": 25544.67,  # Including vehicles, insurance, etc.
    "hourly_cost_no_profit": 145.14,  # Cost per technical hour without profit margin
    "hourly_rate_25percent_margin": 181.43,  # With 25% operational margin
    "fleet_vehicles": 8,
    "monthly_services": 1000,  # Average number of service calls per month
}

# Major Clients
MAJOR_CLIENTS = [
    "Delta Petroleum (Petróleos Delta)",
    "Texaco",
    "Terpel",
    "Puma Energy",
    "US Navy",
    "Panama Canal Commission",
    "Government of Panama",
]

# Service Pricing (base hourly rates)
SERVICE_PRICING = {
    ServiceType.STATION_CONSTRUCTION: {
        "hourly_rate": 200.00,
        "typical_hours": 2000,  # Full station construction
        "materials_markup": 1.20,  # 20% markup on materials
    },
    ServiceType.STATION_MAINTENANCE: {
        "hourly_rate": 181.43,
        "typical_hours": 8,
        "materials_markup": 1.15,
    },
    ServiceType.EQUIPMENT_INSTALLATION: {
        "hourly_rate": 190.00,
        "typical_hours": 40,
        "materials_markup": 1.18,
    },
    ServiceType.TANK_INSTALLATION: {
        "hourly_rate": 195.00,
        "typical_hours": 80,
        "materials_markup": 1.18,
    },
    ServiceType.LEAK_TESTING: {
        "hourly_rate": 185.00,
        "typical_hours": 4,
        "materials_markup": 1.10,
    },
    ServiceType.ELECTRICAL_WORK: {
        "hourly_rate": 188.00,
        "typical_hours": 24,
        "materials_markup": 1.15,
    },
    ServiceType.EMERGENCY_SERVICE: {
        "hourly_rate": 225.00,  # Premium rate for 24/7 service
        "typical_hours": 6,
        "materials_markup": 1.20,
    },
    ServiceType.CALIBRATION: {
        "hourly_rate": 175.00,
        "typical_hours": 3,
        "materials_markup": 1.10,
    },
}

# Competitor Information
COMPETITORS = {
    "Rodrigo Blanco": {
        "relationship": "Ex-employee, trained by Master Services",
        "strengths": ["Lower prices for local work", "Can handle local warranties"],
        "weaknesses": ["Limited national coverage", "Less experience"],
        "estimated_hourly_rate": 120.00,  # More competitive pricing
    },
}

# Strategic Focus (2024 onwards)
STRATEGIC_FOCUS = [
    "Construction and remodeling projects",
    "Specialized technical services with certification",
    "Interior country work (national coverage advantage)",
    "Specialized technical support when required",
    "Delegate routine local maintenance to lower-cost providers",
]

# Recent Major Projects
RECENT_PROJECTS = [
    {
        "name": "Delta San Gabriel Station, Calle 50",
        "type": "Complete construction",
        "scope": ["Civil work", "Electrical", "Mechanical", "Fire protection systems"],
    },
    {
        "name": "Texaco ICA Corredor Sur",
        "type": "Tank installation",
        "scope": ["6 tanks of 5,000 gallons on SKIDS", "Inventory monitoring systems"],
    },
    {
        "name": "Manzanillo International Terminal Fuel Center",
        "type": "Aerial fuel dispatch system",
        "scope": ["Civil work on dock", "Electrical", "Mechanical"],
    },
    {
        "name": "Delta Hato Pintado Station",
        "type": "Electrical and communications",
        "scope": ["Electrical piping", "Structured cabling", "Surge protection"],
    },
]


def get_department_employees(department: Department) -> List[Employee]:
    """Get all employees in a specific department."""
    return [emp for emp in EMPLOYEES.values() if emp.department == department]


def get_total_department_salary(department: Department) -> float:
    """Calculate total monthly salary for a department."""
    return sum(emp.monthly_salary for emp in get_department_employees(department))


def calculate_project_cost(
    service_type: ServiceType, hours: float, materials_cost: float = 0
) -> Dict[str, float]:
    """Calculate the total cost and pricing for a project.

    Args:
        service_type: Type of service being provided
        hours: Estimated hours for the project
        materials_cost: Cost of materials (before markup)

    Returns:
        Dictionary with cost breakdown
    """
    pricing = SERVICE_PRICING.get(service_type, {})
    hourly_rate = pricing.get("hourly_rate", FINANCIAL_DATA["hourly_rate_25percent_margin"])
    materials_markup = pricing.get("materials_markup", 1.15)

    labor_cost = hours * hourly_rate
    materials_price = materials_cost * materials_markup
    total_price = labor_cost + materials_price

    # Calculate internal costs for profitability analysis
    internal_labor_cost = hours * FINANCIAL_DATA["hourly_cost_no_profit"]
    total_cost = internal_labor_cost + materials_cost
    profit = total_price - total_cost
    profit_margin = (profit / total_price * 100) if total_price > 0 else 0

    return {
        "labor_hours": hours,
        "labor_rate": hourly_rate,
        "labor_price": labor_cost,
        "materials_cost": materials_cost,
        "materials_markup": materials_markup,
        "materials_price": materials_price,
        "total_price": total_price,
        "internal_cost": total_cost,
        "estimated_profit": profit,
        "profit_margin_percent": profit_margin,
    }


def find_employees_with_skill(skill: str) -> List[Employee]:
    """Find all employees with a specific skill."""
    return [emp for emp in EMPLOYEES.values() if skill in emp.skills and emp.active]


def get_company_summary() -> str:
    """Get a formatted summary of company information."""
    summary = f"""
MASTER SERVICES PANAMA, S.A. - COMPANY SUMMARY
{'=' * 60}

Founded: {COMPANY_INFO['founded']} ({2025 - COMPANY_INFO['founded']} years)
General Manager: {COMPANY_INFO['general_manager']}
Location: {COMPANY_INFO['location']}

PERSONNEL:
- Total Employees: {len(EMPLOYEES)}
- Maintenance: {len(get_department_employees(Department.MAINTENANCE))} technicians
- Operations: {len(get_department_employees(Department.OPERATIONS))} technicians
- Administration: {len(get_department_employees(Department.ADMINISTRATION))} employees
- Mechanics: {len(get_department_employees(Department.MECHANICS))} technician

FINANCIAL OVERVIEW:
- Monthly Salaries: ${FINANCIAL_DATA['total_monthly_salaries']:,.2f}
- Monthly Payroll (with benefits): ${FINANCIAL_DATA['total_monthly_payroll']:,.2f}
- Total Operating Cost: ${FINANCIAL_DATA['monthly_operating_cost']:,.2f}
- Hourly Rate (25% margin): ${FINANCIAL_DATA['hourly_rate_25percent_margin']:.2f}
- Fleet Vehicles: {FINANCIAL_DATA['fleet_vehicles']}
- Monthly Service Calls: ~{FINANCIAL_DATA['monthly_services']}

MAJOR CLIENTS: {', '.join(MAJOR_CLIENTS[:3])}... and more

STRATEGIC FOCUS:
{chr(10).join('  - ' + focus for focus in STRATEGIC_FOCUS[:3])}
"""
    return summary

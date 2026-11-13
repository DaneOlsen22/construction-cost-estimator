
from bakery import assert_equal
from drafter import *
from dataclasses import dataclass, field


hide_debug_information()
set_website_title("Construction Cost Estimator")
set_website_framed(False)


# Stores the information for each material
@dataclass
class Material:
    name: str
    quantity: float
    price: float


# Keeps track of the project information
@dataclass
class State:
    project_name: str = ""
    budget: float = 0.0
    materials: list[Material] = field(default_factory=list)
    total_cost: float = 0.0
    notes: str = ""
    message: str = ""


# Adds up the cost of all materials
def calculate_total(materials: list[Material]) -> float:
    """Finds the total material cost."""
    total = 0.0

    for material in materials:
        total += material.quantity * material.price

    return round(total, 2)


# Makes prices look like dollar amounts
def money(amount: float) -> str:
    """Turns a number into a dollar amount."""
    return "$" + format(amount, ",.2f")


# Makes a list of the materials
def material_list(state: State) -> list:
    """Shows all materials and their costs."""
    items = []

    if len(state.materials) == 0:
        items.append(Paragraph("No materials added yet."))
    else:
        for material in state.materials:
            cost = material.quantity * material.price

            items.append(Paragraph(
                material.name + " | Quantity: " +
                str(material.quantity) + " | Unit Price: " +
                money(material.price) + " | Total: " +
                money(cost)
            ))

    return items


# Home page
@route
def index(state: State) -> Page:
    """Shows the home page."""
    return Page(state, [
        Header("Construction Cost Estimator"),
        Paragraph("Welcome to my Construction Cost Estimator!"),
        Paragraph(
            "This website helps you estimate construction "
            "material costs and compare them to your budget."
        ),
        Paragraph("Project: " + state.project_name),
        Paragraph("Current Total: " + money(state.total_cost)),
        Button("Create or Edit Project", "project"),
        Button("Add Materials", "materials"),
        Button("View Materials", "view_materials"),
        Button("Cost Estimate", "estimate"),
        Button("Project Summary", "summary"),
        Button("Project Notes", "notes_page")
    ])


# Page to create a project
@route
def project(state: State) -> Page:
    """Lets the user create a project."""
    return Page(state, [
        Header("Create Your Project"),
        Paragraph("Enter the information for your project."),
        Paragraph("Project Name:"),
        TextBox("name", state.project_name),
        Paragraph("Project Budget ($):"),
        TextBox("budget", state.budget, "number"),
        Button("Save Project", "save_project"),
        Button("Back Home", "index")
    ])


# Saves the project information
@route
def save_project(state: State, name: str,
                 budget: float) -> Page:
    """Saves the project name and budget."""

    if name.strip() == "":
        state.message = "Please enter a project name."

    elif budget < 0:
        state.message = "Your budget cannot be negative."

    else:
        state.project_name = name
        state.budget = budget
        state.message = "Project saved successfully!"

    return Page(state, [
        Header("Project Information"),
        Paragraph(state.message),
        Paragraph("Project: " + state.project_name),
        Paragraph("Budget: " + money(state.budget)),
        Button("Continue to Materials", "materials"),
        Button("Edit Project", "project"),
        Button("Home", "index")
    ])


# Page to add materials
@route
def materials(state: State) -> Page:
    """Lets the user enter construction materials."""
    return Page(state, [
        Header("Add Construction Materials"),
        Paragraph("Enter the material you want to add."),
        Paragraph("Material Name:"),
        TextBox("material_name", ""),
        Paragraph("Material Type:"),
        SelectBox("material_type", [
            "Lumber",
            "Concrete",
            "Steel",
            "Drywall",
            "Roofing",
            "Electrical",
            "Plumbing",
            "Other"
        ]),
        Paragraph("Quantity:"),
        TextBox("quantity", 1, "number"),
        Paragraph("Price Per Unit ($):"),
        TextBox("price", 0, "number"),
        Button("Add Material", "add_material"),
        Button("View Materials", "view_materials"),
        Button("Home", "index")
    ])


# Adds a material and updates the total
@route
def add_material(state: State, material_name: str,
                 material_type: str, quantity: float,
                 price: float) -> Page:
    """Adds a material to the project."""

    if material_name.strip() == "":
        state.message = "Please enter a material name."

    elif quantity <= 0:
        state.message = "Quantity must be greater than zero."

    elif price < 0:
        state.message = "Price cannot be negative."

    else:
        new_material = Material(
            material_type + " - " + material_name,
            quantity,
            price
        )

        state.materials.append(new_material)
        state.total_cost = calculate_total(state.materials)
        state.message = "Material added successfully!"

    return Page(state, [
        Header("Material Result"),
        Paragraph(state.message),
        Paragraph("Current Total: " + money(state.total_cost)),
        Button("Add Another Material", "materials"),
        Button("View Materials", "view_materials"),
        Button("Home", "index")
    ])


# Shows the materials in the project
@route
def view_materials(state: State) -> Page:
    """Shows the list of materials."""
    content = [
        Header("Your Materials"),
        Paragraph("Project: " + state.project_name)
    ]

    content.extend(material_list(state))

    content.extend([
        Paragraph("Total Cost: " + money(state.total_cost)),
        Button("Add Material", "materials"),
        Button("Remove Material", "remove_page"),
        Button("View Estimate", "estimate"),
        Button("Home", "index")
    ])

    return Page(state, content)


# Page to remove materials
@route
def remove_page(state: State) -> Page:
    """Lets the user pick a material to remove."""
    content = [
        Header("Remove a Material")
    ]

    if len(state.materials) == 0:
        content.append(
            Paragraph("There are no materials to remove.")
        )

    else:
        names = []

        for material in state.materials:
            names.append(material.name)

        content.append(
            Paragraph("Select a material to remove:")
        )
        content.append(SelectBox("selected", names))
        content.append(
            Button("Remove Selected", "delete_material")
        )

    content.append(
        Button("Back to Materials", "view_materials")
    )

    return Page(state, content)


# Removes a material from the list
@route
def delete_material(state: State, selected: str) -> Page:
    """Removes a material and updates the total."""
    updated_materials = []
    removed = False

    for material in state.materials:
        if material.name == selected and not removed:
            removed = True
        else:
            updated_materials.append(material)

    state.materials = updated_materials
    state.total_cost = calculate_total(state.materials)

    if removed:
        state.message = "Material removed successfully."
    else:
        state.message = "Material was not found."

    return Page(state, [
        Header("Remove Material"),
        Paragraph(state.message),
        Paragraph("New Total: " + money(state.total_cost)),
        Button("View Materials", "view_materials"),
        Button("Home", "index")
    ])


# Shows the estimated project cost
@route
def estimate(state: State) -> Page:
    """Checks if the project is within budget."""
    remaining = state.budget - state.total_cost

    if len(state.materials) == 0:
        result = "Add some materials to create an estimate."

    elif state.total_cost > state.budget:
        result = "Warning: Your project is over budget!"

    elif state.total_cost == state.budget:
        result = "Your project is exactly on budget!"

    else:
        result = "Good news! Your project is under budget."

    return Page(state, [
        Header("Construction Cost Estimate"),
        Paragraph("Project: " + state.project_name),
        Paragraph("Project Budget: " + money(state.budget)),
        Paragraph("Material Costs: " + money(state.total_cost)),
        Paragraph("Remaining Budget: " + money(remaining)),
        Paragraph(result),
        Button("View Materials", "view_materials"),
        Button("Project Summary", "summary"),
        Button("Home", "index")
    ])


# Shows all the project information
@route
def summary(state: State) -> Page:
    """Shows the project summary."""
    number_of_materials = len(state.materials)
    remaining = state.budget - state.total_cost

    content = [
        Header("Project Summary"),
        Paragraph("Project Name: " + state.project_name),
        Paragraph("Project Budget: " + money(state.budget)),
        Paragraph(
            "Number of Materials: " + str(number_of_materials)
        ),
        Paragraph("Estimated Cost: " + money(state.total_cost)),
        Paragraph("Remaining Budget: " + money(remaining)),
        Header("Material Breakdown", 2)
    ]

    content.extend(material_list(state))

    content.extend([
        Header("Project Notes", 2),
        Paragraph(state.notes),
        Button("Edit Project", "project"),
        Button("Edit Notes", "notes_page"),
        Button("Cost Estimate", "estimate"),
        Button("Home", "index")
    ])

    return Page(state, content)


# Page for writing project notes
@route
def notes_page(state: State) -> Page:
    """Lets the user write project notes."""
    return Page(state, [
        Header("Project Notes"),
        Paragraph(
            "Use this space to write important information "
            "about your construction project."
        ),
        TextArea("project_notes", state.notes),
        Button("Save Notes", "save_notes"),
        Button("Project Summary", "summary"),
        Button("Home", "index")
    ])


# Saves the project notes
@route
def save_notes(state: State, project_notes: str) -> Page:
    """Saves the notes entered by the user."""
    state.notes = project_notes
    state.message = "Your notes have been saved."

    return Page(state, [
        Header("Notes Saved"),
        Paragraph(state.message),
        Paragraph(state.notes),
        Button("Edit Notes", "notes_page"),
        Button("Project Summary", "summary"),
        Button("Home", "index")
    ])


# Tests for the website
def test_website() -> None:
    """Checks the main website features."""

    # Tests the cost calculations
    assert_equal(calculate_total([]), 0)
    assert_equal(
        calculate_total([Material("Wood", 10, 5)]), 50
    )
    assert_equal(
        calculate_total([Material("Concrete", 5, 20)]), 100
    )
    assert_equal(money(100), "$100.00")
    assert_equal(money(25.50), "$25.50")
    assert_equal(money(1000), "$1,000.00")

    # Tests the home and project pages
    state = State()

    assert_equal(index(state) is not None, True)
    assert_equal(project(state) is not None, True)

    save_project(state, "New House", 5000)
    assert_equal(state.project_name, "New House")
    assert_equal(state.budget, 5000)
    assert_equal(
        state.message, "Project saved successfully!"
    )

    # Tests an incorrect budget
    save_project(state, "Bad Budget", -100)
    assert_equal(state.budget, 5000)

    # Tests adding materials
    assert_equal(materials(state) is not None, True)

    add_material(state, "2x4", "Lumber", 10, 5)
    assert_equal(len(state.materials), 1)
    assert_equal(state.total_cost, 50)

    add_material(state, "Cement", "Concrete", 5, 20)
    assert_equal(len(state.materials), 2)
    assert_equal(state.total_cost, 150)

    # Tests invalid materials
    add_material(state, "", "Lumber", 5, 10)
    assert_equal(len(state.materials), 2)

    add_material(state, "Steel", "Steel", -5, 20)
    assert_equal(len(state.materials), 2)

    # Tests the other pages
    assert_equal(view_materials(state) is not None, True)
    assert_equal(remove_page(state) is not None, True)
    assert_equal(estimate(state) is not None, True)
    assert_equal(summary(state) is not None, True)
    assert_equal(notes_page(state) is not None, True)

    # Tests removing materials
    delete_material(state, "Lumber - 2x4")
    assert_equal(len(state.materials), 1)
    assert_equal(state.total_cost, 100)

    delete_material(state, "Concrete - Cement")
    assert_equal(len(state.materials), 0)
    assert_equal(state.total_cost, 0)

    # Tests saving notes
    save_notes(state, "Order more supplies")
    assert_equal(state.notes, "Order more supplies")

    # Tests the project summary again
    assert_equal(summary(state) is not None, True)


# Run the tests
test_website()


# Website information for GitHub
set_site_information(
    author="Dane Olsen",
    description=(
        "A website that helps users estimate construction "
        "material costs and compare expenses to a project budget."
    ),
    sources="Drafter documentation and ChatGPT assistance",
    planning=["brainstorm.pdf", "design.pdf"],
    links=[]
)


# Starts the website
start_server(State())

# Oracle SQL Query Visualizer

A Python tool to visualize Oracle SQL query structures as ERP-style entity-relationship diagrams with tables, columns, and relationship connections.

## Features

✨ **Key Features:**
- 📦 Create table structures with columns, data types, and constraints
- 🔐 Mark Primary Keys (PK) and Foreign Keys (FK) with special formatting
- 🔗 Define relationships between tables (1:1, 1:N, N:N)
- 📊 Generate multiple visualization formats:
  - **HTML**: Interactive visualization with physics-based node layout
  - **PNG (Graphviz)**: Professional ERD diagrams

## Installation

```bash
# Clone or copy the project
cd toy-project

# Optional: Install graphviz for PNG export
pip install graphviz

# For Ubuntu/Debian also install the graphviz system package:
# sudo apt-get install graphviz

# For macOS:
# brew install graphviz

# For Windows:
# Download from https://graphviz.org/download/
```

## Quick Start

### Basic Usage

```python
from sql_visualizer import SQLSchemaVisualizer, Table, Column, Relationship, KeyType

# Create visualizer
viz = SQLSchemaVisualizer()

# Define a table
users = Table(name="users", alias="u")
users.add_column(Column("user_id", "NUMBER", KeyType.PRIMARY, nullable=False))
users.add_column(Column("username", "VARCHAR2(50)", KeyType.UNIQUE, nullable=False))
users.add_column(Column("email", "VARCHAR2(100)", KeyType.NONE, nullable=False))

# Add to visualizer
viz.add_table(users)

# Define relationships
orders = Table(name="orders")
orders.add_column(Column("order_id", "NUMBER", KeyType.PRIMARY, nullable=False))
orders.add_column(Column("user_id", "NUMBER", KeyType.FOREIGN, nullable=False))

viz.add_table(orders)
viz.add_relationship(Relationship("users", "user_id", "orders", "user_id", "1:N"))

# Generate outputs
viz.print_schema()                           # Console output
viz.generate_graphviz("my_schema")          # PNG file
viz.generate_html("my_schema.html")         # HTML file
```

## Data Types

### Column Key Types
```python
KeyType.PRIMARY    # Primary key (🔑)
KeyType.FOREIGN    # Foreign key (🔗)
KeyType.UNIQUE     # Unique constraint
KeyType.NONE       # Regular column
```

### Relationship Types
```
"1:1"  # One-to-One
"1:N"  # One-to-Many
"N:N"  # Many-to-Many
```

## File Structure

```
.
├── sql_visualizer.py              # Main library
├── sql-visualizer-demo.ipynb      # Jupyter notebook with examples
├── README.md                       # This file
└── [generated files]
    ├── *.html                      # Interactive HTML diagrams
    └── *.png                       # Graphviz diagrams (if graphviz installed)
```

## Examples

### E-Commerce Schema

```python
# E-commerce with customers, orders, order_items, and products
# See sql-visualizer-demo.ipynb for full example
```

### HR Management Schema

```python
# HR schema with employees, departments, jobs, and locations
# See sql-visualizer-demo.ipynb for full example
```

### University System

```python
# University schema with students, programs, courses, enrollments, professors
# See sql-visualizer-demo.ipynb for full example
```

## API Reference

### SQLSchemaVisualizer

Main class for managing and visualizing schemas.

#### Methods:
- `add_table(table: Table)` - Add a table to the schema
- `add_relationship(rel: Relationship)` - Add a relationship between tables
- `parse_simple_sql(sql: str)` - Parse basic SQL SELECT with JOINs
- `print_schema()` - Print formatted schema to console
- `generate_graphviz(filename, view=False)` - Generate PNG diagram (requires graphviz)
- `generate_html(filename)` - Generate interactive HTML diagram

### Table

Represents a database table.

#### Constructor:
```python
Table(name: str, alias: str = None, columns: List[Column] = None)
```

#### Methods:
- `add_column(column: Column)` - Add column to table
- `get_display_name()` - Returns alias or table name

### Column

Represents a table column.

#### Constructor:
```python
Column(
    name: str,
    data_type: str,
    key_type: KeyType = KeyType.NONE,
    nullable: bool = True
)
```

### Relationship

Represents a relationship between two tables.

#### Constructor:
```python
Relationship(
    from_table: str,
    from_column: str,
    to_table: str,
    to_column: str,
    relationship_type: str = "1:N"
)
```

## Output Formats

### HTML Output

- **Interactive visualization** with physics-based layout
- **Pan and zoom** support
- **Hover tooltips** showing table information
- **Works in any browser** - no dependencies required
- File: `<name>.html`

### Graphviz PNG Output

- **Professional ERD diagram**
- **High quality** raster image
- **Box-based layout** with clear connections
- **Requires graphviz system package** installation
- File: `<name>.png`

## Troubleshooting

### Graphviz not found
```
Error: "dot" not found in path. Is graphviz installed?
```
**Solution**: Install graphviz system package
- Windows: Download from https://graphviz.org/download/
- macOS: `brew install graphviz`
- Linux: `sudo apt-get install graphviz`

### HTML file opens but looks plain
This is normal. The HTML uses Vis.js library for interactive visualization. Open in a modern browser (Chrome, Firefox, Safari, Edge).

## Performance

- **HTML generation**: Fast (< 1 second for typical schemas)
- **Graphviz generation**: Depends on schema complexity (1-5 seconds)
- **Recommended size**: Up to 50-100 tables per diagram

For larger schemas, consider splitting into multiple visualizations.

## Limitations

1. **SQL Parsing**: Limited to basic SELECT with simple JOINs
   - For complex queries, manually define tables and relationships

2. **Graphviz**: Requires system installation
   - HTML output always works without prerequisites

3. **Layout**: HTML uses physics simulation
   - May require adjustment for very large schemas

## Contributing

To extend the visualizer:
1. Add new relationship types to `Relationship` class
2. Extend `generate_*` methods for custom output formats
3. Enhance SQL parsing in `parse_simple_sql` method

## License

See LICENSE file in the project root.

## Examples

See `sql-visualizer-demo.ipynb` for complete working examples:
- E-Commerce Schema
- HR Management System  
- University Management System
- Custom schema creation

## Support

For issues or questions:
1. Check the notebook examples first
2. Review the API reference above
3. Check the troubleshooting section

---

**Created for visualizing Oracle SQL query structures as entity-relationship diagrams**

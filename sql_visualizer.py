"""
Oracle SQL Query Visualizer
Visualizes SQL queries as ERP-style diagrams with tables, columns, and relationships
"""

import re
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum

try:
    import graphviz
    HAS_GRAPHVIZ = True
except ImportError:
    HAS_GRAPHVIZ = False


class KeyType(Enum):
    """Column key type"""
    NONE = "none"
    PRIMARY = "primary"
    FOREIGN = "foreign"
    UNIQUE = "unique"


@dataclass
class Column:
    """Represents a table column"""
    name: str
    data_type: str
    key_type: KeyType = KeyType.NONE
    nullable: bool = True
    
    def __str__(self) -> str:
        """Return formatted column string"""
        prefix = ""
        if self.key_type == KeyType.PRIMARY:
            prefix = "🔑 "
        elif self.key_type == KeyType.FOREIGN:
            prefix = "🔗 "
        
        nullable_marker = "" if self.nullable else " NOT NULL"
        return f"{prefix}{self.name}: {self.data_type}{nullable_marker}"


@dataclass
class Table:
    """Represents a table with columns"""
    name: str
    alias: Optional[str] = None
    columns: List[Column] = None
    
    def __post_init__(self):
        if self.columns is None:
            self.columns = []
    
    def add_column(self, column: Column) -> None:
        """Add a column to the table"""
        self.columns.append(column)
    
    def get_display_name(self) -> str:
        """Get display name (alias if available)"""
        return self.alias or self.name


@dataclass
class Relationship:
    """Represents a relationship between two tables"""
    from_table: str
    from_column: str
    to_table: str
    to_column: str
    relationship_type: str = "1:N"  # 1:1, 1:N, N:N


class SQLSchemaVisualizer:
    """Main class for SQL schema visualization"""
    
    def __init__(self):
        """Initialize the visualizer"""
        self.tables: Dict[str, Table] = {}
        self.relationships: List[Relationship] = []
    
    def add_table(self, table: Table) -> None:
        """Add a table to the schema"""
        self.tables[table.name] = table
    
    def add_relationship(self, relationship: Relationship) -> None:
        """Add a relationship between tables"""
        self.relationships.append(relationship)
    
    def parse_simple_sql(self, sql: str) -> None:
        """
        Parse a simple SQL query to extract tables and joins
        Supports basic SELECT with JOINs
        """
        # Extract FROM clause
        from_pattern = r'FROM\s+(\w+)(?:\s+(?:AS\s+)?(\w+))?'
        from_matches = re.finditer(from_pattern, sql, re.IGNORECASE)
        
        for match in from_matches:
            table_name = match.group(1)
            alias = match.group(2) or table_name
            if table_name not in self.tables:
                table = Table(name=table_name, alias=alias)
                self.add_table(table)
        
        # Extract JOIN clauses
        join_pattern = r'(?:INNER\s+|LEFT\s+|RIGHT\s+|FULL\s+)?JOIN\s+(\w+)(?:\s+(?:AS\s+)?(\w+))?\s+ON\s+(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)'
        join_matches = re.finditer(join_pattern, sql, re.IGNORECASE)
        
        for match in join_matches:
            join_table = match.group(1)
            join_alias = match.group(2) or join_table
            
            if join_table not in self.tables:
                table = Table(name=join_table, alias=join_alias)
                self.add_table(table)
            
            # Extract join condition
            from_table = match.group(3)
            from_col = match.group(4)
            to_table = match.group(5)
            to_col = match.group(6)
            
            relationship = Relationship(
                from_table=from_table,
                from_column=from_col,
                to_table=to_table,
                to_column=to_col
            )
            self.add_relationship(relationship)
    
    def generate_graphviz(self, filename: str = "sql_schema", view: bool = False) -> Optional[str]:
        """
        Generate a Graphviz diagram
        
        Args:
            filename: Output filename (without extension)
            view: Whether to open the diagram after generation
            
        Returns:
            Path to generated file or None if graphviz not available
        """
        if not HAS_GRAPHVIZ:
            print("⚠️  Graphviz not installed. Install with: pip install graphviz")
            return None
        
        dot = graphviz.Digraph(
            name=filename,
            comment='SQL Schema Diagram',
            format='png',
            engine='dot',
            graph_attr={
                'rankdir': 'TB',
                'bgcolor': 'white',
                'splines': 'ortho',
                'nodesep': '1',
                'ranksep': '1.5'
            },
            node_attr={
                'shape': 'plaintext',
                'fontname': 'Arial',
                'fontsize': '10'
            },
            edge_attr={
                'color': '#666666',
                'arrowsize': '1.5',
                'fontsize': '9'
            }
        )
        
        # Create table nodes
        for table_name, table in self.tables.items():
            html_label = self._create_html_label(table)
            dot.node(
                name=table_name,
                label=html_label,
            )
        
        # Create relationships
        for rel in self.relationships:
            dot.edge(
                rel.from_table,
                rel.to_table,
                label=f"{rel.from_column}→{rel.to_column}",
                color='#0066CC'
            )
        
        # Render
        try:
            output_path = dot.render(filename=filename, cleanup=True)
            print(f"✓ Diagram generated: {output_path}")
            
            if view:
                dot.view()
            
            return output_path
        except Exception as e:
            print(f"✗ Error rendering diagram: {e}")
            return None
    
    def _create_html_label(self, table: Table) -> str:
        """Create HTML label for table node"""
        
        # Table header
        html = f'<TABLE BORDER="2" CELLBORDER="1" CELLSPACING="0" CELLPADDING="8" BGCOLOR="#E8F4F8">'
        html += f'<TR><TD COLSPAN="2" BGCOLOR="#0066CC" ALIGN="CENTER"><B><FONT COLOR="white">{table.get_display_name()}</FONT></B></TD></TR>'
        
        # Columns
        if not table.columns:
            html += f'<TR><TD COLSPAN="2"><I>No columns defined</I></TD></TR>'
        else:
            for col in table.columns:
                col_name = col.name
                col_type = col.data_type
                
                # Format based on key type
                if col.key_type == KeyType.PRIMARY:
                    col_name = f"<B><U>{col_name}</U></B>"
                elif col.key_type == KeyType.FOREIGN:
                    col_name = f"<B>{col_name}</B>"
                
                html += f'<TR><TD ALIGN="LEFT">{col_name}</TD><TD ALIGN="LEFT"><FONT SIZE="8" COLOR="#666666">{col_type}</FONT></TD></TR>'
        
        html += '</TABLE>'
        
        return html
    
    def generate_html(self, filename: str = "sql_schema.html") -> str:
        """Generate an interactive HTML visualization"""
        html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>SQL Schema Diagram</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.min.js"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.min.css" rel="stylesheet" type="text/css" />
    <style>
        body {
            font-family: 'Courier New', Courier, monospace;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        #network {
            width: 100%;
            height: 100vh;
            border: 1px solid #ccc;
            background-color: white;
        }
        .info-panel {
            position: absolute;
            top: 20px;
            right: 20px;
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            max-width: 300px;
            z-index: 10;
        }
        h1 {
            color: #333;
            margin-bottom: 20px;
        }
        .legend {
            background: white;
            padding: 10px;
            border-radius: 5px;
            font-size: 12px;
            margin-bottom: 10px;
        }
        .legend-item {
            margin: 5px 0;
        }
    </style>
</head>
<body>
    <h1>SQL Schema Visualization</h1>
    <div class="info-panel">
        <div class="legend">
            <strong>Legend:</strong>
            <div class="legend-item">🔑 = Primary Key</div>
            <div class="legend-item">🔗 = Foreign Key</div>
            <div class="legend-item">→ = Relationship</div>
        </div>
    </div>
    <div id="network"></div>
    <script type="text/javascript">
        var nodes = new vis.DataSet([
"""
        
        # Add nodes with proper formatting
        for idx, (table_name, table) in enumerate(self.tables.items()):
            # Build label with newlines instead of HTML tags
            label_lines = [table_name.upper()]
            label_lines.append("-" * 40)
            
            for col in table.columns:
                prefix = ""
                if col.key_type == KeyType.PRIMARY:
                    prefix = "🔑 "
                elif col.key_type == KeyType.FOREIGN:
                    prefix = "🔗 "
                else:
                    prefix = "   "
                
                column_display = f"{prefix}{col.name}: {col.data_type}"
                label_lines.append(column_display)
            
            # Escape quotes and newlines for JavaScript
            label_text = "\\n".join(label_lines)
            label_text = label_text.replace('"', '\\"')
            
            # Escape for tooltip as well
            tooltip_text = f"{table_name} ({len(table.columns)} columns)"
            
            html_content += f"""            {{
                id: {idx},
                label: "{label_text}",
                title: "{tooltip_text}",
                shape: 'box',
                font: {{
                    size: 11,
                    face: 'Courier New',
                    color: '#000',
                    multi: true,
                    align: 'left'
                }},
                color: {{
                    background: '#E8F4F8',
                    border: '#0066CC',
                    highlight: {{
                        background: '#B3E5FC',
                        border: '#0044AA'
                    }}
                }},
                borderWidth: 2,
                margin: {{
                    top: 10,
                    right: 10,
                    bottom: 10,
                    left: 10
                }}
            }},
"""
        
        html_content += """        ]);

        var edges = new vis.DataSet([
"""
        
        # Add edges
        table_to_id = {name: idx for idx, name in enumerate(self.tables.keys())}
        for rel in self.relationships:
            from_id = table_to_id.get(rel.from_table)
            to_id = table_to_id.get(rel.to_table)
            if from_id is not None and to_id is not None:
                label_text = f"{rel.from_column}→{rel.to_column}"
                html_content += f"""            {{
                from: {from_id},
                to: {to_id},
                label: "{label_text}",
                arrows: "to",
                smooth: {{
                    type: "straightCross"
                }},
                color: {{
                    color: '#0066CC',
                    highlight: '#0044AA'
                }},
                font: {{
                    size: 10,
                    color: '#0066CC',
                    background: {{
                        enabled: true,
                        color: 'white'
                    }}
                }}
            }},
"""
        
        html_content += """        ]);

        var container = document.getElementById("network");
        var data = {
            nodes: nodes,
            edges: edges
        };
        var options = {
            autoResize: true,
            physics: {
                enabled: true,
                stabilization: {
                    iterations: 200,
                    fit: true
                },
                barnesHut: {
                    gravitationalConstant: -80000,
                    centralGravity: 0.3,
                    springLength: 300,
                    springConstant: 0.08
                }
            },
            edges: {
                width: 2,
                widthConstraint: {
                    maximum: 200
                }
            },
            nodes: {
                widthConstraint: {
                    maximum: 400
                },
                spacing: {
                    left: 0,
                    right: 0
                }
            },
            interaction: {
                navigationButtons: true,
                keyboard: true,
                zoomView: true,
                dragView: true
            }
        };
        
        var network = new vis.Network(container, data, options);
        
        // Auto-fit on load
        network.on("stabilizationIterationsDone", function() {
            network.setOptions({physics: false});
            network.fit();
        });
    </script>
</body>
</html>
"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✓ HTML visualization generated: {filename}")
        return filename
    
    def print_schema(self) -> None:
        """Print schema to console"""
        print("\n" + "="*60)
        print("SQL SCHEMA VISUALIZATION")
        print("="*60)
        
        for table_name, table in self.tables.items():
            print(f"\n📋 {table_name}")
            if table.alias and table.alias != table_name:
                print(f"   Alias: {table.alias}")
            
            if table.columns:
                for col in table.columns:
                    print(f"   - {col}")
            else:
                print("   (No columns defined)")
        
        if self.relationships:
            print("\n" + "-"*60)
            print("RELATIONSHIPS:")
            print("-"*60)
            for rel in self.relationships:
                print(f"  {rel.from_table}.{rel.from_column} → {rel.to_table}.{rel.to_column}")
        
        print("\n" + "="*60 + "\n")


# Example usage
if __name__ == "__main__":
    # Create visualizer
    viz = SQLSchemaVisualizer()
    
    # Example 1: E-commerce schema
    print("Creating E-commerce Schema...")
    
    # Add tables
    customers = Table(name="customers", alias="c")
    customers.add_column(Column("customer_id", "NUMBER", KeyType.PRIMARY, False))
    customers.add_column(Column("name", "VARCHAR2(100)", KeyType.NONE, False))
    customers.add_column(Column("email", "VARCHAR2(100)", KeyType.UNIQUE, False))
    customers.add_column(Column("created_at", "DATE", KeyType.NONE, True))
    
    orders = Table(name="orders", alias="o")
    orders.add_column(Column("order_id", "NUMBER", KeyType.PRIMARY, False))
    orders.add_column(Column("customer_id", "NUMBER", KeyType.FOREIGN, False))
    orders.add_column(Column("order_date", "DATE", KeyType.NONE, False))
    orders.add_column(Column("total_amount", "DECIMAL(10,2)", KeyType.NONE, True))
    
    products = Table(name="products", alias="p")
    products.add_column(Column("product_id", "NUMBER", KeyType.PRIMARY, False))
    products.add_column(Column("name", "VARCHAR2(100)", KeyType.NONE, False))
    products.add_column(Column("price", "DECIMAL(10,2)", KeyType.NONE, False))
    products.add_column(Column("category_id", "NUMBER", KeyType.FOREIGN, True))
    
    order_items = Table(name="order_items", alias="oi")
    order_items.add_column(Column("order_item_id", "NUMBER", KeyType.PRIMARY, False))
    order_items.add_column(Column("order_id", "NUMBER", KeyType.FOREIGN, False))
    order_items.add_column(Column("product_id", "NUMBER", KeyType.FOREIGN, False))
    order_items.add_column(Column("quantity", "NUMBER", KeyType.NONE, False))
    order_items.add_column(Column("unit_price", "DECIMAL(10,2)", KeyType.NONE, False))
    
    # Add to visualizer
    viz.add_table(customers)
    viz.add_table(orders)
    viz.add_table(products)
    viz.add_table(order_items)
    
    # Add relationships
    viz.add_relationship(Relationship("customers", "customer_id", "orders", "customer_id"))
    viz.add_relationship(Relationship("orders", "order_id", "order_items", "order_id"))
    viz.add_relationship(Relationship("products", "product_id", "order_items", "product_id"))
    
    # Print schema
    viz.print_schema()
    
    # Generate visualizations
    try:
        viz.generate_graphviz("ecommerce_schema", view=False)
    except Exception as e:
        print(f"Could not generate Graphviz: {e}")
    
    viz.generate_html("ecommerce_schema.html")
    print("\n✓ Visualization generated successfully!")
    print("  - HTML version: ecommerce_schema.html")
    print("  - Graphviz version: ecommerce_schema.png (if graphviz installed)")

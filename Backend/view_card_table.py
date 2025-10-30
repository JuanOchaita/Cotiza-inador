from sqlalchemy import (
    create_engine, MetaData, Table, Column, Integer, String, 
    DECIMAL, TIMESTAMP, ForeignKey, select, case, func, text
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import DDL

# Database connection
DATABASE_URL = "postgresql://myuser:mypassword@localhost:5433/mydb"
engine = create_engine(DATABASE_URL, echo=False)
metadata = MetaData()
Base = declarative_base()

# Define tables (matching your schema)
user_table = Table('user', metadata,
    Column('user_id', Integer, primary_key=True),
    Column('name', String),
    Column('email', String, unique=True),
    Column('created_at', TIMESTAMP)
)

card_condition = Table('card_condition', metadata,
    Column('condition_id', Integer, primary_key=True),
    Column('description', String, unique=True)
)

language_table = Table('language', metadata,
    Column('language_id', Integer, primary_key=True),
    Column('description', String, unique=True)
)

edition_table = Table('edition', metadata,
    Column('edition_id', Integer, primary_key=True),
    Column('description', String, unique=True)
)

set_name_table = Table('set_name', metadata,
    Column('set_name_id', Integer, primary_key=True),
    Column('description', String, unique=True)
)

image_table = Table('image', metadata,
    Column('image_url_id', Integer, primary_key=True),
    Column('url', String, unique=True)
)

card_table = Table('card', metadata,
    Column('card_id', Integer, primary_key=True),
    Column('name', String),
    Column('language_id', Integer, ForeignKey('language.language_id'), nullable=False),
    Column('set_name_id', Integer, ForeignKey('set_name.set_name_id'), nullable=False),
    Column('set_number', String),
    Column('image_id', Integer, ForeignKey('image.image_url_id'), nullable=False),
    Column('edition_id', Integer, ForeignKey('edition.edition_id'))
)

price_table = Table('price', metadata,
    Column('card_id', Integer, ForeignKey('card.card_id'), primary_key=True),
    Column('condition_id', Integer, ForeignKey('card_condition.condition_id'), primary_key=True),
    Column('price_usd', DECIMAL, nullable=False),
    Column('date', TIMESTAMP)
)

collection_table = Table('collection', metadata,
    Column('collection_id', Integer, primary_key=True),
    Column('title', String),
    Column('user_id', Integer, ForeignKey('user.user_id'), nullable=False),
    Column('exchange_rate', DECIMAL),
    Column('collection_price_usd', DECIMAL),
    Column('created_at', TIMESTAMP)
)

card_in_collection = Table('card_in_collection', metadata,
    Column('card_collection_id', Integer, primary_key=True),
    Column('collection_id', Integer, ForeignKey('collection.collection_id'), nullable=False),
    Column('card_id', Integer, nullable=False),
    Column('condition_id', Integer, nullable=False),
    Column('quantity', Integer)
)

# Create the view query using SQLAlchemy
def create_card_market_view():
    """
    Creates a database view for card market information
    """
    # Define the CASE statement for condition ordering
    condition_order = case(
        (card_condition.c.description == 'Damaged', 1),
        (card_condition.c.description == 'Heavily Played', 2),
        (card_condition.c.description == 'Moderately Played', 3),
        (card_condition.c.description == 'Lightly Played', 4),
        (card_condition.c.description == 'Near Mint', 5),
        else_=6
    )
    
    # Build the SELECT query
    view_query = select(
        card_table.c.name.label('card_name'),
        set_name_table.c.description.label('set_name'),
        card_table.c.set_number.label('number_in_set'),
        func.coalesce(edition_table.c.description, 'Normal').label('printing_option'),
        card_condition.c.description.label('condition'),
        price_table.c.price_usd.label('market_price'),
        image_table.c.url.label('image')
    ).select_from(
        card_table
        .join(set_name_table, card_table.c.set_name_id == set_name_table.c.set_name_id)
        .join(image_table, card_table.c.image_id == image_table.c.image_url_id)
        .join(price_table, card_table.c.card_id == price_table.c.card_id)
        .join(card_condition, price_table.c.condition_id == card_condition.c.condition_id)
        .outerjoin(edition_table, card_table.c.edition_id == edition_table.c.edition_id)
    ).order_by(
        card_table.c.name,
        set_name_table.c.description,
        card_table.c.set_number,
        func.coalesce(edition_table.c.description, 'Normal'),
        condition_order
    )
    
    # Convert the query to SQL
    view_sql = str(view_query.compile(
        engine, 
        compile_kwargs={"literal_binds": True}
    ))
    
    # Create the view DDL statement
    create_view_ddl = DDL(f"""
        CREATE OR REPLACE VIEW card_market_view AS
        {view_sql}
    """)
    
    # Execute the view creation
    with engine.connect() as conn:
        conn.execute(text("DROP VIEW IF EXISTS card_market_view"))
        conn.execute(create_view_ddl)
        conn.commit()
        print("View 'card_market_view' created successfully!")

# Function to query the view
def query_card_market_view(limit=None):
    """
    Query the card_market_view
    """
    with engine.connect() as conn:
        if limit:
            result = conn.execute(text(f"SELECT * FROM card_market_view LIMIT {limit}"))
        else:
            result = conn.execute(text("SELECT * FROM card_market_view"))
        
        rows = result.fetchall()
        columns = result.keys()
        
        return [dict(zip(columns, row)) for row in rows]

# Main execution
if __name__ == "__main__":
    try:
        # Create the view
        create_card_market_view()
        
        # Example: Query the view (first 10 records)
        print("\nQuerying card_market_view (first 10 records):")
        results = query_card_market_view()
        
        for row in results:
            print(row)
            
    except Exception as e:
        print(f"Error: {e}")
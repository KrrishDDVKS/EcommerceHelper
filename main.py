import sqlite3
#from Orchastrator import main_agent
def main():
    print("Hello from ecommercehelper!")
    

    conn = sqlite3.connect("ecommerce.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        sales_id INTEGER PRIMARY KEY AUTOINCREMENT,
        item TEXT NOT NULL,
        count INTEGER NOT NULL,
        total_price REAL NOT NULL,
        date TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
        inventory_id INTEGER PRIMARY KEY AUTOINCREMENT,
        item TEXT NOT NULL,
        date TEXT NOT NULL,
        count INTEGER NOT NULL,
        price_per_item REAL NOT NULL
    )
    """)

    conn.commit()
    conn.close()

    #main_agent.invoke({"messages": [{"role": "system", "content": "You are a helpful Ecommerce Agent who can call subagents to insert sales and inventory data into the database and provide insights about the sales and inventory data in the database."}, {"role": "user", "content": "Insert sales data for 10."}]})


if __name__ == "__main__":
    main()

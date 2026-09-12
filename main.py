import sqlite3
from agents.Orchastrator import main_agent
def main():
    print("Hello from ecommercehelper!")
    print("Always write items in Singular form. For example,\n write 'apple' instead of 'apples'.")
    print("Always specify one item at a time. For example,\n write 'I want to add 5 apples of $1.50.' \ninstead of 'I want to add 5 apples of $1.50 and 3 bananas of $0.75.'")
    

    conn = sqlite3.connect("ecommerce.db")
    cursor = conn.cursor()
    # cursor.execute("""
    #     Drop table if exists sales;
    # """)

    # cursor.execute("""
    #         Drop table if exists lookup_items;
    #      """)    

    # cursor.execute("""
    #          Drop table if exists inventory;
    #      """)
    
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


    conn.execute("""
        CREATE TABLE IF NOT EXISTS lookup_items (
            item TEXT PRIMARY KEY,
            count INTEGER NOT NULL DEFAULT 0,
            price_per_item REAL NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()

    #main_agent.invoke({"messages": [{"role": "user", "content": "I want to add 5 apples of $1.50."}]})


if __name__ == "__main__":
    main()

import sqlite3
import streamlit as st
from agents.Orchastrator import main_agent

if "reg_in" not in st.session_state:
    st.session_state["reg_in"] = False
if "logged_in"  not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["userid"] = ""
    st.session_state["role"] = ""
if "messages"  not in st.session_state:
    st.session_state.messages = {}  # Store chat history per user
if "admin_joined"  not in st.session_state:
    st.session_state.admin_joined = {}
if 'mar' not in st.session_state:
    st.session_state.mar=0
if 'mark' not in st.session_state:
    st.session_state.mark=0
if 'exam' not in st.session_state:
    st.session_state.exam=0
if 'descriptive' not in st.session_state:
    st.session_state.descriptive=0
if 'call' not in st.session_state:
    st.session_state.call=0
if "ms" not in st.session_state:
    st.session_state["ms"] = [{"role": "assistant", "content": "Enter your profession to get course recommendations:"}]

def reg():
    'Already have an Account'
    if st.button('Login Page'):
        st.session_state["reg_in"] = False
        st.session_state["rerun"] = True
        st.rerun()
    new_userid = st.text_input("New Userid")
    new_password = st.text_input("New Password", type="password")
    s=st.text_input("Specialization")
    
        
    if st.button("Register"):
        # convert the mongoDB document to sqlite3 database
        conn = sqlite3.connect("ecommerce.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Users WHERE id = ?", (new_userid,))
        user = cursor.fetchone()
        if user is not None:
            st.warning("The UserID already EXIST.")
        else:
            if new_userid and new_password:
                y={"id":new_userid,"pwd":new_password,"role":'Student',"spec":s,"balance":300}
                cursor.execute("INSERT INTO Users (id, pwd, role) VALUES (?, ?, ?)", (new_userid, new_password, 'Customer'))
                conn.commit()
                st.success('Registered Sucessfully')
            else:
                st.warning("Please enter both userid and password.")
            st.session_state["reg_in"] = False
            st.session_state["rerun"] = True
            st.rerun()

def login():
    st.title("Login Page")
    userid = st.text_input("Userid")
    password = st.text_input("Password", type="password")
    'Create an Account'
    if st.button('Registration form'):
        st.session_state["reg_in"] = True
        st.session_state["rerun"] = True
        st.rerun()

    if st.button("Login"):
            # convert the mongoDB document to sqlite3 database
            conn = sqlite3.connect("ecommerce.db")
            cursor = conn.cursor()
            cursor.execute("""
            SELECT * FROM Users WHERE id = ? AND pwd = ?
            """, (userid, password))
            user = cursor.fetchone()
            conn.close()
            if user is not None: 
                if user[1] == password:  # Assuming pwd is the second column
                    st.session_state["logged_in"] = True
                    st.session_state["userid"] = userid
                    st.session_state["role"] = user[2]  # Assuming role is the third column
                    st.session_state["rerun"] = True
                    st.rerun()  # Refresh to show navigation
                else:
                    st.error("Invalid Password")
            else:
                    st.error("Invalid Userid")

def main():
    print("Hello from ecommercehelper!")
    print("Always write items in Singular form. For example,\n write 'apple' instead of 'apples'.")
    print("Always specify one item at a time. For example,\n write 'I want to add 5 apples of $1.50.' \ninstead of 'I want to add 5 apples of $1.50 and 3 bananas of $0.75.'")
    

    conn = sqlite3.connect("ecommerce.db")
    cursor = conn.cursor()
    cursor.execute("""
        Drop table if exists sales;
    """)

    cursor.execute("""
            Drop table if exists lookup_items;
         """)    

    cursor.execute("""
             Drop table if exists inventory;
         """)
    
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

    conn.execute("""
            CREATE TABLE IF NOT EXISTS Users (
                id TEXT PRIMARY KEY,
                pwd TEXT NOT NULL,
                role TEXT NOT NULL
            )
        """)
    
    
    conn.commit()
    conn.close()

    main_agent.invoke({"messages": [{"role": "user", "content": "I want to add 5 apples of $1.50."}]})

def logout():
    st.session_state["logged_in"] = False
    st.session_state["userid"] = ""
    st.session_state["role"] = ""
    st.session_state["rerun"] = True
    st.rerun()



if __name__ == "__main__":
    main()

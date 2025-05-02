# Importing the required modules
import tkinter as tk
from tkinter import *
from tkinter import messagebox
import sqlite3
from datetime import datetime

# Updated color scheme for shop management theme
MAIN_BG = "#ffffff"
HEADER_BG = "#2c3e50"
HEADER_FG = "#ffffff"
BTN_BG = "#2980b9"
BTN_FG = "#ffffff"
LABEL_FG = "#2c3e50"
SUCCESS_BG = "#27ae60"
DELETE_BG = "#e74c3c"
ENTRY_BG = "#f7f9f9"

BG_COLOR = MAIN_BG
FG_COLOR = LABEL_FG
LABEL_FONT = ("Arial", 10)
ENTRY_FONT = ("Arial", 10)
BTN_FONT = ("Arial", 11)
BTN_WIDTH = 25
STATUS_BG = "#ecf0f1"
STATUS_FG = LABEL_FG
HIGHLIGHT_COLOR = "#dcdde1"

# Connecting to the SQLite database and creating tables
db = sqlite3.connect("shop.db")
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    date TEXT,
    prodName TEXT,
    prodPrice INTEGER,
    stock INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS sale (
    custName TEXT,
    date TEXT,
    prodName TEXT,
    qty INTEGER,
    price INTEGER
)
""")
db.commit()


class ShopManagementSystem:
    def __init__(self):
        self.cart = []
        self.current_window = tk.Tk()
        self.mainMenu()

    def clear_window(self):
        pass

    def mainMenu(self):
        wn = self.current_window
        wn.title("Shop Management System")
        wn.geometry("300x400")
        wn.configure(bg=MAIN_BG)
        Label(wn, text="Shop Management System", font=("Arial", 18), bg=MAIN_BG, fg=LABEL_FG).pack(pady=20)

        Button(wn, text="Admin Section", command=self.adminSection, bg=BTN_BG, fg=BTN_FG, font=BTN_FONT).pack(pady=10)
        Button(wn, text="Customer Section", command=self.customerSection, bg=BTN_BG, fg=BTN_FG, font=BTN_FONT).pack(pady=10)
        Button(wn, text="Exit", command=wn.destroy, bg=DELETE_BG, fg=BTN_FG, font=BTN_FONT).pack(pady=20)

        wn.mainloop()

    # Customer Section Functions
    def addToCart(self):
        pname = self.prodName.get()
        qty = self.prodQty.get()

        if not pname or not qty:
            messagebox.showwarning("Input Error", "All fields are required.")
            return

        try:
            qty = int(qty)
            if qty <= 0:
                messagebox.showwarning("Input Error", "Quantity must be positive.")
                return
        except ValueError:
            messagebox.showerror("Input Error", "Quantity must be a number.")
            return

        try:
            cursor.execute("SELECT prodPrice, stock FROM products WHERE prodName = ?", (pname,))
            result = cursor.fetchone()
            if result:
                price, stock = result
                if qty > stock:
                    messagebox.showwarning("Stock Error", f"Only {stock} items available.")
                else:
                    self.cart.append((pname, qty, price * qty))
                    new_stock = stock - qty
                    cursor.execute("UPDATE products SET stock = ? WHERE prodName = ?", (new_stock, pname))
                    db.commit()
                    messagebox.showinfo("Success", f"{qty} x {pname} added to cart.")
                    self.prodName.delete(0, END)
                    self.prodQty.delete(0, END)
            else:
                messagebox.showwarning("Not Found", "Product not found.")
        except Exception as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")

    def deleteFromCart(self):
        pname = self.prodName.get()
        qty = self.prodQty.get()

        if not pname or not qty:
            messagebox.showwarning("Input Error", "Both Product Name and Quantity are required.")
            return

        try:
            qty = int(qty)
            if qty <= 0:
                messagebox.showwarning("Input Error", "Quantity must be positive.")
                return
        except ValueError:
            messagebox.showerror("Input Error", "Quantity must be a number.")
            return

        for item in self.cart:
            if item[0] == pname:
                if qty > item[1]:
                    messagebox.showwarning("Quantity Error", "Cannot remove more than present in the cart.")
                    return

                # Remove or update quantity in the cart
                self.cart.remove(item)
                cursor.execute("SELECT stock FROM products WHERE prodName = ?", (pname,))
                result = cursor.fetchone()
                if result:
                    updated_stock = result[0] + qty
                    cursor.execute("UPDATE products SET stock = ? WHERE prodName = ?", (updated_stock, pname))
                    db.commit()

                    # Adjust remaining quantity if any
                    remaining_qty = item[1] - qty
                    if remaining_qty > 0:
                        self.cart.append((pname, remaining_qty, remaining_qty * item[2] // item[1]))
                    messagebox.showinfo("Success", f"{qty} x {pname} removed from the cart.")
                    self.prodName.delete(0, END)
                    self.prodQty.delete(0, END)
                    return

        messagebox.showwarning("Not Found", "Product not found in the cart.")

    def viewCart(self):
        wn = tk.Toplevel(self.current_window)
        wn.title("View Cart")
        wn.geometry("400x400")
        wn.configure(bg=MAIN_BG)

        header_frame = Frame(wn, bg=HEADER_BG, padx=10, pady=10, width=400)
        header_frame.pack(fill=X)
        Label(header_frame, text="Your Cart", font=("Arial", 16, "bold"), bg=HEADER_BG, fg=HEADER_FG).pack(pady=10)

        content_frame = Frame(wn, bg=MAIN_BG, padx=20, pady=20)
        content_frame.pack(fill=BOTH, expand=True)

        total = 0
        if self.cart:
            for i, item in enumerate(self.cart):
                bg_color = "#f9f9f9" if i % 2 == 0 else "#f0f0f0"
                item_frame = Frame(content_frame, bg=bg_color, padx=10, pady=5, width=380)
                item_frame.pack(fill=X, pady=2)
                Label(item_frame, text=f"Name: {item[0]}", bg=bg_color, fg=LABEL_FG, width=15, anchor="w").pack(side=LEFT)
                Label(item_frame, text=f"Qty: {item[1]}", bg=bg_color, fg=LABEL_FG, width=8, anchor="w").pack(side=LEFT)
                Label(item_frame, text=f"Price: ${item[2]}", bg=bg_color, fg=LABEL_FG, width=10, anchor="w").pack(side=LEFT)
                total += item[2]
        else:
            Label(content_frame, text="Your cart is empty", bg=MAIN_BG, fg=LABEL_FG, font=("Arial", 12)).pack(pady=20)

        total_frame = Frame(wn, bg="#e8f8f5", padx=10, pady=10, relief=RIDGE, bd=1)
        total_frame.pack(fill=X, padx=20, pady=10)
        Label(total_frame, text=f"Total: ${total}", font=("Arial", 14, "bold"), bg="#e8f8f5", fg="#16a085").pack(pady=5)
        
        Button(wn, text="Close", command=wn.destroy, bg=BTN_BG, fg=BTN_FG, padx=20, pady=5).pack(pady=15)

    def generateBill(self):
        if not self.cart:
            messagebox.showwarning("Empty Cart", "Your cart is empty. Add items before generating bill.")
            return

        wn = tk.Toplevel(self.current_window)
        wn.title("Bill")
        wn.geometry("400x500")
        wn.configure(bg=MAIN_BG)

        header_frame = Frame(wn, bg=HEADER_BG, padx=10, pady=10, width=400)
        header_frame.pack(fill=X)
        Label(header_frame, text="Final Bill", font=("Arial", 16, "bold"), bg=HEADER_BG, fg=HEADER_FG).pack(pady=10)

        content_frame = Frame(wn, bg=MAIN_BG, padx=20, pady=20)
        content_frame.pack(fill=BOTH, expand=True)

        # Add a thank you message and receipt header
        Label(content_frame, text="Thank You for Shopping With Us!", font=("Arial", 12, "italic"), 
              bg=MAIN_BG, fg="#2980b9").pack(pady=10)
        
        receipt_frame = Frame(content_frame, bg="#fafafa", relief=RIDGE, bd=1)
        receipt_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Add receipt headers
        headers_frame = Frame(receipt_frame, bg="#f0f0f0", padx=5, pady=5)
        headers_frame.pack(fill=X)
        Label(headers_frame, text="Product", font=("Arial", 10, "bold"), bg="#f0f0f0", fg=LABEL_FG, width=15, anchor="w").pack(side=LEFT)
        Label(headers_frame, text="Quantity", font=("Arial", 10, "bold"), bg="#f0f0f0", fg=LABEL_FG, width=8, anchor="w").pack(side=LEFT)
        Label(headers_frame, text="Price", font=("Arial", 10, "bold"), bg="#f0f0f0", fg=LABEL_FG, width=10, anchor="w").pack(side=LEFT)

        # Items frame
        items_frame = Frame(receipt_frame, bg="#fafafa", padx=5, pady=5)
        items_frame.pack(fill=BOTH, expand=True)

        total = 0
        current_date = datetime.now().strftime("%Y-%m-%d")
        for i, item in enumerate(self.cart):
            bg_color = "#ffffff" if i % 2 == 0 else "#f9f9f9"
            item_frame = Frame(items_frame, bg=bg_color, padx=5, pady=5)
            item_frame.pack(fill=X)
            Label(item_frame, text=f"{item[0]}", bg=bg_color, fg=LABEL_FG, width=15, anchor="w").pack(side=LEFT)
            Label(item_frame, text=f"{item[1]}", bg=bg_color, fg=LABEL_FG, width=8, anchor="w").pack(side=LEFT)
            Label(item_frame, text=f"${item[2]}", bg=bg_color, fg=LABEL_FG, width=10, anchor="w").pack(side=LEFT)
            total += item[2]
            
            # Record the sale in database
            cursor.execute("INSERT INTO sale (custName, date, prodName, qty, price) VALUES (?, ?, ?, ?, ?)",
                          ("Customer", current_date, item[0], item[1], item[2]))
            db.commit()

        # Divider line
        Frame(receipt_frame, height=1, bg="#ddd").pack(fill=X, padx=5, pady=5)

        # Total amount
        total_frame = Frame(receipt_frame, bg="#f0f0f0", padx=5, pady=8)
        total_frame.pack(fill=X)
        Label(total_frame, text="", width=15, bg="#f0f0f0").pack(side=LEFT)
        Label(total_frame, text="Total:", font=("Arial", 10, "bold"), bg="#f0f0f0", fg=LABEL_FG, width=8, anchor="w").pack(side=LEFT)
        Label(total_frame, text=f"${total}", font=("Arial", 10, "bold"), bg="#f0f0f0", fg="#e74c3c", width=10, anchor="w").pack(side=LEFT)

        # Clear the cart after generating bill
        self.cart = []
        
        Button(wn, text="Close", command=wn.destroy, bg=BTN_BG, fg=BTN_FG, padx=20, pady=5).pack(pady=15)

    def customerSection(self):
        self.clear_window()
        self.current_window = tk.Tk()
        wn = self.current_window
        wn.title("Customer Section")
        wn.geometry("400x500")
        wn.configure(bg=MAIN_BG)

        header_frame = Frame(wn, bg=HEADER_BG, padx=10, pady=10, width=400)
        header_frame.pack(fill=X)
        Label(header_frame, text="Customer Section", font=("Arial", 16, "bold"), bg=HEADER_BG, fg=HEADER_FG).pack(pady=10)

        content_frame = Frame(wn, bg=MAIN_BG, padx=20, pady=20)
        content_frame.pack(fill=BOTH, expand=True)

        # Product Name Input
        Label(content_frame, text="Product Name", bg=MAIN_BG, fg=LABEL_FG, font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 2))
        self.prodName = Entry(content_frame, bg=ENTRY_BG, fg=LABEL_FG, width=30)
        self.prodName.pack(fill=X, pady=(0, 10))

        # Quantity Input
        Label(content_frame, text="Quantity", bg=MAIN_BG, fg=LABEL_FG, font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 2))
        self.prodQty = Entry(content_frame, bg=ENTRY_BG, fg=LABEL_FG, width=30)
        self.prodQty.pack(fill=X, pady=(0, 20))

        # Buttons
        buttons_frame = Frame(content_frame, bg=MAIN_BG)
        buttons_frame.pack(fill=X, pady=10)
        
        btn_add = Button(buttons_frame, text="Add to Cart", command=self.addToCart, bg=SUCCESS_BG, fg=BTN_FG, padx=15, pady=8)
        btn_add.pack(fill=X, pady=5)
        
        btn_delete = Button(buttons_frame, text="Delete from Cart", command=self.deleteFromCart, bg=DELETE_BG, fg=BTN_FG, padx=15, pady=8)
        btn_delete.pack(fill=X, pady=5)
        
        btn_view = Button(buttons_frame, text="View Cart", command=self.viewCart, bg=BTN_BG, fg=BTN_FG, padx=15, pady=8)
        btn_view.pack(fill=X, pady=5)
        
        btn_bill = Button(buttons_frame, text="Generate Bill", command=self.generateBill, bg=BTN_BG, fg=BTN_FG, padx=15, pady=8)
        btn_bill.pack(fill=X, pady=5)

        wn.mainloop()

    # Admin Section Functions
    def prodtoTable(self):
        pname = self.prodName.get()
        price = self.prodPrice.get()
        stock = self.prodStock.get()
        dt = self.date.get()

        if not pname or not price or not stock or not dt:
            messagebox.showwarning("Input Error", "All fields are required.")
            return

        try:
            price = int(price)
            stock = int(stock)
            if price <= 0 or stock < 0:
                messagebox.showwarning("Input Error", "Price must be positive and stock cannot be negative.")
                return
        except ValueError:
            messagebox.showerror("Input Error", "Product price and stock must be numbers.")
            return

        try:
            cursor.execute(
                "INSERT INTO products (date, prodName, prodPrice, stock) VALUES (?, ?, ?, ?)",
                (dt, pname, price, stock),
            )
            db.commit()
            messagebox.showinfo('Success', "Product added successfully.")
            self.window.destroy()
        except Exception as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")

    def removeProd(self):
        name = self.prodName.get().strip().lower()

        if not name:
            messagebox.showwarning("Input Error", "Product name is required.")
            return

        try:
            cursor.execute("DELETE FROM products WHERE LOWER(prodName) = ?", (name,))
            db.commit()
            if cursor.rowcount > 0:
                messagebox.showinfo("Success", "Product deleted successfully.")
            else:
                messagebox.showwarning("Not Found", "No such product found.")
            self.window.destroy()
        except Exception as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")

    def updateProduct(self):
        old_name = self.oldProdName.get().strip().lower()
        new_name = self.newProdName.get()
        new_price = self.newProdPrice.get()
        new_stock = self.newProdStock.get()

        if not old_name or not new_name or not new_price or not new_stock:
            messagebox.showwarning("Input Error", "All fields are required.")
            return

        try:
            new_price = int(new_price)
            new_stock = int(new_stock)
            if new_price <= 0 or new_stock < 0:
                messagebox.showwarning("Input Error", "Price must be positive and stock cannot be negative.")
                return
        except ValueError:
            messagebox.showerror("Input Error", "Product price and stock must be numbers.")
            return

        try:
            cursor.execute(
                "UPDATE products SET prodName = ?, prodPrice = ?, stock = ? WHERE LOWER(prodName) = ?",
                (new_name, new_price, new_stock, old_name),
            )
            db.commit()
            if cursor.rowcount > 0:
                messagebox.showinfo("Success", "Product updated successfully.")
            else:
                messagebox.showwarning("Not Found", "No such product found.")
            self.window.destroy()
        except Exception as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")

    def viewProducts(self):
        wn = tk.Toplevel(self.current_window)
        wn.title("View Products")
        wn.geometry("600x500")
        wn.configure(bg=MAIN_BG)

        header_frame = Frame(wn, bg=HEADER_BG, padx=10, pady=10, width=600)
        header_frame.pack(fill=X)
        Label(header_frame, text="Products in Database", font=("Arial", 16, "bold"), bg=HEADER_BG, fg=HEADER_FG).pack(pady=10)

        # Create a scrollable frame for products
        canvas = Canvas(wn, bg=MAIN_BG)
        scrollbar = Scrollbar(wn, orient="vertical", command=canvas.yview)
        scrollable_frame = Frame(canvas, bg=MAIN_BG)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)

        # Table header frame
        header_row = Frame(scrollable_frame, bg="#34495e", padx=5, pady=8, width=580)
        header_row.pack(fill=X, pady=(0, 2))
        
        Label(header_row, text="Date", font=("Arial", 10, "bold"), bg="#34495e", fg=HEADER_FG, width=15).pack(side=LEFT, padx=2)
        Label(header_row, text="Name", font=("Arial", 10, "bold"), bg="#34495e", fg=HEADER_FG, width=20).pack(side=LEFT, padx=2)
        Label(header_row, text="Price", font=("Arial", 10, "bold"), bg="#34495e", fg=HEADER_FG, width=10).pack(side=LEFT, padx=2)
        Label(header_row, text="Stock", font=("Arial", 10, "bold"), bg="#34495e", fg=HEADER_FG, width=10).pack(side=LEFT, padx=2)

        try:
            cursor.execute("SELECT * FROM products")
            records = cursor.fetchall()
            if records:
                for i, record in enumerate(records):
                    bg_color = "#ffffff" if i % 2 == 0 else "#f5f5f5"
                    row_frame = Frame(scrollable_frame, bg=bg_color, padx=5, pady=5, width=580)
                    row_frame.pack(fill=X, pady=1)
                    
                    Label(row_frame, text=record[0], bg=bg_color, fg=LABEL_FG, width=15).pack(side=LEFT, padx=2)
                    Label(row_frame, text=record[1], bg=bg_color, fg=LABEL_FG, width=20).pack(side=LEFT, padx=2)
                    Label(row_frame, text=f"${record[2]}", bg=bg_color, fg=LABEL_FG, width=10).pack(side=LEFT, padx=2)
                    
                    # Color the stock label based on stock level
                    stock_label = Label(row_frame, text=record[3], width=10)
                    if record[3] < 5:
                        stock_label.configure(bg=bg_color, fg="#c0392b")  # Red for low stock
                    elif record[3] < 20:
                        stock_label.configure(bg=bg_color, fg="#d35400")  # Orange for medium stock
                    else:
                        stock_label.configure(bg=bg_color, fg="#27ae60")  # Green for high stock
                    stock_label.pack(side=LEFT, padx=2)
                    
            else:
                no_prod_frame = Frame(scrollable_frame, bg=MAIN_BG, padx=10, pady=30, width=580)
                no_prod_frame.pack(fill=X)
                Label(no_prod_frame, text="No products found.", bg=MAIN_BG, fg=LABEL_FG, font=("Arial", 12)).pack()
        except Exception as e:
            error_frame = Frame(scrollable_frame, bg=MAIN_BG, padx=10, pady=30, width=580)
            error_frame.pack(fill=X)
            Label(error_frame, text=f"An error occurred: {e}", bg=MAIN_BG, fg="#c0392b", font=("Arial", 12)).pack()

        Button(wn, text="Close", command=wn.destroy, bg=BTN_BG, fg=BTN_FG, padx=20, pady=8).pack(pady=15)

    def addProd(self):
        self.window = tk.Toplevel(self.current_window)
        wn = self.window
        wn.title("Add Product")
        wn.geometry("400x400")
        wn.configure(bg=MAIN_BG)

        header_frame = Frame(wn, bg=HEADER_BG, padx=10, pady=10, width=400)
        header_frame.pack(fill=X)
        Label(header_frame, text="Add Product", font=("Arial", 16, "bold"), bg=HEADER_BG, fg=HEADER_FG).pack(pady=10)

        content_frame = Frame(wn, bg=MAIN_BG, padx=20, pady=20)
        content_frame.pack(fill=BOTH, expand=True)

        Label(content_frame, text="Date (YYYY-MM-DD)", bg=MAIN_BG, fg=LABEL_FG, font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 2))
        self.date = Entry(content_frame, bg=ENTRY_BG, fg=LABEL_FG, width=30)
        self.date.pack(fill=X, pady=(0, 10))
        self.date.insert(0, datetime.now().strftime("%Y-%m-%d"))

        Label(content_frame, text="Product Name", bg=MAIN_BG, fg=LABEL_FG, font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 2))
        self.prodName = Entry(content_frame, bg=ENTRY_BG, fg=LABEL_FG, width=30)
        self.prodName.pack(fill=X, pady=(0, 10))

        Label(content_frame, text="Product Price", bg=MAIN_BG, fg=LABEL_FG, font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 2))
        self.prodPrice = Entry(content_frame, bg=ENTRY_BG, fg=LABEL_FG, width=30)
        self.prodPrice.pack(fill=X, pady=(0, 10))

        Label(content_frame, text="Product Stock", bg=MAIN_BG, fg=LABEL_FG, font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 2))
        self.prodStock = Entry(content_frame, bg=ENTRY_BG, fg=LABEL_FG, width=30)
        self.prodStock.pack(fill=X, pady=(0, 10))

        buttons_frame = Frame(content_frame, bg=MAIN_BG, pady=10)
        buttons_frame.pack(fill=X)
        
        Button(buttons_frame, text="Add Product", command=self.prodtoTable, bg=SUCCESS_BG, fg=BTN_FG, padx=15, pady=8).pack(fill=X, pady=5)
        Button(buttons_frame, text="Cancel", command=wn.destroy, bg="#7f8c8d", fg=BTN_FG, padx=15, pady=8).pack(fill=X, pady=5)

    def delProd(self):
        self.window = tk.Toplevel(self.current_window)
        wn = self.window
        wn.title("Delete Product")
        wn.geometry("400x300")
        wn.configure(bg=MAIN_BG)

        header_frame = Frame(wn, bg=HEADER_BG, padx=10, pady=10, width=400)
        header_frame.pack(fill=X)
        Label(header_frame, text="Delete Product", font=("Arial", 16, "bold"), bg=HEADER_BG, fg=HEADER_FG).pack(pady=10)

        content_frame = Frame(wn, bg=MAIN_BG, padx=20, pady=20)
        content_frame.pack(fill=BOTH, expand=True)

        Label(content_frame, text="Product Name", bg=MAIN_BG, fg=LABEL_FG, font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 2))
        self.prodName = Entry(content_frame, bg=ENTRY_BG, fg=LABEL_FG, width=30)
        self.prodName.pack(fill=X, pady=(0, 20))

        warning_label = Label(content_frame, text="Warning: This action cannot be undone!", bg=MAIN_BG, fg="#c0392b", font=("Arial", 10, "italic"))
        warning_label.pack(pady=10)

        buttons_frame = Frame(content_frame, bg=MAIN_BG, pady=10)
        buttons_frame.pack(fill=X)
        
        Button(buttons_frame, text="Delete Product", command=self.removeProd, bg=DELETE_BG, fg=BTN_FG, padx=15, pady=8).pack(fill=X, pady=5)
        Button(buttons_frame, text="Cancel", command=wn.destroy, bg="#7f8c8d", fg=BTN_FG, padx=15, pady=8).pack(fill=X, pady=5)

    def updProd(self):
        self.window = tk.Toplevel(self.current_window)
        wn = self.window
        wn.title("Update Product")
        wn.geometry("400x450")
        wn.configure(bg=MAIN_BG)

        header_frame = Frame(wn, bg=HEADER_BG, padx=10, pady=10, width=400)
        header_frame.pack(fill=X)
        Label(header_frame, text="Update Product", font=("Arial", 16, "bold"), bg=HEADER_BG, fg=HEADER_FG).pack(pady=10)

        content_frame = Frame(wn, bg=MAIN_BG, padx=20, pady=20)
        content_frame.pack(fill=BOTH, expand=True)

        Label(content_frame, text="Old Product Name", bg=MAIN_BG, fg=LABEL_FG, font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 2))
        self.oldProdName = Entry(content_frame, bg=ENTRY_BG, fg=LABEL_FG, width=30)
        self.oldProdName.pack(fill=X, pady=(0, 15))

        # Separator line
        Frame(content_frame, height=1, bg="#bdc3c7").pack(fill=X, pady=10)

        Label(content_frame, text="New Product Name", bg=MAIN_BG, fg=LABEL_FG, font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 2))
        self.newProdName = Entry(content_frame, bg=ENTRY_BG, fg=LABEL_FG, width=30)
        self.newProdName.pack(fill=X, pady=(0, 10))

        Label(content_frame, text="New Product Price", bg=MAIN_BG, fg=LABEL_FG, font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 2))
        self.newProdPrice = Entry(content_frame, bg=ENTRY_BG, fg=LABEL_FG, width=30)
        self.newProdPrice.pack(fill=X, pady=(0, 10))

        Label(content_frame, text="New Product Stock", bg=MAIN_BG, fg=LABEL_FG, font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 2))
        self.newProdStock = Entry(content_frame, bg=ENTRY_BG, fg=LABEL_FG, width=30)
        self.newProdStock.pack(fill=X, pady=(0, 15))

        buttons_frame = Frame(content_frame, bg=MAIN_BG, pady=10)
        buttons_frame.pack(fill=X)
        
        Button(buttons_frame, text="Update Product", command=self.updateProduct, bg=BTN_BG, fg=BTN_FG, padx=15, pady=8).pack(fill=X, pady=5)
        Button(buttons_frame, text="Cancel", command=wn.destroy, bg="#7f8c8d", fg=BTN_FG, padx=15, pady=8).pack(fill=X, pady=5)

    def adminSection(self):
        self.clear_window()
        self.current_window = tk.Tk()
        wn = self.current_window
        wn.title("Admin Section")
        wn.geometry("400x450")
        wn.configure(bg=MAIN_BG)

        header_frame = Frame(wn, bg=HEADER_BG, padx=10, pady=10, width=400)
        header_frame.pack(fill=X)
        Label(header_frame, text="Admin Section", font=("Arial", 16, "bold"), bg=HEADER_BG, fg=HEADER_FG).pack(pady=10)

        content_frame = Frame(wn, bg=MAIN_BG, padx=30, pady=30)
        content_frame.pack(fill=BOTH, expand=True)
        
        Label(content_frame, text="Select an Option", bg=MAIN_BG, fg=LABEL_FG, font=("Arial", 12, "bold")).pack(pady=(0, 20))

        # Button styles with icons (using text characters as icons)
        Button(content_frame, text="➕ Add Product", command=self.addProd, bg=SUCCESS_BG, fg=BTN_FG, 
               font=("Arial", 11), padx=20, pady=12, width=25).pack(pady=10)
               
        Button(content_frame, text="❌ Delete Product", command=self.delProd, bg=DELETE_BG, fg=BTN_FG, 
               font=("Arial", 11), padx=20, pady=12, width=25).pack(pady=10)
               
        Button(content_frame, text="🔄 Update Product", command=self.updProd, bg=BTN_BG, fg=BTN_FG, 
               font=("Arial", 11), padx=20, pady=12, width=25).pack(pady=10)
               
        Button(content_frame, text="📋 View Products", command=self.viewProducts, bg=BTN_BG, fg=BTN_FG, 
               font=("Arial", 11), padx=20, pady=12, width=25).pack(pady=10)
               
        Button(content_frame, text="🔙 Back to Main Menu", command=self.mainMenu, bg="#7f8c8d", fg=BTN_FG, 
               font=("Arial", 11), padx=20, pady=12, width=25).pack(pady=10)

        wn.mainloop()

# Start the application
if __name__ == "__main__":
    app = ShopManagementSystem()
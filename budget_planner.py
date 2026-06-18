"""
Cute Budget Planner - Main Application
A fun and engaging budget management tool!
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime, timedelta
from tkinter import font as tkfont
import calendar
import random
import math

class BudgetPlannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("💰 Cute Budget Planner 💰")
        self.root.geometry("1000x750")
        
        # Data file
        self.data_file = "budget_data.json"
        self.data = self.load_data()
        
        # Currency symbols
        self.currencies = {
            'TND': {'symbol': 'د.ت', 'name': 'Tunisian Dinar'},
            'USD': {'symbol': '$', 'name': 'US Dollar'},
            'EUR': {'symbol': '€', 'name': 'Euro'}
        }
        
        # Get saved currency or default to USD
        self.current_currency = self.data.get('currency', 'USD')
        
        # Load theme settings
        self.load_theme()
        
        # Apply background color to root
        self.root.configure(bg=self.colors['bg'])
        self.root.minsize(900, 650)
        self.active_scroll_canvas = None
        
        # Setup fonts - softer, more readable
        self.title_font = tkfont.Font(family="Segoe UI", size=22, weight="bold")
        self.heading_font = tkfont.Font(family="Segoe UI", size=15, weight="bold")
        self.normal_font = tkfont.Font(family="Segoe UI", size=11)
        self.small_font = tkfont.Font(family="Segoe UI", size=9)
        self.setup_styles()
        self.root.bind_all("<MouseWheel>", self.on_mousewheel, add="+")
        self.root.bind_all("<Button-4>", self.on_mousewheel, add="+")
        self.root.bind_all("<Button-5>", self.on_mousewheel, add="+")
        
        # Pet animation variables
        self.pet_x = 100
        self.pet_y = 100
        self.pet_dx = 2
        self.pet_dy = 2
        self.pet_frame = 0
        
        # Check for automatic salary addition and recurring expenses before showing UI
        if self.data and 'setup_complete' in self.data:
            self.check_and_add_salary()
            self.process_recurring_expenses()
        
        # Check if first run
        if not self.data or 'setup_complete' not in self.data:
            self.show_welcome_screen()
        else:
            self.show_main_dashboard()
    
    def process_recurring_expenses(self):
        """Process recurring expenses monthly after salary"""
        if 'recurring_expenses' not in self.data:
            self.data['recurring_expenses'] = []
            return
        
        today = datetime.now()
        last_processed = self.data.get('last_recurring_processed')
        
        if not last_processed:
            self.data['last_recurring_processed'] = today.strftime('%Y-%m-%d')
            self.save_data()
            return
        
        last_date = datetime.strptime(last_processed, '%Y-%m-%d')
        
        # Process if in new month
        if last_date.month != today.month or last_date.year != today.year:
            for recurring in self.data['recurring_expenses']:
                # Add to regular expenses
                expense = {
                    'description': recurring['description'] + ' (Auto)',
                    'amount': recurring['amount'],
                    'category': recurring['category'],
                    'date': today.strftime('%Y-%m-%d'),
                    'notes': 'Recurring expense - auto-added',
                    'is_recurring': True
                }
                
                if 'expenses' not in self.data:
                    self.data['expenses'] = []
                self.data['expenses'].append(expense)
            
            self.data['last_recurring_processed'] = today.strftime('%Y-%m-%d')
            self.save_data()
            
            if self.data['recurring_expenses']:
                messagebox.showinfo(
                    "💸 Recurring Expenses Added",
                    f"{len(self.data['recurring_expenses'])} recurring expense(s) have been automatically added for this month!"
                )
    
    def load_theme(self):
        """Load color theme from saved data - with SOFTER, more pleasant colors"""
        theme_name = self.data.get('theme', 'default')
        
        self.themes = {
            'default': {
                'primary': '#EF476F',      # Modern rose
                'secondary': '#7C3AED',    # Violet accent
                'success': '#06A77D',      # Clean green
                'info': '#2563EB',         # Strong blue
                'bg': '#F4F7FB',           # Soft app background
                'card': '#FFFFFF',         # White
                'text': '#1F2937',         # Dark slate
                'light_text': '#6B7280'    # Muted gray
            },
            'purple_dream': {
                'primary': '#7C3AED',      # Purple
                'secondary': '#DB2777',    # Pink
                'success': '#0D9488',      # Teal
                'info': '#4F46E5',         # Indigo
                'bg': '#F6F3FF',           # Light lavender
                'card': '#FFFFFF',
                'text': '#27272A',
                'light_text': '#71717A'
            },
            'ocean_breeze': {
                'primary': '#0284C7',      # Ocean blue
                'secondary': '#0891B2',    # Cyan
                'success': '#059669',      # Green
                'info': '#2563EB',         # Blue
                'bg': '#EFF8FB',           # Light cyan
                'card': '#FFFFFF',
                'text': '#164E63',
                'light_text': '#64748B'
            },
            'sunset_glow': {
                'primary': '#E11D48',      # Warm rose
                'secondary': '#EA580C',    # Orange
                'success': '#16A34A',      # Green
                'info': '#DC2626',         # Red
                'bg': '#FFF7ED',           # Light orange
                'card': '#FFFFFF',
                'text': '#431407',
                'light_text': '#78716C'
            },
            'forest_zen': {
                'primary': '#15803D',      # Forest green
                'secondary': '#4D7C0F',    # Olive
                'success': '#059669',      # Emerald
                'info': '#0F766E',         # Teal
                'bg': '#F3FAF4',           # Light green
                'card': '#FFFFFF',
                'text': '#14532D',
                'light_text': '#64748B'
            }
        }

        for theme in self.themes.values():
            theme.setdefault('shadow', '#DCE4EC')
            theme.setdefault('button_hover', theme['text'])
        
        self.colors = self.themes.get(theme_name, self.themes['default'])
        self.current_theme = theme_name
    
    def check_and_add_salary(self):
        """Check if salary should be added since last app open"""
        if 'regular_incomes' not in self.data or not self.data['regular_incomes']:
            return
        
        today = datetime.now()
        last_open = self.data.get('last_app_open')
        
        # Update last open date
        self.data['last_app_open'] = today.strftime('%Y-%m-%d')
        
        if not last_open:
            self.save_data()
            return
        
        last_open_date = datetime.strptime(last_open, '%Y-%m-%d')
        
        # Check each regular income
        for income in self.data['regular_incomes']:
            self.check_salary_payment(income, last_open_date, today)
        
        self.save_data()
    
    def check_salary_payment(self, income, last_open, today):
        """Check if a salary payment should be added"""
        frequency = income.get('frequency', 'Monthly')
        payment_day = income.get('payment_day', '1')
        last_payment = income.get('last_payment')
        
        if not last_payment:
            return
        
        last_payment_date = datetime.strptime(last_payment, '%Y-%m-%d')
        
        # Calculate next payment date
        if frequency == 'Weekly':
            next_payment = last_payment_date + timedelta(days=7)
        elif frequency == 'Bi-weekly':
            next_payment = last_payment_date + timedelta(days=14)
        elif frequency == 'Monthly':
            # Add one month
            if last_payment_date.month == 12:
                next_payment = last_payment_date.replace(year=last_payment_date.year + 1, month=1)
            else:
                next_payment = last_payment_date.replace(month=last_payment_date.month + 1)
        elif frequency == 'Yearly':
            next_payment = last_payment_date.replace(year=last_payment_date.year + 1)
        else:
            return
        
        # If next payment date is between last open and today, add salary
        if last_open < next_payment <= today:
            income['current_left'] += income['amount']
            income['last_payment'] = today.strftime('%Y-%m-%d')
            
            # Show notification
            messagebox.showinfo(
                "💰 Salary Added!",
                f"Your {income['name']} of {self.format_currency(income['amount'])} has been added!\n\n"
                f"Payment date: {next_payment.strftime('%B %d, %Y')}"
            )
    
    def format_currency(self, amount):
        """Format amount with current currency symbol"""
        symbol = self.currencies[self.current_currency]['symbol']
        if self.current_currency == 'TND':
            return f"{amount:.3f} {symbol}"
        else:
            return f"{symbol}{amount:.2f}"
    
    def load_data(self):
        """Load budget data from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_data(self):
        """Save budget data to JSON file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=4)
    
    def clear_window(self):
        """Clear all widgets from window"""
        self.active_scroll_canvas = None
        for widget in self.root.winfo_children():
            widget.destroy()

    def setup_styles(self):
        """Apply app-wide ttk styling."""
        self.root.option_add("*Font", self.normal_font)
        self.root.option_add("*Entry.Font", self.normal_font)
        self.root.option_add("*Entry.Background", "#FFFFFF")
        self.root.option_add("*Entry.Foreground", self.colors['text'])
        self.root.option_add("*Entry.InsertBackground", self.colors['primary'])
        self.root.option_add("*Entry.Relief", tk.FLAT)
        self.root.option_add("*Entry.HighlightThickness", 1)
        self.root.option_add("*Entry.HighlightBackground", self.colors['shadow'])
        self.root.option_add("*Entry.HighlightColor", self.colors['primary'])
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except tk.TclError:
            pass
        style.configure(
            "Vertical.TScrollbar",
            gripcount=0,
            background=self.colors['primary'],
            darkcolor=self.colors['primary'],
            lightcolor=self.colors['primary'],
            troughcolor=self.colors['bg'],
            bordercolor=self.colors['bg'],
            arrowcolor='white',
            relief=tk.FLAT,
            width=14
        )
        style.map(
            "Vertical.TScrollbar",
            background=[('active', self.colors['info'])]
        )
    
    def create_card(self, parent, bg_color='#FFFFFF'):
        """Create a modern card-like frame."""
        card = tk.Frame(
            parent,
            bg=bg_color,
            relief=tk.FLAT,
            bd=0,
            highlightthickness=1,
            highlightbackground=self.colors['shadow'],
            highlightcolor=self.colors['shadow']
        )
        return card
    
    def create_button(self, parent, text, command, color='primary', width=15):
        """Create a styled button with consistent hover behavior."""
        bg_color = self.colors.get(color, color)
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg_color,
            fg='white',
            font=self.normal_font,
            relief=tk.FLAT,
            padx=22,
            pady=10,
            width=width,
            cursor='hand2',
            activebackground=bg_color,
            activeforeground='white',
            bd=0,
            highlightthickness=0,
            takefocus=True
        )
        btn.bind("<Enter>", lambda e, b=btn: b.configure(bg=self.colors['button_hover']))
        btn.bind("<Leave>", lambda e, b=btn, c=bg_color: b.configure(bg=c))
        return btn

    def create_scrollable_frame(self, parent, fill_width=True):
        """Create a scrollable content frame with mouse-wheel support."""
        canvas = tk.Canvas(parent, bg=self.colors['bg'], highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        content = tk.Frame(canvas, bg=self.colors['bg'])
        window_id = canvas.create_window((0, 0), window=content, anchor="nw")

        def update_scroll_region(_event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
            if fill_width:
                canvas.itemconfigure(window_id, width=canvas.winfo_width())

        content.bind("<Configure>", update_scroll_region)
        canvas.bind("<Configure>", update_scroll_region)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind("<Enter>", lambda _e: self.set_active_scroll_canvas(canvas))
        content.bind("<Enter>", lambda _e: self.set_active_scroll_canvas(canvas))
        self.active_scroll_canvas = canvas
        return canvas, scrollbar, content

    def set_active_scroll_canvas(self, canvas):
        if canvas.winfo_exists():
            self.active_scroll_canvas = canvas

    def on_mousewheel(self, event):
        canvas = self.active_scroll_canvas
        if not canvas or not canvas.winfo_exists():
            return
        event_num = getattr(event, 'num', None)
        if event_num == 4:
            delta = -3
        elif event_num == 5:
            delta = 3
        else:
            delta = -1 * int(event.delta / 120) if event.delta else 0
        if delta:
            canvas.yview_scroll(delta, "units")
    
    def show_welcome_screen(self):
        """Show welcome/setup screen"""
        self.clear_window()
        
        # Create a centered container
        container = tk.Frame(self.root, bg=self.colors['bg'])
        container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Add animated pet
        self.add_welcome_pet(self.root)
        
        # Welcome message
        welcome_label = tk.Label(
            container,
            text="🌟 Welcome to Your Budget Planner! 🌟",
            font=self.title_font,
            bg=self.colors['bg'],
            fg=self.colors['primary']
        )
        welcome_label.pack(pady=20)
        
        subtitle = tk.Label(
            container,
            text="Let's set up your financial journey together! 💪",
            font=self.heading_font,
            bg=self.colors['bg'],
            fg=self.colors['text']
        )
        subtitle.pack(pady=10)
        
        # Info card (centered)
        info_card = self.create_card(container)
        info_card.pack(pady=20)
        
        info_text = tk.Label(
            info_card,
            text="We'll help you:\n\n"
                 "💵 Track your income sources\n"
                 "💰 Manage your expenses\n"
                 "🎯 Reach your savings goals\n"
                 "📊 Visualize your progress\n\n"
                 "Ready to take control of your finances?",
            font=self.normal_font,
            bg='white',
            fg=self.colors['text'],
            justify=tk.CENTER,
            padx=50,
            pady=30
        )
        info_text.pack()
        
        # Start button (centered)
        start_btn = self.create_button(
            container,
            "🚀 Let's Get Started!",
            self.show_currency_selection,
            width=20
        )
        start_btn.pack(pady=20)
    
    def show_currency_selection(self):
        """Show currency selection screen"""
        self.clear_window()
        
        # Centered container
        container = tk.Frame(self.root, bg=self.colors['bg'])
        container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        tk.Label(
            container,
            text="💱 Choose Your Currency",
            font=self.title_font,
            bg=self.colors['bg'],
            fg=self.colors['primary']
        ).pack(pady=30)
        
        # Currency selection card
        currency_card = self.create_card(container)
        currency_card.pack(pady=20, padx=40)
        
        tk.Label(
            currency_card,
            text="Select the currency you'll use:",
            font=self.heading_font,
            bg='white',
            fg=self.colors['text']
        ).pack(pady=20)
        
        currency_var = tk.StringVar(value=self.current_currency)
        
        for code, info in self.currencies.items():
            currency_frame = tk.Frame(currency_card, bg='white')
            currency_frame.pack(pady=10, padx=40)
            
            tk.Radiobutton(
                currency_frame,
                text=f"{info['symbol']} {info['name']} ({code})",
                variable=currency_var,
                value=code,
                font=self.normal_font,
                bg='white',
                activebackground='white',
                selectcolor=self.colors['success']
            ).pack(anchor=tk.W)
        
        def save_currency():
            self.current_currency = currency_var.get()
            self.data['currency'] = self.current_currency
            self.save_data()
            self.show_income_setup()
        
        self.create_button(
            container,
            "➡️ Continue",
            save_currency,
            width=15
        ).pack(pady=20)
    
    def add_welcome_pet(self, parent):
        """Add an animated pet to the welcome screen"""
        canvas = tk.Canvas(parent, width=150, height=150, bg=self.colors['bg'], highlightthickness=0)
        canvas.place(x=50, y=50)
        
        # Draw a cute cat
        def animate_pet():
            canvas.delete("all")
            # Body
            canvas.create_oval(40, 60, 110, 120, fill=self.colors['primary'], outline="")
            # Head
            canvas.create_oval(50, 30, 100, 80, fill=self.colors['primary'], outline="")
            # Ears
            canvas.create_polygon(55, 40, 50, 20, 65, 35, fill=self.colors['primary'], outline="")
            canvas.create_polygon(95, 40, 100, 20, 85, 35, fill=self.colors['primary'], outline="")
            # Eyes (blinking animation)
            eye_size = 5 if (self.pet_frame // 20) % 2 == 0 else 2
            canvas.create_oval(62, 50, 62+eye_size, 50+eye_size, fill="white")
            canvas.create_oval(82, 50, 82+eye_size, 50+eye_size, fill="white")
            # Whiskers
            canvas.create_line(40, 60, 20, 55, fill="white", width=2)
            canvas.create_line(40, 65, 20, 65, fill="white", width=2)
            canvas.create_line(110, 60, 130, 55, fill="white", width=2)
            canvas.create_line(110, 65, 130, 65, fill="white", width=2)
            
            self.pet_frame += 1
            if hasattr(self, '_pet_animation'):
                canvas.after(100, animate_pet)
        
        self._pet_animation = True
        animate_pet()
    
    def show_income_setup(self):
        """Show income setup screen - CENTERED"""
        self.clear_window()
        
        # Main container
        outer_frame = tk.Frame(self.root, bg=self.colors['bg'])
        outer_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title at top (centered)
        title = tk.Label(
            outer_frame,
            text="💵 Set Up Your Income Sources",
            font=self.title_font,
            bg=self.colors['bg'],
            fg=self.colors['info']
        )
        title.pack(pady=20)
        
        # Create centered container for scrollable content
        center_container = tk.Frame(outer_frame, bg=self.colors['bg'])
        center_container.pack(expand=True, fill=tk.BOTH)
        
        canvas, scrollbar, scrollable_frame = self.create_scrollable_frame(center_container)
        
        # Create inner container for cards (fixed width for centering)
        cards_container = tk.Frame(scrollable_frame, bg=self.colors['bg'])
        cards_container.pack(expand=True)
        
        # Regular Income Section - centered cards
        regular_card = self.create_card(cards_container)
        regular_card.pack(pady=15)
        
        tk.Label(
            regular_card,
            text="📅 Regular Income (Salary, Wages, etc.)",
            font=self.heading_font,
            bg='white',
            fg=self.colors['primary']
        ).pack(pady=15)
        
        # Income name
        tk.Label(regular_card, text="Income Name:", font=self.normal_font, bg='white').pack(pady=5)
        self.income_name_entry = tk.Entry(regular_card, font=self.normal_font, width=40)
        self.income_name_entry.pack(pady=5)
        self.income_name_entry.insert(0, "Monthly Salary")
        
        # Amount
        tk.Label(regular_card, text="Amount:", font=self.normal_font, bg='white').pack(pady=5)
        self.income_amount_entry = tk.Entry(regular_card, font=self.normal_font, width=40)
        self.income_amount_entry.pack(pady=5)
        
        # Frequency
        tk.Label(regular_card, text="Frequency:", font=self.normal_font, bg='white').pack(pady=5)
        self.frequency_var = tk.StringVar(value="Monthly")
        frequency_frame = tk.Frame(regular_card, bg='white')
        frequency_frame.pack(pady=5)
        
        frequencies = ["Weekly", "Bi-weekly", "Monthly", "Yearly"]
        for freq in frequencies:
            tk.Radiobutton(
                frequency_frame,
                text=freq,
                variable=self.frequency_var,
                value=freq,
                font=self.normal_font,
                bg='white'
            ).pack(side=tk.LEFT, padx=10)
        
        # Payment day
        tk.Label(regular_card, text="Which day do you get paid?", font=self.normal_font, bg='white').pack(pady=5)
        self.payment_day_entry = tk.Entry(regular_card, font=self.normal_font, width=40)
        self.payment_day_entry.pack(pady=5)
        self.payment_day_entry.insert(0, "1")
        tk.Label(
            regular_card,
            text="(e.g., 1 for 1st of month, or Monday, Wednesday, etc.)",
            font=self.small_font,
            bg='white',
            fg=self.colors['light_text']
        ).pack(pady=5)
        
        # Current amount left
        tk.Label(
            regular_card,
            text="How much do you have left from your current payment?",
            font=self.normal_font,
            bg='white'
        ).pack(pady=5)
        self.current_left_entry = tk.Entry(regular_card, font=self.normal_font, width=40)
        self.current_left_entry.pack(pady=10)
        
        # One-time income section - centered
        onetime_card = self.create_card(cards_container)
        onetime_card.pack(pady=15)
        
        tk.Label(
            onetime_card,
            text="💸 One-Time Income (Optional)",
            font=self.heading_font,
            bg='white',
            fg=self.colors['secondary']
        ).pack(pady=15)
        
        tk.Label(
            onetime_card,
            text="Description:",
            font=self.normal_font,
            bg='white'
        ).pack(pady=5)
        self.onetime_desc_entry = tk.Entry(onetime_card, font=self.normal_font, width=40)
        self.onetime_desc_entry.pack(pady=5)
        
        tk.Label(onetime_card, text="Amount:", font=self.normal_font, bg='white').pack(pady=5)
        self.onetime_amount_entry = tk.Entry(onetime_card, font=self.normal_font, width=40)
        self.onetime_amount_entry.pack(pady=10)
        
        # Button frame - centered
        btn_frame = tk.Frame(cards_container, bg=self.colors['bg'])
        btn_frame.pack(pady=20)
        
        self.create_button(
            btn_frame,
            "➡️ Next: Savings",
            self.save_income_and_continue
        ).pack()
        
        # Pack canvas and scrollbar (full width)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def save_income_and_continue(self):
        """Save income data and continue to savings setup"""
        try:
            # Validate regular income
            income_name = self.income_name_entry.get().strip()
            income_amount = float(self.income_amount_entry.get().strip())
            frequency = self.frequency_var.get()
            payment_day = self.payment_day_entry.get().strip()
            current_left = float(self.current_left_entry.get().strip() or 0)
            
            if not income_name or income_amount <= 0:
                messagebox.showerror("Error", "Please enter valid income name and amount!")
                return
            
            # Save regular income
            if 'regular_incomes' not in self.data:
                self.data['regular_incomes'] = []
            
            self.data['regular_incomes'].append({
                'name': income_name,
                'amount': income_amount,
                'frequency': frequency,
                'payment_day': payment_day,
                'current_left': current_left,
                'last_payment': datetime.now().strftime('%Y-%m-%d')
            })
            
            # Save one-time income if provided
            onetime_desc = self.onetime_desc_entry.get().strip()
            onetime_amount = self.onetime_amount_entry.get().strip()
            
            if onetime_desc and onetime_amount:
                if 'onetime_incomes' not in self.data:
                    self.data['onetime_incomes'] = []
                
                self.data['onetime_incomes'].append({
                    'description': onetime_desc,
                    'amount': float(onetime_amount),
                    'date': datetime.now().strftime('%Y-%m-%d')
                })
            
            self.save_data()
            self.show_savings_setup()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for amounts!")
    
    def show_savings_setup(self):
        """Show savings setup screen"""
        self.clear_window()
        
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)
        
        # Title
        title = tk.Label(
            main_frame,
            text="🎯 Let's Talk About Your Goals!",
            font=self.title_font,
            bg=self.colors['bg'],
            fg=self.colors['success']
        )
        title.pack(pady=20)
        
        # Savings account card
        savings_card = self.create_card(main_frame)
        savings_card.pack(pady=20, fill=tk.BOTH, expand=True)
        
        tk.Label(
            savings_card,
            text="💰 Current Savings",
            font=self.heading_font,
            bg='white',
            fg=self.colors['info']
        ).pack(pady=15)
        
        tk.Label(
            savings_card,
            text="Do you have a savings account?",
            font=self.normal_font,
            bg='white'
        ).pack(pady=10)
        
        tk.Label(
            savings_card,
            text="Current savings balance:",
            font=self.normal_font,
            bg='white'
        ).pack(pady=5)
        self.savings_balance_entry = tk.Entry(savings_card, font=self.normal_font, width=30)
        self.savings_balance_entry.pack(pady=5)
        self.savings_balance_entry.insert(0, "0")
        
        tk.Label(
            savings_card,
            text="🎯 Savings Goal",
            font=self.heading_font,
            bg='white',
            fg=self.colors['primary']
        ).pack(pady=15)
        
        tk.Label(
            savings_card,
            text="What are you saving for? (e.g., Vacation, Car, Emergency Fund)",
            font=self.normal_font,
            bg='white'
        ).pack(pady=5)
        self.goal_name_entry = tk.Entry(savings_card, font=self.normal_font, width=40)
        self.goal_name_entry.pack(pady=5)
        
        tk.Label(
            savings_card,
            text="Target amount:",
            font=self.normal_font,
            bg='white'
        ).pack(pady=5)
        self.goal_amount_entry = tk.Entry(savings_card, font=self.normal_font, width=30)
        self.goal_amount_entry.pack(pady=5)
        
        tk.Label(
            savings_card,
            text="Target date (optional):",
            font=self.normal_font,
            bg='white'
        ).pack(pady=5)
        self.goal_date_entry = tk.Entry(savings_card, font=self.normal_font, width=30)
        self.goal_date_entry.pack(pady=5)
        self.goal_date_entry.insert(0, "YYYY-MM-DD")
        
        # Buttons
        btn_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        btn_frame.pack(pady=20)
        
        self.create_button(
            btn_frame,
            "✨ Complete Setup!",
            self.complete_setup
        ).pack()
    
    def complete_setup(self):
        """Complete initial setup and go to main dashboard"""
        try:
            savings_balance = float(self.savings_balance_entry.get().strip() or 0)
            goal_name = self.goal_name_entry.get().strip()
            goal_amount = self.goal_amount_entry.get().strip()
            goal_date = self.goal_date_entry.get().strip()
            
            self.data['savings'] = {
                'balance': savings_balance,
                'initial_balance': savings_balance
            }
            
            if goal_name and goal_amount:
                if 'goals' not in self.data:
                    self.data['goals'] = []
                
                goal_data = {
                    'name': goal_name,
                    'target_amount': float(goal_amount),
                    'current_amount': savings_balance,
                    'created': datetime.now().strftime('%Y-%m-%d')
                }
                
                if goal_date and goal_date != "YYYY-MM-DD":
                    goal_data['target_date'] = goal_date
                
                self.data['goals'].append(goal_data)
            
            if 'expenses' not in self.data:
                self.data['expenses'] = []
            
            self.data['setup_complete'] = True
            self.save_data()
            
            messagebox.showinfo(
                "Success! 🎉",
                "Your budget planner is all set up!\nLet's start managing your finances!"
            )
            
            self.show_main_dashboard()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers!")
    
    def show_main_dashboard(self):
        """Show main dashboard"""
        self.clear_window()
        
        # Main container
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header with settings button
        header = tk.Frame(main_frame, bg=self.colors['primary'], height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # Settings button (top right)
        settings_btn = tk.Button(
            header,
            text="⚙️ Settings",
            command=self.show_settings,
            bg=self.colors['secondary'],
            fg='white',
            font=self.small_font,
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor='hand2'
        )
        settings_btn.place(relx=0.95, rely=0.5, anchor=tk.E)
        
        # Title (centered)
        tk.Label(
            header,
            text="💰 My Budget Dashboard 💰",
            font=self.title_font,
            bg=self.colors['primary'],
            fg='white'
        ).place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Create centered container for content
        center_outer = tk.Frame(main_frame, bg=self.colors['bg'])
        center_outer.pack(fill=tk.BOTH, expand=True)
        
        canvas, scrollbar, content_wrapper = self.create_scrollable_frame(center_outer)
        
        # Inner content frame with padding for centering effect
        content_frame = tk.Frame(content_wrapper, bg=self.colors['bg'])
        content_frame.pack(expand=True, padx=50)
        
        # Calculate totals
        total_income = self.calculate_total_current_income()
        total_expenses = self.calculate_total_expenses()
        remaining = total_income - total_expenses
        
        # Summary cards row (centered with better spacing)
        summary_frame = tk.Frame(content_frame, bg=self.colors['bg'])
        summary_frame.pack(pady=15)
        
        # Income card
        self.create_summary_card(
            summary_frame,
            "💵 Available Money",
            self.format_currency(total_income),
            self.colors['success']
        ).pack(side=tk.LEFT, padx=10)
        
        # Expenses card
        self.create_summary_card(
            summary_frame,
            "💸 Total Expenses",
            self.format_currency(total_expenses),
            self.colors['primary']
        ).pack(side=tk.LEFT, padx=10)
        
        # Remaining card
        self.create_summary_card(
            summary_frame,
            "💰 Remaining",
            self.format_currency(remaining),
            self.colors['info']
        ).pack(side=tk.LEFT, padx=10)
        
        # Goals section
        if 'goals' in self.data and self.data['goals']:
            self.show_goals_section(content_frame)
        
        # Recent expenses section
        self.show_expenses_section(content_frame)
        
        # Action buttons (centered)
        button_container = tk.Frame(content_frame, bg=self.colors['bg'])
        button_container.pack(pady=20)
        
        btn_row1 = tk.Frame(button_container, bg=self.colors['bg'])
        btn_row1.pack(pady=5)
        
        self.create_button(
            btn_row1,
            "➕ Add Expense",
            self.show_add_expense,
            'primary',
            18
        ).pack(side=tk.LEFT, padx=10)
        
        self.create_button(
            btn_row1,
            "💵 Add Income",
            self.show_add_income,
            'success',
            18
        ).pack(side=tk.LEFT, padx=10)
        
        btn_row2 = tk.Frame(button_container, bg=self.colors['bg'])
        btn_row2.pack(pady=5)
        
        self.create_button(
            btn_row2,
            "💵 Manage Incomes",
            self.show_manage_incomes,
            'success',
            18
        ).pack(side=tk.LEFT, padx=10)
        
        self.create_button(
            btn_row2,
            "🎯 Manage Goals",
            self.show_manage_goals,
            'info',
            18
        ).pack(side=tk.LEFT, padx=10)
        
        btn_row3 = tk.Frame(button_container, bg=self.colors['bg'])
        btn_row3.pack(pady=5)
        
        self.create_button(
            btn_row3,
            "📊 View Reports",
            self.show_reports,
            'secondary',
            18
        ).pack(side=tk.LEFT, padx=10)
        
        self.create_button(
            btn_row3,
            "🔄 Recurring Expenses",
            self.show_manage_recurring_expenses,
            'primary',
            18
        ).pack(side=tk.LEFT, padx=10)
        
        # Pack canvas and scrollbar (full width)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add animated pet companion
        self.add_dashboard_pet(main_frame)
    
    def create_summary_card(self, parent, title, value, color):
        """Create a summary card widget"""
        card = self.create_card(parent)
        card.configure(bg=color, bd=0)
        
        tk.Label(
            card,
            text=title,
            font=self.normal_font,
            bg=color,
            fg='white'
        ).pack(pady=(15, 5))
        
        tk.Label(
            card,
            text=value,
            font=self.title_font,
            bg=color,
            fg='white'
        ).pack(pady=(5, 15))
        
        return card
    
    def show_goals_section(self, parent):
        """Show savings goals section - CENTERED"""
        goals_card = self.create_card(parent)
        goals_card.pack(pady=15, fill=tk.X, padx=20)
        
        tk.Label(
            goals_card,
            text="🎯 Your Savings Goals",
            font=self.heading_font,
            bg='white',
            fg=self.colors['primary']
        ).pack(pady=15)
        
        for goal in self.data['goals']:
            self.create_goal_widget(goals_card, goal)
    
    def create_goal_widget(self, parent, goal):
        """Create a goal progress widget"""
        goal_frame = tk.Frame(parent, bg='white')
        goal_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Goal name and amount
        header_frame = tk.Frame(goal_frame, bg='white')
        header_frame.pack(fill=tk.X)
        
        tk.Label(
            header_frame,
            text=goal['name'],
            font=self.heading_font,
            bg='white',
            fg=self.colors['text']
        ).pack(side=tk.LEFT)
        
        progress_percent = (goal['current_amount'] / goal['target_amount']) * 100
        tk.Label(
            header_frame,
            text=f"{self.format_currency(goal['current_amount'])} / {self.format_currency(goal['target_amount'])} ({progress_percent:.0f}%)",
            font=self.normal_font,
            bg='white',
            fg=self.colors['light_text']
        ).pack(side=tk.RIGHT)
        
        # Progress bar
        progress_frame = tk.Frame(goal_frame, bg='#E0E0E0', height=30)
        progress_frame.pack(fill=tk.X, pady=10)
        progress_frame.pack_propagate(False)
        
        progress_width = min(progress_percent, 100)
        progress_bar = tk.Frame(
            progress_frame,
            bg=self.colors['success'],
            height=30
        )
        progress_bar.place(x=0, y=0, relwidth=progress_width/100, relheight=1)
        
        # Motivational message
        if progress_percent >= 100:
            msg = "🎉 Goal Achieved! Amazing!"
            color = self.colors['success']
        elif progress_percent >= 75:
            msg = "💪 So close! You're doing great!"
            color = self.colors['success']
        elif progress_percent >= 50:
            msg = "👍 Halfway there! Keep it up!"
            color = self.colors['info']
        elif progress_percent >= 25:
            msg = "🌟 Good start! Stay consistent!"
            color = self.colors['secondary']
        else:
            msg = "🚀 Every step counts! You got this!"
            color = self.colors['primary']
        
        tk.Label(
            goal_frame,
            text=msg,
            font=self.normal_font,
            bg='white',
            fg=color
        ).pack()
    
    def show_expenses_section(self, parent):
        """Show recent expenses section - CENTERED"""
        expenses_card = self.create_card(parent)
        expenses_card.pack(pady=15, fill=tk.X, padx=20)
        
        tk.Label(
            expenses_card,
            text="📝 Recent Expenses",
            font=self.heading_font,
            bg='white',
            fg=self.colors['info']
        ).pack(pady=15)
        
        if not self.data.get('expenses'):
            tk.Label(
                expenses_card,
                text="No expenses recorded yet.\nClick 'Add Expense' to get started! 👆",
                font=self.normal_font,
                bg='white',
                fg=self.colors['light_text']
            ).pack(pady=20)
        else:
            # Show last 5 expenses
            recent = self.data['expenses'][-5:][::-1]
            for expense in recent:
                self.create_expense_widget(expenses_card, expense)
    
    def create_expense_widget(self, parent, expense):
        """Create an expense item widget with edit button"""
        exp_frame = tk.Frame(parent, bg='#F8F9FA', relief=tk.FLAT, bd=1, highlightthickness=1, highlightbackground=self.colors['shadow'])
        exp_frame.pack(fill=tk.X, padx=20, pady=8)
        
        left_frame = tk.Frame(exp_frame, bg='#F8F9FA')
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=12)
        
        tk.Label(
            left_frame,
            text=expense['description'],
            font=self.heading_font,
            bg='#F8F9FA',
            fg=self.colors['text']
        ).pack(anchor=tk.W)
        
        tk.Label(
            left_frame,
            text=f"{expense['category']} • {expense['date']}",
            font=self.small_font,
            bg='#F8F9FA',
            fg=self.colors['light_text']
        ).pack(anchor=tk.W)
        
        right_frame = tk.Frame(exp_frame, bg='#F8F9FA')
        right_frame.pack(side=tk.RIGHT, padx=15, pady=12)
        
        tk.Label(
            right_frame,
            text=self.format_currency(expense['amount']),
            font=self.heading_font,
            bg='#F8F9FA',
            fg=self.colors['primary']
        ).pack()
        
        # Edit button
        edit_btn = tk.Button(
            right_frame,
            text="✏️ Edit",
            command=lambda e=expense: self.show_edit_expense_dialog(e),
            bg=self.colors['info'],
            fg='white',
            font=self.small_font,
            relief=tk.FLAT,
            padx=10,
            pady=4,
            cursor='hand2',
            bd=0
        )
        edit_btn.pack(pady=(5, 0))
    
    def calculate_total_current_income(self):
        """Calculate total available income"""
        total = 0
        
        # Regular incomes - current left amount
        for income in self.data.get('regular_incomes', []):
            total += income.get('current_left', 0)
        
        # One-time incomes
        for income in self.data.get('onetime_incomes', []):
            total += income.get('amount', 0)
        
        return total
    
    def calculate_total_expenses(self):
        """Calculate total expenses"""
        return sum(exp['amount'] for exp in self.data.get('expenses', []))
    
    def show_add_expense(self):
        """Show add expense dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Expense")
        dialog.geometry("520x720")
        dialog.configure(bg=self.colors['bg'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        tk.Label(
            dialog,
            text="💸 Add New Expense",
            font=self.title_font,
            bg=self.colors['bg'],
            fg=self.colors['primary']
        ).pack(pady=20)
        
        form_frame = self.create_card(dialog)
        form_frame.pack(pady=20, padx=30, fill=tk.BOTH, expand=True)
        
        # Description
        tk.Label(
            form_frame,
            text="Description:",
            font=self.normal_font,
            bg='white'
        ).pack(pady=(20, 5))
        desc_entry = tk.Entry(form_frame, font=self.normal_font, width=35)
        desc_entry.pack(pady=5)
        
        # Amount
        tk.Label(
            form_frame,
            text="Amount:",
            font=self.normal_font,
            bg='white'
        ).pack(pady=(15, 5))
        amount_entry = tk.Entry(form_frame, font=self.normal_font, width=35)
        amount_entry.pack(pady=5)
        
        # Category
        tk.Label(
            form_frame,
            text="Category:",
            font=self.normal_font,
            bg='white'
        ).pack(pady=(15, 5))
        
        categories = [
            "🏠 Housing",
            "🍔 Food",
            "🚗 Transportation",
            "💡 Utilities",
            "🎬 Entertainment",
            "🏥 Healthcare",
            "👕 Shopping",
            "📚 Education",
            "💳 Debt Payment",
            "🎨 Other"
        ]
        
        category_var = tk.StringVar(value=categories[0])
        category_menu = ttk.Combobox(
            form_frame,
            textvariable=category_var,
            values=categories,
            font=self.normal_font,
            state='readonly',
            width=33
        )
        category_menu.pack(pady=5)
        
        # Expense Type: Recurring or One-time
        tk.Label(
            form_frame,
            text="Expense Type:",
            font=self.normal_font,
            bg='white'
        ).pack(pady=(15, 5))
        
        expense_type_var = tk.StringVar(value="one_time")
        
        type_frame = tk.Frame(form_frame, bg='white')
        type_frame.pack(pady=5)
        
        tk.Radiobutton(
            type_frame,
            text="💸 One-Time (this month only)",
            variable=expense_type_var,
            value="one_time",
            font=self.normal_font,
            bg='white',
            activebackground='white'
        ).pack(anchor=tk.W, padx=10)
        
        tk.Radiobutton(
            type_frame,
            text="🔄 Recurring (every month automatically)",
            variable=expense_type_var,
            value="recurring",
            font=self.normal_font,
            bg='white',
            activebackground='white'
        ).pack(anchor=tk.W, padx=10)
        
        tk.Label(
            form_frame,
            text="Recurring expenses are automatically added each month!",
            font=self.small_font,
            bg='white',
            fg=self.colors['light_text']
        ).pack(pady=5)
        
        # Date
        tk.Label(
            form_frame,
            text="Date:",
            font=self.normal_font,
            bg='white'
        ).pack(pady=(15, 5))
        date_entry = tk.Entry(form_frame, font=self.normal_font, width=35)
        date_entry.pack(pady=5)
        date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        
        # Notes
        tk.Label(
            form_frame,
            text="Notes (optional):",
            font=self.normal_font,
            bg='white'
        ).pack(pady=(15, 5))
        notes_entry = tk.Entry(form_frame, font=self.normal_font, width=35)
        notes_entry.pack(pady=5)
        
        def save_expense():
            try:
                description = desc_entry.get().strip()
                amount = float(amount_entry.get().strip())
                category = category_var.get()
                expense_type = expense_type_var.get()
                date = date_entry.get().strip()
                notes = notes_entry.get().strip()
                
                if not description or amount <= 0:
                    messagebox.showerror("Error", "Please enter valid description and amount!")
                    return
                
                if expense_type == "recurring":
                    # Add to recurring expenses
                    if 'recurring_expenses' not in self.data:
                        self.data['recurring_expenses'] = []
                    
                    recurring_expense = {
                        'description': description,
                        'amount': amount,
                        'category': category,
                        'notes': notes,
                        'created': datetime.now().strftime('%Y-%m-%d')
                    }
                    self.data['recurring_expenses'].append(recurring_expense)
                    
                    # Also add for this month
                    expense = {
                        'description': description,
                        'amount': amount,
                        'category': category,
                        'date': date,
                        'notes': notes + " (Recurring)",
                        'is_recurring': True
                    }
                    self.data['expenses'].append(expense)
                    
                    messagebox.showinfo(
                        "Success! 🎉",
                        f"Recurring expense added!\nThis will be automatically added every month."
                    )
                else:
                    # One-time expense
                    expense = {
                        'description': description,
                        'amount': amount,
                        'category': category,
                        'date': date,
                        'notes': notes,
                        'is_recurring': False
                    }
                    self.data['expenses'].append(expense)
                    messagebox.showinfo("Success! 🎉", "Expense added successfully!")
                
                self.save_data()
                dialog.destroy()
                self.show_main_dashboard()
                
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid amount!")
        
        # Buttons
        btn_frame = tk.Frame(dialog, bg=self.colors['bg'])
        btn_frame.pack(pady=20)
        
        self.create_button(
            btn_frame,
            "✅ Save Expense",
            save_expense,
            'primary'
        ).pack(side=tk.LEFT, padx=10)
        
        self.create_button(
            btn_frame,
            "❌ Cancel",
            dialog.destroy,
            'light_text'
        ).pack(side=tk.LEFT, padx=10)
    
    def show_add_income(self):
        """Show add income dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Income")
        dialog.geometry("500x400")
        dialog.configure(bg=self.colors['bg'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        tk.Label(
            dialog,
            text="💵 Add One-Time Income",
            font=self.title_font,
            bg=self.colors['bg'],
            fg=self.colors['success']
        ).pack(pady=20)
        
        form_frame = self.create_card(dialog)
        form_frame.pack(pady=20, padx=30, fill=tk.BOTH, expand=True)
        
        tk.Label(
            form_frame,
            text="Description:",
            font=self.normal_font,
            bg='white'
        ).pack(pady=(20, 5))
        desc_entry = tk.Entry(form_frame, font=self.normal_font, width=35)
        desc_entry.pack(pady=5)
        desc_entry.insert(0, "e.g., Freelance project, Gift, Bonus")
        
        tk.Label(
            form_frame,
            text="Amount:",
            font=self.normal_font,
            bg='white'
        ).pack(pady=(15, 5))
        amount_entry = tk.Entry(form_frame, font=self.normal_font, width=35)
        amount_entry.pack(pady=5)
        
        def save_income():
            try:
                description = desc_entry.get().strip()
                amount = float(amount_entry.get().strip())
                
                if not description or amount <= 0:
                    messagebox.showerror("Error", "Please enter valid description and amount!")
                    return
                
                if 'onetime_incomes' not in self.data:
                    self.data['onetime_incomes'] = []
                
                income = {
                    'description': description,
                    'amount': amount,
                    'date': datetime.now().strftime('%Y-%m-%d')
                }
                
                self.data['onetime_incomes'].append(income)
                self.save_data()
                
                dialog.destroy()
                messagebox.showinfo("Success! 🎉", "Income added successfully!")
                self.show_main_dashboard()
                
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid amount!")
        
        btn_frame = tk.Frame(dialog, bg=self.colors['bg'])
        btn_frame.pack(pady=20)
        
        self.create_button(
            btn_frame,
            "✅ Save Income",
            save_income,
            'success'
        ).pack(side=tk.LEFT, padx=10)
        
        self.create_button(
            btn_frame,
            "❌ Cancel",
            dialog.destroy,
            'light_text'
        ).pack(side=tk.LEFT, padx=10)
    
    def show_manage_goals(self):
        """Show manage goals screen"""
        self.clear_window()
        
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # Header with back button
        header_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.create_button(
            header_frame,
            "⬅️ Back",
            self.show_main_dashboard,
            'info',
            10
        ).pack(side=tk.LEFT)
        
        tk.Label(
            header_frame,
            text="🎯 Manage Your Goals",
            font=self.title_font,
            bg=self.colors['bg'],
            fg=self.colors['primary']
        ).pack(side=tk.LEFT, padx=20)
        
        canvas, scrollbar, content = self.create_scrollable_frame(main_frame)

        # Goals list
        if self.data.get('goals'):
            for goal in self.data['goals']:
                self.create_goal_management_card(content, goal)
        else:
            tk.Label(
                content,
                text="No goals yet. Add your first goal! 🎯",
                font=self.heading_font,
                bg=self.colors['bg'],
                fg=self.colors['light_text']
            ).pack(pady=40)
        
        # Add goal button
        self.create_button(
            content,
            "➕ Add New Goal",
            self.show_add_goal_dialog,
            'success',
            20
        ).pack(pady=20)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_goal_management_card(self, parent, goal):
        """Create a goal management card"""
        card = self.create_card(parent)
        card.pack(pady=10, fill=tk.X)
        
        # Goal info
        info_frame = tk.Frame(card, bg='white')
        info_frame.pack(fill=tk.X, padx=20, pady=15)
        
        tk.Label(
            info_frame,
            text=goal['name'],
            font=self.heading_font,
            bg='white',
            fg=self.colors['text']
        ).pack(anchor=tk.W)
        
        tk.Label(
            info_frame,
            text=f"Target: {self.format_currency(goal['target_amount'])} | Current: {self.format_currency(goal['current_amount'])}",
            font=self.normal_font,
            bg='white',
            fg=self.colors['light_text']
        ).pack(anchor=tk.W, pady=5)
        
        # Progress bar
        progress_percent = (goal['current_amount'] / goal['target_amount']) * 100
        progress_frame = tk.Frame(card, bg='#E0E0E0', height=25)
        progress_frame.pack(fill=tk.X, padx=20, pady=10)
        progress_frame.pack_propagate(False)
        
        progress_width = min(progress_percent, 100)
        progress_bar = tk.Frame(progress_frame, bg=self.colors['success'], height=25)
        progress_bar.place(x=0, y=0, relwidth=progress_width/100, relheight=1)
        
        tk.Label(
            progress_frame,
            text=f"{progress_percent:.0f}%",
            font=self.normal_font,
            bg='#E0E0E0',
            fg=self.colors['text']
        ).place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Buttons
        btn_frame = tk.Frame(card, bg='white')
        btn_frame.pack(pady=15)
        
        self.create_button(
            btn_frame,
            "💰 Add to Goal",
            lambda g=goal: self.show_add_to_goal_dialog(g),
            'success',
            15
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="✏️ Edit",
            command=lambda g=goal: self.show_edit_goal_dialog(g),
            bg=self.colors['info'],
            fg='white',
            font=self.normal_font,
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor='hand2',
            bd=0
        ).pack(side=tk.LEFT, padx=5)
    
    def show_add_goal_dialog(self):
        """Show add goal dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Goal")
        dialog.geometry("500x500")
        dialog.configure(bg=self.colors['bg'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(
            dialog,
            text="🎯 Create New Goal",
            font=self.title_font,
            bg=self.colors['bg'],
            fg=self.colors['primary']
        ).pack(pady=20)
        
        form_frame = self.create_card(dialog)
        form_frame.pack(pady=20, padx=30, fill=tk.BOTH, expand=True)
        
        tk.Label(form_frame, text="Goal Name:", font=self.normal_font, bg='white').pack(pady=(20, 5))
        name_entry = tk.Entry(form_frame, font=self.normal_font, width=35)
        name_entry.pack(pady=5)
        
        tk.Label(form_frame, text="Target Amount:", font=self.normal_font, bg='white').pack(pady=(15, 5))
        amount_entry = tk.Entry(form_frame, font=self.normal_font, width=35)
        amount_entry.pack(pady=5)
        
        tk.Label(form_frame, text="Current Amount (optional):", font=self.normal_font, bg='white').pack(pady=(15, 5))
        current_entry = tk.Entry(form_frame, font=self.normal_font, width=35)
        current_entry.pack(pady=5)
        current_entry.insert(0, "0")
        
        tk.Label(form_frame, text="Target Date (optional):", font=self.normal_font, bg='white').pack(pady=(15, 5))
        date_entry = tk.Entry(form_frame, font=self.normal_font, width=35)
        date_entry.pack(pady=5)
        date_entry.insert(0, "YYYY-MM-DD")
        
        def save_goal():
            try:
                name = name_entry.get().strip()
                target = float(amount_entry.get().strip())
                current = float(current_entry.get().strip() or 0)
                target_date = date_entry.get().strip()
                
                if not name or target <= 0:
                    messagebox.showerror("Error", "Please enter valid goal name and target amount!")
                    return
                
                if 'goals' not in self.data:
                    self.data['goals'] = []
                
                goal = {
                    'name': name,
                    'target_amount': target,
                    'current_amount': current,
                    'created': datetime.now().strftime('%Y-%m-%d')
                }
                
                if target_date and target_date != "YYYY-MM-DD":
                    goal['target_date'] = target_date
                
                self.data['goals'].append(goal)
                self.save_data()
                
                dialog.destroy()
                messagebox.showinfo("Success! 🎉", "Goal created successfully!")
                self.show_manage_goals()
                
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers!")
        
        btn_frame = tk.Frame(dialog, bg=self.colors['bg'])
        btn_frame.pack(pady=20)
        
        self.create_button(btn_frame, "✅ Create Goal", save_goal, 'success').pack(side=tk.LEFT, padx=10)
        self.create_button(btn_frame, "❌ Cancel", dialog.destroy, 'light_text').pack(side=tk.LEFT, padx=10)
    
    def show_add_to_goal_dialog(self, goal):
        """Show dialog to add money to a goal"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add to Goal")
        dialog.geometry("450x300")
        dialog.configure(bg=self.colors['bg'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(
            dialog,
            text=f"💰 Add to: {goal['name']}",
            font=self.title_font,
            bg=self.colors['bg'],
            fg=self.colors['success']
        ).pack(pady=20)
        
        form_frame = self.create_card(dialog)
        form_frame.pack(pady=20, padx=30, fill=tk.BOTH, expand=True)
        
        tk.Label(
            form_frame,
            text=f"Current: {self.format_currency(goal['current_amount'])} / {self.format_currency(goal['target_amount'])}",
            font=self.normal_font,
            bg='white',
            fg=self.colors['light_text']
        ).pack(pady=15)
        
        tk.Label(form_frame, text="Amount to add:", font=self.normal_font, bg='white').pack(pady=5)
        amount_entry = tk.Entry(form_frame, font=self.normal_font, width=25)
        amount_entry.pack(pady=5)
        
        def add_amount():
            try:
                amount = float(amount_entry.get().strip())
                if amount <= 0:
                    messagebox.showerror("Error", "Please enter a valid amount!")
                    return
                
                goal['current_amount'] += amount
                self.save_data()
                
                dialog.destroy()
                messagebox.showinfo("Success! 🎉", f"Added {self.format_currency(amount)} to your goal!")
                self.show_manage_goals()
                
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number!")
        
        btn_frame = tk.Frame(dialog, bg=self.colors['bg'])
        btn_frame.pack(pady=20)
        
        self.create_button(btn_frame, "✅ Add", add_amount, 'success').pack(side=tk.LEFT, padx=10)
        self.create_button(btn_frame, "❌ Cancel", dialog.destroy, 'light_text').pack(side=tk.LEFT, padx=10)
    
    def show_reports(self):
        """Show reports and analytics screen"""
        self.clear_window()
        
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # Header
        header_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.create_button(
            header_frame,
            "⬅️ Back",
            self.show_main_dashboard,
            'info',
            10
        ).pack(side=tk.LEFT)
        
        tk.Label(
            header_frame,
            text="📊 Your Financial Report",
            font=self.title_font,
            bg=self.colors['bg'],
            fg=self.colors['info']
        ).pack(side=tk.LEFT, padx=20)
        
        canvas, scrollbar, content = self.create_scrollable_frame(main_frame)
        
        # Expense breakdown by category
        if self.data.get('expenses'):
            category_card = self.create_card(content)
            category_card.pack(pady=10, fill=tk.X)
            
            tk.Label(
                category_card,
                text="💸 Expenses by Category",
                font=self.heading_font,
                bg='white',
                fg=self.colors['primary']
            ).pack(pady=15)
            
            # Calculate category totals
            category_totals = {}
            for expense in self.data['expenses']:
                cat = expense['category']
                category_totals[cat] = category_totals.get(cat, 0) + expense['amount']
            
            total_expenses = sum(category_totals.values())
            
            for category, amount in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
                self.create_category_bar(category_card, category, amount, total_expenses)
        
        # Spending trends
        trends_card = self.create_card(content)
        trends_card.pack(pady=10, fill=tk.X)
        
        tk.Label(
            trends_card,
            text="📈 Quick Stats",
            font=self.heading_font,
            bg='white',
            fg=self.colors['info']
        ).pack(pady=15)
        
        stats_frame = tk.Frame(trends_card, bg='white')
        stats_frame.pack(padx=20, pady=10)
        
        total_income = self.calculate_total_current_income()
        total_expenses = self.calculate_total_expenses()
        num_expenses = len(self.data.get('expenses', []))
        avg_expense = total_expenses / num_expenses if num_expenses > 0 else 0
        
        stats = [
            ("Total Income Available", self.format_currency(total_income)),
            ("Total Expenses", self.format_currency(total_expenses)),
            ("Number of Transactions", str(num_expenses)),
            ("Average Expense", self.format_currency(avg_expense)),
            ("Savings Rate", f"{((total_income - total_expenses) / total_income * 100 if total_income > 0 else 0):.1f}%")
        ]
        
        for label, value in stats:
            stat_row = tk.Frame(stats_frame, bg='white')
            stat_row.pack(fill=tk.X, pady=5)
            
            tk.Label(
                stat_row,
                text=label + ":",
                font=self.normal_font,
                bg='white',
                fg=self.colors['text']
            ).pack(side=tk.LEFT)
            
            tk.Label(
                stat_row,
                text=value,
                font=self.heading_font,
                bg='white',
                fg=self.colors['primary']
            ).pack(side=tk.RIGHT)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_category_bar(self, parent, category, amount, total):
        """Create a category spending bar"""
        bar_frame = tk.Frame(parent, bg='white')
        bar_frame.pack(fill=tk.X, padx=20, pady=8)
        
        # Category name and amount
        label_frame = tk.Frame(bar_frame, bg='white')
        label_frame.pack(fill=tk.X)
        
        tk.Label(
            label_frame,
            text=category,
            font=self.normal_font,
            bg='white',
            fg=self.colors['text']
        ).pack(side=tk.LEFT)
        
        percentage = (amount / total) * 100
        tk.Label(
            label_frame,
            text=f"{self.format_currency(amount)} ({percentage:.1f}%)",
            font=self.normal_font,
            bg='white',
            fg=self.colors['light_text']
        ).pack(side=tk.RIGHT)
        
        # Progress bar
        bar_bg = tk.Frame(bar_frame, bg='#E0E0E0', height=20)
        bar_bg.pack(fill=tk.X, pady=5)
        bar_bg.pack_propagate(False)
        
        bar_fill = tk.Frame(bar_bg, bg=self.colors['primary'], height=20)
        bar_fill.place(x=0, y=0, relwidth=percentage/100, relheight=1)
    
    def show_edit_expense_dialog(self, expense):
        """Show dialog to edit an expense"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Expense")
        dialog.geometry("520x650")
        dialog.configure(bg=self.colors['bg'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(
            dialog,
            text="✏️ Edit Expense",
            font=self.title_font,
            bg=self.colors['bg'],
            fg=self.colors['info']
        ).pack(pady=20)
        
        form_frame = tk.Frame(dialog, bg='white', bd=2, relief=tk.FLAT)
        form_frame.pack(pady=20, padx=30, fill=tk.BOTH, expand=True)
        
        # Description
        tk.Label(form_frame, text="Description:", font=self.normal_font, bg='white').pack(pady=(20, 5))
        desc_entry = tk.Entry(form_frame, font=self.normal_font, width=35)
        desc_entry.pack(pady=5)
        desc_entry.insert(0, expense['description'])
        
        # Amount
        tk.Label(form_frame, text="Amount:", font=self.normal_font, bg='white').pack(pady=(15, 5))
        amount_entry = tk.Entry(form_frame, font=self.normal_font, width=35)
        amount_entry.pack(pady=5)
        amount_entry.insert(0, str(expense['amount']))
        
        # Category
        tk.Label(form_frame, text="Category:", font=self.normal_font, bg='white').pack(pady=(15, 5))
        categories = [
            "🏠 Housing", "🍔 Food", "🚗 Transportation", "💡 Utilities",
            "🎬 Entertainment", "🏥 Healthcare", "👕 Shopping",
            "📚 Education", "💳 Debt Payment", "🎨 Other"
        ]
        category_var = tk.StringVar(value=expense['category'])
        category_menu = ttk.Combobox(form_frame, textvariable=category_var, values=categories,
                                     font=self.normal_font, state='readonly', width=33)
        category_menu.pack(pady=5)
        
        # Date
        tk.Label(form_frame, text="Date:", font=self.normal_font, bg='white').pack(pady=(15, 5))
        date_entry = tk.Entry(form_frame, font=self.normal_font, width=35)
        date_entry.pack(pady=5)
        date_entry.insert(0, expense['date'])
        
        # Notes
        tk.Label(form_frame, text="Notes:", font=self.normal_font, bg='white').pack(pady=(15, 5))
        notes_entry = tk.Entry(form_frame, font=self.normal_font, width=35)
        notes_entry.pack(pady=5)
        notes_entry.insert(0, expense.get('notes', ''))
        
        def save_changes():
            try:
                expense['description'] = desc_entry.get().strip()
                expense['amount'] = float(amount_entry.get().strip())
                expense['category'] = category_var.get()
                expense['date'] = date_entry.get().strip()
                expense['notes'] = notes_entry.get().strip()
                
                self.save_data()
                dialog.destroy()
                messagebox.showinfo("Success! ✓", "Expense updated successfully!")
                self.show_main_dashboard()
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid amount!")
        
        def delete_expense():
            if messagebox.askyesno("Delete Expense", "Are you sure you want to delete this expense?"):
                self.data['expenses'].remove(expense)
                self.save_data()
                dialog.destroy()
                messagebox.showinfo("Deleted", "Expense deleted successfully!")
                self.show_main_dashboard()
        
        btn_frame = tk.Frame(dialog, bg=self.colors['bg'])
        btn_frame.pack(pady=20)
        
        self.create_button(btn_frame, "✅ Save Changes", save_changes, 'success').pack(side=tk.LEFT, padx=5)
        self.create_button(btn_frame, "🗑️ Delete", delete_expense, 'primary').pack(side=tk.LEFT, padx=5)
        self.create_button(btn_frame, "❌ Cancel", dialog.destroy, 'light_text').pack(side=tk.LEFT, padx=5)
    
    def show_edit_income_dialog(self, income):
        """Show dialog to edit an income"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Income")
        dialog.geometry("520x600")
        dialog.configure(bg=self.colors['bg'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(
            dialog,
            text="✏️ Edit Income",
            font=self.title_font,
            bg=self.colors['bg'],
            fg=self.colors['success']
        ).pack(pady=20)
        
        form_frame = tk.Frame(dialog, bg='white', bd=2, relief=tk.FLAT)
        form_frame.pack(pady=20, padx=30, fill=tk.BOTH, expand=True)
        
        is_regular = 'frequency' in income
        
        if is_regular:
            # Regular income fields
            tk.Label(form_frame, text="Income Name:", font=self.normal_font, bg='white').pack(pady=(20, 5))
            name_entry = tk.Entry(form_frame, font=self.normal_font, width=35)
            name_entry.pack(pady=5)
            name_entry.insert(0, income['name'])
            
            tk.Label(form_frame, text="Amount:", font=self.normal_font, bg='white').pack(pady=(15, 5))
            amount_entry = tk.Entry(form_frame, font=self.normal_font, width=35)
            amount_entry.pack(pady=5)
            amount_entry.insert(0, str(income['amount']))
            
            tk.Label(form_frame, text="Current Left:", font=self.normal_font, bg='white').pack(pady=(15, 5))
            current_left_entry = tk.Entry(form_frame, font=self.normal_font, width=35)
            current_left_entry.pack(pady=5)
            current_left_entry.insert(0, str(income.get('current_left', 0)))
            
            def save_changes():
                try:
                    income['name'] = name_entry.get().strip()
                    income['amount'] = float(amount_entry.get().strip())
                    income['current_left'] = float(current_left_entry.get().strip())
                    self.save_data()
                    dialog.destroy()
                    messagebox.showinfo("Success! ✓", "Income updated successfully!")
                    self.show_main_dashboard()
                except ValueError:
                    messagebox.showerror("Error", "Please enter valid numbers!")
        else:
            # One-time income fields
            tk.Label(form_frame, text="Description:", font=self.normal_font, bg='white').pack(pady=(20, 5))
            desc_entry = tk.Entry(form_frame, font=self.normal_font, width=35)
            desc_entry.pack(pady=5)
            desc_entry.insert(0, income['description'])
            
            tk.Label(form_frame, text="Amount:", font=self.normal_font, bg='white').pack(pady=(15, 5))
            amount_entry = tk.Entry(form_frame, font=self.normal_font, width=35)
            amount_entry.pack(pady=5)
            amount_entry.insert(0, str(income['amount']))
            
            def save_changes():
                try:
                    income['description'] = desc_entry.get().strip()
                    income['amount'] = float(amount_entry.get().strip())
                    self.save_data()
                    dialog.destroy()
                    messagebox.showinfo("Success! ✓", "Income updated successfully!")
                    self.show_main_dashboard()
                except ValueError:
                    messagebox.showerror("Error", "Please enter a valid amount!")
        
        def delete_income():
            if messagebox.askyesno("Delete Income", "Are you sure you want to delete this income?"):
                if is_regular:
                    self.data['regular_incomes'].remove(income)
                else:
                    self.data['onetime_incomes'].remove(income)
                self.save_data()
                dialog.destroy()
                messagebox.showinfo("Deleted", "Income deleted successfully!")
                self.show_main_dashboard()
        
        btn_frame = tk.Frame(dialog, bg=self.colors['bg'])
        btn_frame.pack(pady=20)
        
        self.create_button(btn_frame, "✅ Save Changes", save_changes, 'success').pack(side=tk.LEFT, padx=5)
        self.create_button(btn_frame, "🗑️ Delete", delete_income, 'primary').pack(side=tk.LEFT, padx=5)
        self.create_button(btn_frame, "❌ Cancel", dialog.destroy, 'light_text').pack(side=tk.LEFT, padx=5)
    
    def show_edit_goal_dialog(self, goal):
        """Show dialog to edit a goal"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Goal")
        dialog.geometry("520x550")
        dialog.configure(bg=self.colors['bg'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(
            dialog,
            text="✏️ Edit Goal",
            font=self.title_font,
            bg=self.colors['bg'],
            fg=self.colors['info']
        ).pack(pady=20)
        
        form_frame = tk.Frame(dialog, bg='white', bd=2, relief=tk.FLAT)
        form_frame.pack(pady=20, padx=30, fill=tk.BOTH, expand=True)
        
        tk.Label(form_frame, text="Goal Name:", font=self.normal_font, bg='white').pack(pady=(20, 5))
        name_entry = tk.Entry(form_frame, font=self.normal_font, width=35)
        name_entry.pack(pady=5)
        name_entry.insert(0, goal['name'])
        
        tk.Label(form_frame, text="Target Amount:", font=self.normal_font, bg='white').pack(pady=(15, 5))
        target_entry = tk.Entry(form_frame, font=self.normal_font, width=35)
        target_entry.pack(pady=5)
        target_entry.insert(0, str(goal['target_amount']))
        
        tk.Label(form_frame, text="Current Amount:", font=self.normal_font, bg='white').pack(pady=(15, 5))
        current_entry = tk.Entry(form_frame, font=self.normal_font, width=35)
        current_entry.pack(pady=5)
        current_entry.insert(0, str(goal['current_amount']))
        
        tk.Label(form_frame, text="Target Date (optional):", font=self.normal_font, bg='white').pack(pady=(15, 5))
        date_entry = tk.Entry(form_frame, font=self.normal_font, width=35)
        date_entry.pack(pady=5)
        date_entry.insert(0, goal.get('target_date', 'YYYY-MM-DD'))
        
        def save_changes():
            try:
                goal['name'] = name_entry.get().strip()
                goal['target_amount'] = float(target_entry.get().strip())
                goal['current_amount'] = float(current_entry.get().strip())
                target_date = date_entry.get().strip()
                if target_date and target_date != "YYYY-MM-DD":
                    goal['target_date'] = target_date
                
                self.save_data()
                dialog.destroy()
                messagebox.showinfo("Success! ✓", "Goal updated successfully!")
                self.show_manage_goals()
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers!")
        
        def delete_goal():
            if messagebox.askyesno("Delete Goal", "Are you sure you want to delete this goal?"):
                self.data['goals'].remove(goal)
                self.save_data()
                dialog.destroy()
                messagebox.showinfo("Deleted", "Goal deleted successfully!")
                self.show_manage_goals()
        
        btn_frame = tk.Frame(dialog, bg=self.colors['bg'])
        btn_frame.pack(pady=20)
        
        self.create_button(btn_frame, "✅ Save Changes", save_changes, 'success').pack(side=tk.LEFT, padx=5)
        self.create_button(btn_frame, "🗑️ Delete", delete_goal, 'primary').pack(side=tk.LEFT, padx=5)
        self.create_button(btn_frame, "❌ Cancel", dialog.destroy, 'light_text').pack(side=tk.LEFT, padx=5)
    
    def show_manage_incomes(self):
        """Show screen to manage all incomes"""
        self.clear_window()
        
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # Header
        header_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.create_button(
            header_frame,
            "⬅️ Back",
            self.show_main_dashboard,
            'info',
            10
        ).pack(side=tk.LEFT)
        
        tk.Label(
            header_frame,
            text="💵 Manage Your Incomes",
            font=self.title_font,
            bg=self.colors['bg'],
            fg=self.colors['success']
        ).pack(side=tk.LEFT, padx=20)
        
        canvas, scrollbar, content = self.create_scrollable_frame(main_frame)
        
        # Regular incomes
        if self.data.get('regular_incomes'):
            reg_card = tk.Frame(content, bg='white', bd=2, relief=tk.FLAT)
            reg_card.pack(pady=10, fill=tk.X, padx=20)
            
            tk.Label(
                reg_card,
                text="📅 Regular Incomes",
                font=self.heading_font,
                bg='white',
                fg=self.colors['primary']
            ).pack(pady=15)
            
            for income in self.data['regular_incomes']:
                self.create_income_widget(reg_card, income, True)
        
        # One-time incomes
        if self.data.get('onetime_incomes'):
            onetime_card = tk.Frame(content, bg='white', bd=2, relief=tk.FLAT)
            onetime_card.pack(pady=10, fill=tk.X, padx=20)
            
            tk.Label(
                onetime_card,
                text="💸 One-Time Incomes",
                font=self.heading_font,
                bg='white',
                fg=self.colors['secondary']
            ).pack(pady=15)
            
            for income in self.data['onetime_incomes']:
                self.create_income_widget(onetime_card, income, False)
        
        if not self.data.get('regular_incomes') and not self.data.get('onetime_incomes'):
            tk.Label(
                content,
                text="No incomes yet. Add income from the dashboard! 💵",
                font=self.heading_font,
                bg=self.colors['bg'],
                fg=self.colors['light_text']
            ).pack(pady=40)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_income_widget(self, parent, income, is_regular):
        """Create an income item widget with edit button"""
        inc_frame = tk.Frame(parent, bg='#F0F8FF', relief=tk.FLAT, bd=1, highlightthickness=1, highlightbackground=self.colors['shadow'])
        inc_frame.pack(fill=tk.X, padx=20, pady=8)
        
        left_frame = tk.Frame(inc_frame, bg='#F0F8FF')
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=12)
        
        name = income.get('name') if is_regular else income.get('description')
        tk.Label(
            left_frame,
            text=name,
            font=self.heading_font,
            bg='#F0F8FF',
            fg=self.colors['text']
        ).pack(anchor=tk.W)
        
        if is_regular:
            detail = f"{income['frequency']} • Day {income['payment_day']} • Left: {self.format_currency(income.get('current_left', 0))}"
        else:
            detail = f"Date: {income['date']}"
        
        tk.Label(
            left_frame,
            text=detail,
            font=self.small_font,
            bg='#F0F8FF',
            fg=self.colors['light_text']
        ).pack(anchor=tk.W)
        
        right_frame = tk.Frame(inc_frame, bg='#F0F8FF')
        right_frame.pack(side=tk.RIGHT, padx=15, pady=12)
        
        tk.Label(
            right_frame,
            text=self.format_currency(income['amount']),
            font=self.heading_font,
            bg='#F0F8FF',
            fg=self.colors['success']
        ).pack()
        
        # Edit button
        edit_btn = tk.Button(
            right_frame,
            text="✏️ Edit",
            command=lambda i=income: self.show_edit_income_dialog(i),
            bg=self.colors['info'],
            fg='white',
            font=self.small_font,
            relief=tk.FLAT,
            padx=10,
            pady=4,
            cursor='hand2',
            bd=0
        )
        edit_btn.pack(pady=(5, 0))
    
    def show_manage_recurring_expenses(self):
        """Show screen to manage recurring expenses"""
        self.clear_window()
        
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # Header
        header_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.create_button(
            header_frame,
            "⬅️ Back",
            self.show_main_dashboard,
            'info',
            10
        ).pack(side=tk.LEFT)
        
        tk.Label(
            header_frame,
            text="🔄 Recurring Expenses",
            font=self.title_font,
            bg=self.colors['bg'],
            fg=self.colors['primary']
        ).pack(side=tk.LEFT, padx=20)
        
        # Info text
        tk.Label(
            main_frame,
            text="These expenses are automatically added every month!",
            font=self.normal_font,
            bg=self.colors['bg'],
            fg=self.colors['text']
        ).pack(pady=10)
        
        # Scrollable content
        canvas, scrollbar, content = self.create_scrollable_frame(main_frame)
        
        if self.data.get('recurring_expenses'):
            for expense in self.data['recurring_expenses']:
                self.create_recurring_expense_widget(content, expense)
        else:
            tk.Label(
                content,
                text="No recurring expenses set up yet.\n\nAdd expenses marked as 'Recurring' to see them here!",
                font=self.heading_font,
                bg=self.colors['bg'],
                fg=self.colors['light_text'],
                justify=tk.CENTER
            ).pack(pady=40)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_recurring_expense_widget(self, parent, expense):
        """Create a recurring expense item widget"""
        exp_frame = tk.Frame(parent, bg='#FFF8F0', relief=tk.FLAT, bd=1, highlightthickness=1, highlightbackground=self.colors['shadow'])
        exp_frame.pack(fill=tk.X, padx=20, pady=8)
        
        left_frame = tk.Frame(exp_frame, bg='#FFF8F0')
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=12)
        
        tk.Label(
            left_frame,
            text=expense['description'] + " 🔄",
            font=self.heading_font,
            bg='#FFF8F0',
            fg=self.colors['text']
        ).pack(anchor=tk.W)
        
        tk.Label(
            left_frame,
            text=f"{expense['category']} • Auto-deducted monthly",
            font=self.small_font,
            bg='#FFF8F0',
            fg=self.colors['light_text']
        ).pack(anchor=tk.W)
        
        right_frame = tk.Frame(exp_frame, bg='#FFF8F0')
        right_frame.pack(side=tk.RIGHT, padx=15, pady=12)
        
        tk.Label(
            right_frame,
            text=self.format_currency(expense['amount']),
            font=self.heading_font,
            bg='#FFF8F0',
            fg=self.colors['primary']
        ).pack()
        
        # Delete button
        delete_btn = tk.Button(
            right_frame,
            text="🗑️ Remove",
            command=lambda e=expense: self.delete_recurring_expense(e),
            bg=self.colors['primary'],
            fg='white',
            font=self.small_font,
            relief=tk.FLAT,
            padx=10,
            pady=4,
            cursor='hand2',
            bd=0
        )
        delete_btn.pack(pady=(5, 0))
    
    def delete_recurring_expense(self, expense):
        """Delete a recurring expense"""
        if messagebox.askyesno("Remove Recurring Expense", 
                               "Are you sure? This expense will no longer be added automatically each month."):
            self.data['recurring_expenses'].remove(expense)
            self.save_data()
            messagebox.showinfo("Removed", "Recurring expense removed successfully!")
            self.show_manage_recurring_expenses()
    
    def show_settings(self):
        """Show settings screen"""
        self.clear_window()
        
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # Header with back button
        header_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.create_button(
            header_frame,
            "⬅️ Back",
            self.show_main_dashboard,
            'info',
            10
        ).pack(side=tk.LEFT)
        
        tk.Label(
            header_frame,
            text="⚙️ Settings",
            font=self.title_font,
            bg=self.colors['bg'],
            fg=self.colors['primary']
        ).pack(side=tk.LEFT, padx=20)
        
        canvas, scrollbar, content = self.create_scrollable_frame(main_frame)
        
        # Currency Settings
        currency_card = self.create_card(content)
        currency_card.pack(pady=10, fill=tk.X, padx=20)
        
        tk.Label(
            currency_card,
            text="💱 Currency Settings",
            font=self.heading_font,
            bg='white',
            fg=self.colors['primary']
        ).pack(pady=15)
        
        current_curr = self.currencies[self.current_currency]
        tk.Label(
            currency_card,
            text=f"Current: {current_curr['symbol']} {current_curr['name']}",
            font=self.normal_font,
            bg='white',
            fg=self.colors['text']
        ).pack(pady=10)
        
        self.create_button(
            currency_card,
            "Change Currency",
            self.show_currency_change_dialog,
            'info',
            18
        ).pack(pady=15)
        
        # Theme Settings
        theme_card = self.create_card(content)
        theme_card.pack(pady=10, fill=tk.X, padx=20)
        
        tk.Label(
            theme_card,
            text="🎨 Color Theme",
            font=self.heading_font,
            bg='white',
            fg=self.colors['primary']
        ).pack(pady=15)
        
        tk.Label(
            theme_card,
            text="Choose your favorite color theme:",
            font=self.normal_font,
            bg='white',
            fg=self.colors['text']
        ).pack(pady=5)
        
        # Theme buttons
        theme_info = {
            'default': '💗 Cute Pink (Default)',
            'purple_dream': '💜 Purple Dream',
            'ocean_breeze': '🌊 Ocean Breeze',
            'sunset_glow': '🌅 Sunset Glow',
            'forest_zen': '🌲 Forest Zen'
        }
        
        for theme_name, theme_label in theme_info.items():
            btn_frame = tk.Frame(theme_card, bg='white')
            btn_frame.pack(pady=5)
            
            is_current = theme_name == self.current_theme
            btn = tk.Button(
                btn_frame,
                text=f"{'✓ ' if is_current else ''}{theme_label}",
                command=lambda t=theme_name: self.change_theme(t),
                bg=self.themes[theme_name]['primary'],
                fg='white',
                font=self.normal_font,
                relief=tk.RAISED if is_current else tk.FLAT,
                padx=20,
                pady=10,
                width=25,
                cursor='hand2'
            )
            btn.pack()
        
        # Pet Settings
        pet_card = self.create_card(content)
        pet_card.pack(pady=10, fill=tk.X, padx=20)
        
        tk.Label(
            pet_card,
            text="🐱 Choose Your Pet Companion",
            font=self.heading_font,
            bg='white',
            fg=self.colors['primary']
        ).pack(pady=15)
        
        tk.Label(
            pet_card,
            text="A cute pet will keep you company while budgeting!",
            font=self.normal_font,
            bg='white',
            fg=self.colors['text']
        ).pack(pady=5)
        
        pet_types = {
            'cat': '🐱 Cute Cat',
            'dog': '🐶 Happy Dog',
            'bunny': '🐰 Fluffy Bunny',
            'bear': '🐻 Teddy Bear',
            'penguin': '🐧 Cool Penguin'
        }
        
        current_pet = self.data.get('pet_type', 'cat')
        
        pet_buttons_frame = tk.Frame(pet_card, bg='white')
        pet_buttons_frame.pack(pady=10)
        
        for pet_type, pet_label in pet_types.items():
            is_selected = pet_type == current_pet
            btn = tk.Button(
                pet_buttons_frame,
                text=f"{'✓ ' if is_selected else ''}{pet_label}",
                command=lambda p=pet_type: self.change_pet(p),
                bg=self.colors['success'] if is_selected else self.colors['info'],
                fg='white',
                font=self.normal_font,
                relief=tk.FLAT,
                padx=15,
                pady=8,
                cursor='hand2'
            )
            btn.pack(side=tk.LEFT, padx=5)
        
        tk.Label(
            pet_card,
            text="Your pet will animate and move around to keep you relaxed! 😊",
            font=self.small_font,
            bg='white',
            fg=self.colors['light_text']
        ).pack(pady=10, padx=20)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def show_currency_change_dialog(self):
        """Show dialog to change currency"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Change Currency")
        dialog.geometry("450x400")
        dialog.configure(bg=self.colors['bg'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(
            dialog,
            text="💱 Select Currency",
            font=self.title_font,
            bg=self.colors['bg'],
            fg=self.colors['primary']
        ).pack(pady=20)
        
        form_frame = self.create_card(dialog)
        form_frame.pack(pady=20, padx=30, fill=tk.BOTH, expand=True)
        
        currency_var = tk.StringVar(value=self.current_currency)
        
        for code, info in self.currencies.items():
            tk.Radiobutton(
                form_frame,
                text=f"{info['symbol']} {info['name']} ({code})",
                variable=currency_var,
                value=code,
                font=self.normal_font,
                bg='white',
                activebackground='white',
                selectcolor=self.colors['success']
            ).pack(anchor=tk.W, padx=30, pady=10)
        
        def save_currency():
            self.current_currency = currency_var.get()
            self.data['currency'] = self.current_currency
            self.save_data()
            dialog.destroy()
            messagebox.showinfo("Success! ✓", "Currency updated successfully!")
            self.show_settings()
        
        btn_frame = tk.Frame(dialog, bg=self.colors['bg'])
        btn_frame.pack(pady=20)
        
        self.create_button(btn_frame, "✅ Save", save_currency, 'success').pack(side=tk.LEFT, padx=10)
        self.create_button(btn_frame, "❌ Cancel", dialog.destroy, 'light_text').pack(side=tk.LEFT, padx=10)
    
    def change_theme(self, theme_name):
        """Change the color theme"""
        self.current_theme = theme_name
        self.data['theme'] = theme_name
        self.save_data()
        self.load_theme()
        messagebox.showinfo(
            "Theme Changed! 🎨",
            f"Theme changed to {theme_name.replace('_', ' ').title()}!\nRestarting app to apply changes..."
        )
        # Refresh the app
        self.root.configure(bg=self.colors['bg'])
        self.show_settings()
    
    def change_pet(self, pet_type):
        """Change the pet companion"""
        self.data['pet_type'] = pet_type
        self.save_data()
        messagebox.showinfo("Pet Changed! 🐾", f"Your new companion is ready to help you budget!")
        self.show_settings()
    
    def add_dashboard_pet(self, parent):
        """Add animated pet to dashboard"""
        pet_type = self.data.get('pet_type', 'cat')
        
        # Create canvas for pet in bottom right corner
        pet_canvas = tk.Canvas(parent, width=120, height=120, bg=self.colors['bg'], highlightthickness=0)
        pet_canvas.place(relx=0.95, rely=0.95, anchor=tk.SE)
        
        # Animation variables
        bounce_offset = [0]
        frame_count = [0]
        
        def animate_pet():
            pet_canvas.delete("all")
            
            # Bounce animation
            bounce_offset[0] = math.sin(frame_count[0] * 0.1) * 5
            base_y = 60 + bounce_offset[0]
            
            if pet_type == 'cat':
                self.draw_cat(pet_canvas, 60, base_y, frame_count[0])
            elif pet_type == 'dog':
                self.draw_dog(pet_canvas, 60, base_y, frame_count[0])
            elif pet_type == 'bunny':
                self.draw_bunny(pet_canvas, 60, base_y, frame_count[0])
            elif pet_type == 'bear':
                self.draw_bear(pet_canvas, 60, base_y, frame_count[0])
            elif pet_type == 'penguin':
                self.draw_penguin(pet_canvas, 60, base_y, frame_count[0])
            
            frame_count[0] += 1
            pet_canvas.after(50, animate_pet)
        
        animate_pet()
    
    def draw_cat(self, canvas, x, y, frame):
        """Draw animated cat"""
        # Body
        canvas.create_oval(x-20, y+10, x+20, y+40, fill=self.colors['primary'], outline="")
        # Head
        canvas.create_oval(x-15, y-15, x+15, y+15, fill=self.colors['primary'], outline="")
        # Ears
        canvas.create_polygon(x-12, y-10, x-15, y-25, x-5, y-12, fill=self.colors['primary'])
        canvas.create_polygon(x+12, y-10, x+15, y-25, x+5, y-12, fill=self.colors['primary'])
        # Eyes (blinking)
        eye_size = 4 if (frame // 30) % 2 == 0 else 1
        canvas.create_oval(x-8, y-5, x-8+eye_size, y-5+eye_size, fill="white")
        canvas.create_oval(x+4, y-5, x+4+eye_size, y-5+eye_size, fill="white")
        # Tail (wagging)
        tail_angle = math.sin(frame * 0.15) * 15
        canvas.create_arc(x+15, y+15, x+35, y+35, start=tail_angle, extent=90, 
                         style=tk.ARC, width=3, outline=self.colors['primary'])
    
    def draw_dog(self, canvas, x, y, frame):
        """Draw animated dog"""
        # Body
        canvas.create_oval(x-20, y+10, x+20, y+40, fill=self.colors['secondary'], outline="")
        # Head
        canvas.create_oval(x-15, y-15, x+15, y+15, fill=self.colors['secondary'], outline="")
        # Ears (floppy)
        canvas.create_oval(x-20, y-5, x-10, y+10, fill=self.colors['secondary'], outline="")
        canvas.create_oval(x+10, y-5, x+20, y+10, fill=self.colors['secondary'], outline="")
        # Eyes
        canvas.create_oval(x-8, y-5, x-4, y-1, fill="black")
        canvas.create_oval(x+4, y-5, x+8, y-1, fill="black")
        # Nose
        canvas.create_oval(x-3, y+2, x+3, y+8, fill="black")
        # Tail (wagging fast)
        tail_angle = math.sin(frame * 0.3) * 25
        canvas.create_line(x+18, y+25, x+30+tail_angle, y+20, width=3, fill=self.colors['secondary'])
    
    def draw_bunny(self, canvas, x, y, frame):
        """Draw animated bunny"""
        # Body
        canvas.create_oval(x-18, y+10, x+18, y+40, fill=self.colors['success'], outline="")
        # Head
        canvas.create_oval(x-14, y-10, x+14, y+20, fill=self.colors['success'], outline="")
        # Long ears
        ear_wiggle = math.sin(frame * 0.1) * 3
        canvas.create_oval(x-10, y-35+ear_wiggle, x-5, y-5, fill=self.colors['success'], outline="")
        canvas.create_oval(x+5, y-35-ear_wiggle, x+10, y-5, fill=self.colors['success'], outline="")
        # Eyes
        canvas.create_oval(x-7, y, x-3, y+4, fill="black")
        canvas.create_oval(x+3, y, x+7, y+4, fill="black")
        # Nose
        canvas.create_oval(x-2, y+8, x+2, y+12, fill="pink")
    
    def draw_bear(self, canvas, x, y, frame):
        """Draw animated bear"""
        # Body
        canvas.create_oval(x-22, y+10, x+22, y+45, fill=self.colors['info'], outline="")
        # Head
        canvas.create_oval(x-16, y-12, x+16, y+18, fill=self.colors['info'], outline="")
        # Ears
        canvas.create_oval(x-18, y-18, x-10, y-10, fill=self.colors['info'], outline="")
        canvas.create_oval(x+10, y-18, x+18, y-10, fill=self.colors['info'], outline="")
        # Eyes
        canvas.create_oval(x-8, y-3, x-4, y+1, fill="black")
        canvas.create_oval(x+4, y-3, x+8, y+1, fill="black")
        # Snout
        canvas.create_oval(x-6, y+4, x+6, y+14, fill="#DEB887", outline="")
        canvas.create_oval(x-2, y+8, x+2, y+12, fill="black")
    
    def draw_penguin(self, canvas, x, y, frame):
        """Draw animated penguin"""
        # Body
        canvas.create_oval(x-18, y+5, x+18, y+45, fill="black", outline="")
        # Belly
        canvas.create_oval(x-12, y+15, x+12, y+40, fill="white", outline="")
        # Head
        canvas.create_oval(x-14, y-10, x+14, y+15, fill="black", outline="")
        # Eyes
        canvas.create_oval(x-8, y-2, x-4, y+2, fill="white", outline="")
        canvas.create_oval(x+4, y-2, x+8, y+2, fill="white", outline="")
        canvas.create_oval(x-7, y-1, x-5, y+1, fill="black")
        canvas.create_oval(x+5, y-1, x+7, y+1, fill="black")
        # Beak
        beak_move = math.sin(frame * 0.1) * 2
        canvas.create_polygon(x, y+3, x-4, y+8+beak_move, x+4, y+8+beak_move, fill="orange")
        # Wings (flapping)
        wing_angle = math.sin(frame * 0.15) * 10
        canvas.create_oval(x-22, y+15+wing_angle, x-10, y+30, fill="black", outline="")
        canvas.create_oval(x+10, y+15+wing_angle, x+22, y+30, fill="black", outline="")


def main():
    root = tk.Tk()
    app = BudgetPlannerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()












































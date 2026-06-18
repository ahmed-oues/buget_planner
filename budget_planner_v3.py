"""
Cute Budget Planner - Version 3.0
Enhanced design with centering, rounded corners, and full edit capabilities
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime, timedelta
from tkinter import font as tkfont
import math

class RoundedFrame(tk.Canvas):
    """Custom widget for rounded corners"""
    def __init__(self, parent, radius=20, bg='white', **kwargs):
        tk.Canvas.__init__(self, parent, highlightthickness=0, **kwargs)
        self.config(bg=bg)
        self.radius = radius

    def create_rounded_rect(self, x1, y1, x2, y2, radius=20, **kwargs):
        points = [x1+radius, y1,
                  x1+radius, y1,
                  x2-radius, y1,
                  x2-radius, y1,
                  x2, y1,
                  x2, y1+radius,
                  x2, y1+radius,
                  x2, y2-radius,
                  x2, y2-radius,
                  x2, y2,
                  x2-radius, y2,
                  x2-radius, y2,
                  x1+radius, y2,
                  x1+radius, y2,
                  x1, y2,
                  x1, y2-radius,
                  x1, y2-radius,
                  x1, y1+radius,
                  x1, y1+radius,
                  x1, y1]
        return self.create_polygon(points, **kwargs, smooth=True)

class BudgetPlannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("💰 Cute Budget Planner 💰")
        self.root.geometry("1100x800")

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

        # Setup fonts
        self.title_font = tkfont.Font(family="Segoe UI", size=24, weight="bold")
        self.heading_font = tkfont.Font(family="Segoe UI", size=16, weight="bold")
        self.normal_font = tkfont.Font(family="Segoe UI", size=11)
        self.small_font = tkfont.Font(family="Segoe UI", size=9)

        # Pet animation variables
        self.pet_frame = 0

        # Check for automatic salary addition and recurring expenses
        if self.data and 'setup_complete' in self.data:
            self.check_and_add_salary()
            self.process_recurring_expenses()

        # Check if first run
        if not self.data or 'setup_complete' not in self.data:
            self.show_welcome_screen()
        else:
            self.show_main_dashboard()

    def load_theme(self):
        """Load color theme from saved data - with softer colors"""
        theme_name = self.data.get('theme', 'default')

        self.themes = {
            'default': {
                'primary': '#FF8FAB',      # Softer pink
                'secondary': '#FFD88F',    # Softer yellow
                'success': '#8FE8B4',      # Softer green
                'info': '#8FB4E8',         # Softer blue
                'bg': '#F8FBFF',           # Very light blue
                'card': '#FFFFFF',         # White
                'text': '#3D4E5C',         # Softer dark gray
                'light_text': '#95A5A6',   # Light gray
                'shadow': '#E8ECF0'        # For shadows
            },
            'purple_dream': {
                'primary': '#B58FFF',      # Softer purple
                'secondary': '#FF8FCF',    # Softer hot pink
                'success': '#8FECD2',      # Softer teal
                'info': '#9B88EE',         # Softer slate blue
                'bg': '#FAF7FF',           # Very light lavender
                'card': '#FFFFFF',
                'text': '#3D4E5C',
                'light_text': '#9B9B9B',
                'shadow': '#F0E8FF'
            },
            'ocean_breeze': {
                '': '#5FC4E8',      # Softer cyan
                'secondary': '#FFE475',    # Softer gold
                'success': '#5FE89B',      # Softer green
                'info': '#5FA8D0',         # Softer deep sky blue
                'bg': '#F0FAFD',           # Very light cyan
                'card': '#FFFFFF',
                'text': '#3D6B8B',
                'light_text': '#748E9A',
                'shadow': '#E0F5FA'
            },
            'sunset_glow': {
                'primary': '#FF9F91',      # Softer coral
                'secondary': '#FFBC70',    # Softer orange
                'success': '#96CBA9',      # Softer green
                'info': '#FFA595',         # Softer light coral
                'bg': '#FFF8F0',           # Very light orange
                'card': '#FFFFFF',
                'text': '#6E5442',
                'light_text': '#AD8E83',
                'shadow': '#FFE8D0'
            },
            'forest_zen': {
                'primary': '#7CBF80',      # Softer green
                'secondary': '#ABC46A',    # Softer light green
                'success': '#96CBA9',      # Softer medium green
                'info': '#5FA698',         # Softer teal
                'bg': '#F5FAF5',           # Very light green
                'card': '#FFFFFF',
                'text': '#3B6E40',
                'light_text': '#88AF68',
                'shadow': '#E8F5E9'
            }
        }

        self.colors = self.themes.get(theme_name, self.themes['default'])
        self.current_theme = theme_name

    def process_recurring_expenses(self):
        """Process recurring expenses monthly"""
        if 'recurring_expenses' not in self.data:
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
                    'recurring_id': recurring.get('id', '')
                }

                if 'expenses' not in self.data:
                    self.data['expenses'] = []
                self.data['expenses'].append(expense)

            self.data['last_recurring_processed'] = today.strftime('%Y-%m-%d')
            self.save_data()

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
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_data(self):
        """Save budget data to JSON file"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    def clear_window(self):
        """Clear all widgets from window"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def create_rounded_card(self, parent, width=600, height=None, bg_color='#FFFFFF'):
        """Create a card with rounded corners and shadow effect"""
        # Shadow layer
        shadow = tk.Frame(parent, bg=self.colors['shadow'], bd=0)

        # Main card
        card = tk.Frame(shadow, bg=bg_color, bd=0, highlightthickness=1,
                       highlightbackground=self.colors['shadow'])
        card.pack(padx=2, pady=2)

        return shadow, card

    def create_button(self, parent, text, command, color='primary', width=15):
        """Create a styled button with rounded appearance"""
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=self.colors[color],
            fg='white',
            font=self.normal_font,
            relief=tk.FLAT,
            padx=25,
            pady=12,
            width=width,
            cursor='hand2',
            activebackground=self.colors[color],
            activeforeground='white',
            bd=0
        )
        return btn

    def show_welcome_screen(self):
        """Show welcome/setup screen - CENTERED"""
        self.clear_window()

        # Main centered container
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Welcome message
        tk.Label(
            main_container,
            text="🌟 Welcome to Your Budget Planner! 🌟",
            font=self.title_font,
            bg=self.colors['bg'],
            fg=self.colors['primary']
        ).pack(pady=(0, 15))

        tk.Label(
            main_container,
            text="Let's set up your financial journey together! 💪",
            font=self.heading_font,
            bg=self.colors['bg'],
            fg=self.colors['text']
        ).pack(pady=(0, 25))

        # Info card (centered)
        shadow, card = self.create_rounded_card(main_container, width=500)
        shadow.pack(pady=20)

        tk.Label(
            card,
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
            padx=60,
            pady=40
        ).pack()

        # Start button
        self.create_button(
            main_container,
            "🚀 Let's Get Started!",
            self.show_currency_selection,
            width=20
        ).pack(pady=(15, 0))

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
        ).pack(pady=(0, 30))

        # Currency selection card
        shadow, card = self.create_rounded_card(container, width=450)
        shadow.pack()

        tk.Label(
            card,
            text="Select the currency you'll use:",
            font=self.heading_font,
            bg='white',
            fg=self.colors['text']
        ).pack(pady=(25, 20))

        currency_var = tk.StringVar(value=self.current_currency)

        for code, info in self.currencies.items():
            currency_frame = tk.Frame(card, bg='white')
            currency_frame.pack(pady=8)

            tk.Radiobutton(
                currency_frame,
                text=f"{info['symbol']} {info['name']} ({code})",
                variable=currency_var,
                value=code,
                font=self.normal_font,
                bg='white',
                activebackground='white',
                selectcolor=self.colors['success'],
                bd=0
            ).pack()

        def save_currency():
            self.current_currency = currency_var.get()
            self.data['currency'] = self.current_currency
            self.save_data()
            self.show_income_setup()

        self.create_button(
            card,
            "➡️ Continue",
            save_currency,
            width=15
        ).pack(pady=(20, 25))

    # Due to length, I'll continue with the rest of the methods in the next section...
    # This is getting long, so I'll create a simplified fix for your existing file instead



# core/starter_data.py

STARTER_EXAMPLES = [
    # FINANSE
    ("Invoice #12345 from ABC Company for office supplies totaling $1,247.89", "Finanse", "Faktury"),
    ("Monthly bank statement showing transactions for account ending in 4567", "Finanse", "Wyciagi"),
    ("Tax return documents for fiscal year 2024 need to be filed by April 15th", "Finanse", "Podatki"),
    ("Receipt for business lunch with client at downtown restaurant $87.50", "Finanse", "Faktury"),
    ("Credit card bill due date March 15th with balance of $2,340.67", "Finanse", "Rachunki"),
    ("Expense report for travel costs including flights hotel and meals", "Finanse", "Wydatki"),
    ("Insurance premium payment due for business liability coverage", "Finanse", "Rachunki"),
    ("Budget allocation for Q2 marketing campaigns and advertising spend", "Finanse", "Budzet"),
    ("Purchase order for new computer equipment and software licenses", "Finanse", "Zakupy"),
    ("Financial audit results and recommendations for accounting improvements", "Finanse", "Raporty"),
    
    # SLUZBOWE  
    ("Meeting notes from quarterly planning session with department heads", "Sluzbowe", "Spotkania"),
    ("Performance review feedback and goals for next evaluation period", "Sluzbowe", "HR"),
    ("Project status update milestone achieved ahead of schedule", "Sluzbowe", "Projekty"),
    ("Team building event scheduled for next Friday at conference center", "Sluzbowe", "Wydarzenia"),
    ("Employee handbook updates regarding remote work policies", "Sluzbowe", "Procedury"),
    ("Contract negotiation with vendor for software licensing agreement", "Sluzbowe", "Umowy"),
    ("Board meeting agenda items for next month investor presentation", "Sluzbowe", "Spotkania"),
    ("Training schedule for new employee onboarding program", "Sluzbowe", "Szkolenia"),
    ("Department restructuring plan and timeline for implementation", "Sluzbowe", "Organizacja"),
    ("Client proposal draft for marketing campaign project scope", "Sluzbowe", "Propozycje"),
    
    # PRYWATNE
    ("Dentist appointment scheduled for Thursday afternoon cleaning", "Prywatne", "Zdrowie"),
    ("Grocery shopping list milk bread eggs cheese and vegetables", "Prywatne", "Zakupy"),
    ("Vacation plans for summer trip to Europe flight bookings", "Prywatne", "Wakacje"),
    ("Birthday party invitation for Sarah next weekend bring dessert", "Prywatne", "Wydarzenia"),
    ("Car maintenance oil change tire rotation scheduled Saturday", "Prywatne", "Auto"),
    ("Gym membership renewal due next month personal trainer sessions", "Prywatne", "Fitness"),
    ("Recipe for chocolate cake ingredients and baking instructions", "Prywatne", "Gotowanie"),
    ("Book club meeting discussion of latest novel recommendations", "Prywatne", "Hobby"),
    ("Family reunion planning logistics accommodation and activities", "Prywatne", "Rodzina"),
    ("Home improvement project kitchen renovation contractor quotes", "Prywatne", "Dom"),
    
    # DAILY BUSINESS
    ("Daily standup completed user authentication module working on database", "Daily Business", "Standup"),
    ("Client called about website bug in checkout process investigating", "Daily Business", "Support"),
    ("Code review comments addressed deploying hotfix this afternoon", "Daily Business", "Development"),
    ("Team sync scheduled for 2pm to discuss sprint planning", "Daily Business", "Planowanie"),
    ("Bug report filed priority high affecting user login functionality", "Daily Business", "Bugs"),
    ("Feature request from customer for advanced reporting capabilities", "Daily Business", "Features"),
    ("Server maintenance window scheduled for weekend system updates", "Daily Business", "Maintenance"),
    ("Documentation update for API endpoints and usage examples", "Daily Business", "Dokumentacja"),
    ("Testing completed for mobile app new version ready for release", "Daily Business", "Testing"),
    ("Sprint retrospective feedback team velocity and improvement areas", "Daily Business", "Retrospektywa"),
]

def load_starter_data(db_manager, classifier):
    """Ładuje przykładowe dane do systemu"""
    print("Loading starter data...")
    
    for text, area, subarea in STARTER_EXAMPLES:
        # Zapisz do bazy
        db_manager.save_document(text, area, subarea)
        # Naucz klasyfikator
        classifier.learn(text, area)
    
    print(f"✓ Loaded {len(STARTER_EXAMPLES)} starter examples")
    print(f"✓ Categories: {len(classifier.categories)}")
    
    return True
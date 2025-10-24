import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'home_screen.dart';
import 'analytics_screen.dart';
import 'insights_screen.dart';
import 'chatbot_screen.dart';
import 'account_screen.dart';
import '../providers/transaction_provider.dart';

class MainNavigation extends StatefulWidget {
  const MainNavigation({Key? key}) : super(key: key);

  @override
  State<MainNavigation> createState() => _MainNavigationState();
}

class _MainNavigationState extends State<MainNavigation> {
  int _selectedIndex = 0;
  int _previousIndex = 0;

  final List<Widget> _screens = [
    const HomeScreen(),
    const AnalyticsScreen(),
    const InsightsScreen(),
    const AccountScreen(),
  ];

  void _onItemTapped(int index) {
    // If switching to analytics tab from another tab, refresh data
    if (index == 1 && _selectedIndex != 1) {
      // Refresh transactions when switching to analytics tab
      Provider.of<TransactionProvider>(context, listen: false).fetchTransactions();
    }
    
    setState(() {
      _previousIndex = _selectedIndex;
      _selectedIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _screens[_selectedIndex],
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          Navigator.push(
            context,
            MaterialPageRoute(builder: (context) => const ChatbotScreen()),
          );
        },
        backgroundColor: Colors.deepPurple,
        child: const Icon(Icons.chat, color: Colors.white),
        tooltip: 'Ask Financial Assistant',
      ),
      bottomNavigationBar: BottomNavigationBar(
        type: BottomNavigationBarType.fixed,
        items: const <BottomNavigationBarItem>[
          BottomNavigationBarItem(
            icon: Icon(Icons.home),
            label: 'Home',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.analytics),
            label: 'Analytics',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.psychology),
            label: 'AI Insights',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.account_circle),
            label: 'Account',
          ),
        ],
        currentIndex: _selectedIndex,
        selectedItemColor: Colors.deepPurple,
        onTap: _onItemTapped,
      ),
    );
  }
}

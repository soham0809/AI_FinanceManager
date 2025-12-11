import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/transaction_provider.dart';
import '../widgets/connection_status_card.dart';
import '../widgets/sms_permission_card.dart';
import '../widgets/auto_sms_scanner.dart';
import '../widgets/sms_test_card.dart';
import '../widgets/ml_categorization_card.dart';
import '../widgets/transaction_list.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  bool _hasSMSPermissions = false;

  @override
  void initState() {
    super.initState();
    // Check connection and fetch transactions when app starts
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final provider = context.read<TransactionProvider>();
      provider.checkConnection().then((_) {
        provider.fetchTransactions();
      });
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'AI Financial Copilot',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        backgroundColor: Theme.of(context).colorScheme.primaryContainer,
        actions: [
          IconButton(
            icon: const Icon(Icons.cleaning_services),
            tooltip: 'Remove Duplicates',
            onPressed: () {
              context.read<TransactionProvider>().removeDuplicateTransactions();
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Duplicate transactions removed')),
              );
            },
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              context.read<TransactionProvider>().checkConnection();
            },
          ),
        ],
      ),
      body: Consumer<TransactionProvider>(
        builder: (context, provider, child) {
          return RefreshIndicator(
            onRefresh: () async {
              await provider.checkConnection();
              return provider.fetchTransactions();
            },
            child: SingleChildScrollView(
              physics: const AlwaysScrollableScrollPhysics(),
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Connection Status Card
                  const ConnectionStatusCard(),
                  const SizedBox(height: 16),
                  
                  // SMS Permission Card
                  SMSPermissionCard(
                    onPermissionChanged: (hasPermissions) {
                      setState(() {
                        _hasSMSPermissions = hasPermissions;
                      });
                    },
                  ),
                  const SizedBox(height: 16),
                  
                  // Auto SMS Scanner (only show if permissions granted)
                  if (_hasSMSPermissions) ...[
                    const AutoSMSScanner(),
                    const SizedBox(height: 16),
                  ],
                  
                  // SMS Test Card (for manual testing)
                  const SMSTestCard(),
                  const SizedBox(height: 16),
                  
                  // ML Categorization Card
                  const MLCategorizationCard(),
                  const SizedBox(height: 16),
                  
                  // Quick Stats
                  if (provider.transactions.isNotEmpty) ...[
                    _buildQuickStats(provider),
                    const SizedBox(height: 16),
                    const Text(
                      'Recent Transactions',
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),
                  ],
                  
                  // Transaction List
                  const TransactionList(),
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildQuickStats(TransactionProvider provider) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Text(
                  'Quick Stats',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const Spacer(),
                IconButton(
                  tooltip: 'Reload',
                  icon: const Icon(Icons.refresh),
                  onPressed: () async {
                    final p = context.read<TransactionProvider>();
                    await p.checkConnection();
                    await p.fetchTransactions();
                    if (mounted) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('Quick stats reloaded')),
                      );
                    }
                  },
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: _buildStatItem(
                    'Total Spent',
                    '₹${provider.totalSpending.toStringAsFixed(2)}',
                    Colors.red,
                    Icons.arrow_downward,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: _buildStatItem(
                    'Total Income',
                    '₹${provider.totalIncome.toStringAsFixed(2)}',
                    Colors.green,
                    Icons.arrow_upward,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            _buildStatItem(
              'Transactions',
              provider.transactions.length.toString(),
              Colors.blue,
              Icons.receipt,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatItem(String label, String value, Color color, IconData icon) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          Icon(icon, color: color, size: 20),
          const SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  label,
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey[600],
                  ),
                ),
                Text(
                  value,
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: color,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

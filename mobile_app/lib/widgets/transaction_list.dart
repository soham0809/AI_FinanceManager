import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../providers/transaction_provider.dart';
import '../models/transaction.dart';

class TransactionList extends StatelessWidget {
  const TransactionList({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer<TransactionProvider>(
      builder: (context, provider, child) {
        if (provider.isLoading && provider.transactions.isEmpty) {
          return const Center(
            child: Padding(
              padding: EdgeInsets.all(32.0),
              child: CircularProgressIndicator(),
            ),
          );
        }

        if (provider.transactions.isEmpty) {
          return Card(
            child: Padding(
              padding: const EdgeInsets.all(32.0),
              child: Column(
                children: [
                  Icon(
                    Icons.receipt_long,
                    size: 64,
                    color: Colors.grey[400],
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'No Transactions Yet',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: Colors.grey[600],
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Test the SMS parser above to see transactions appear here!',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      color: Colors.grey[500],
                    ),
                  ),
                ],
              ),
            ),
          );
        }

        return ListView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: provider.transactions.length,
          itemBuilder: (context, index) {
            final transaction = provider.transactions[index];
            return TransactionCard(transaction: transaction);
          },
        );
      },
    );
  }
}

class TransactionCard extends StatelessWidget {
  final Transaction transaction;

  const TransactionCard({
    super.key,
    required this.transaction,
  });

  @override
  Widget build(BuildContext context) {
    final isDebit = transaction.isDebit;
    final color = isDebit ? Colors.red : Colors.green;
    final icon = isDebit ? Icons.arrow_downward : Icons.arrow_upward;

    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: color.withOpacity(0.1),
          child: Icon(icon, color: color),
        ),
        title: Text(
          transaction.vendor,
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              DateFormat('MMM dd, yyyy • hh:mm a').format(transaction.parsedDate),
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey[600],
              ),
            ),
            const SizedBox(height: 4),
            Row(
              children: [
                // Category badge
                if (transaction.category != null) ...[
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                    decoration: BoxDecoration(
                      color: Colors.blue.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      transaction.category!,
                      style: TextStyle(
                        fontSize: 10,
                        color: Colors.blue.shade700,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ),
                  const SizedBox(width: 6),
                ],
                // Payment method badge
                if (transaction.paymentMethod != null) ...[
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                    decoration: BoxDecoration(
                      color: _getPaymentMethodColor(transaction.paymentMethod!).withOpacity(0.1),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      transaction.paymentMethod!,
                      style: TextStyle(
                        fontSize: 10,
                        color: _getPaymentMethodColor(transaction.paymentMethod!),
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ),
                  const SizedBox(width: 6),
                ],
                // Subscription badge
                if (transaction.isSubscription) ...[
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                    decoration: BoxDecoration(
                      color: Colors.purple.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(
                          Icons.subscriptions,
                          size: 10,
                          color: Colors.purple.shade700,
                        ),
                        const SizedBox(width: 2),
                        Text(
                          transaction.subscriptionService ?? 'Subscription',
                          style: TextStyle(
                            fontSize: 10,
                            color: Colors.purple.shade700,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ],
            ),
          ],
        ),
        trailing: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              '${isDebit ? '-' : '+'}${transaction.formattedAmount}',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
            const SizedBox(width: 8),
            _DeleteActionButton(transaction: transaction),
          ],
        ),
        onTap: () => _showTransactionDetails(context, transaction),
      ),
    );
  }

  void _showTransactionDetails(BuildContext context, Transaction transaction) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (context) => TransactionDetailsSheet(transaction: transaction),
    );
  }

  Color _getPaymentMethodColor(String paymentMethod) {
    switch (paymentMethod.toLowerCase()) {
      case 'upi':
        return Colors.orange;
      case 'credit card':
        return Colors.red;
      case 'debit card':
        return Colors.green;
      case 'net banking':
        return Colors.indigo;
      default:
        return Colors.grey;
    }
  }
}

class _DeleteActionButton extends StatelessWidget {
  final Transaction transaction;
  const _DeleteActionButton({super.key, required this.transaction});

  @override
  Widget build(BuildContext context) {
    final provider = Provider.of<TransactionProvider>(context, listen: false);
    final lowConfidence = transaction.confidence < 0.85;
    final color = lowConfidence ? Colors.red : Colors.grey.shade700;

    Future<void> doDelete() async {
      await provider.deleteTransaction(transaction);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Transaction deleted')),
      );
    }

    return IconButton(
      icon: Icon(Icons.delete_outline, color: color),
      tooltip: lowConfidence ? 'Delete (low confidence)' : 'Delete',
      onPressed: () async {
        if (lowConfidence) {
          await doDelete();
        } else {
          final confirmed = await showDialog<bool>(
            context: context,
            builder: (ctx) => AlertDialog(
              title: const Text('Delete transaction?'),
              content: const Text('This transaction has high confidence. Do you want to delete it?'),
              actions: [
                TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancel')),
                TextButton(onPressed: () => Navigator.pop(ctx, true), child: const Text('Delete')),
              ],
            ),
          );
          if (confirmed == true) {
            await doDelete();
          }
        }
      },
    );
  }
}

class TransactionDetailsSheet extends StatelessWidget {
  final Transaction transaction;

  const TransactionDetailsSheet({
    super.key,
    required this.transaction,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(24),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Text(
                'Transaction Details',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const Spacer(),
              IconButton(
                onPressed: () => Navigator.pop(context),
                icon: const Icon(Icons.close),
              ),
            ],
          ),
          const SizedBox(height: 16),
          
          _buildDetailRow('Vendor', transaction.vendor),
          _buildDetailRow('Amount', transaction.formattedAmount),
          // _buildDetailRow('Type', transaction.transactionType.toUpperCase()), // Removed - field no longer exists
          _buildDetailRow(
            'Date', 
            DateFormat('MMMM dd, yyyy at hh:mm a').format(transaction.parsedDate),
          ),
          if (transaction.category != null)
            _buildDetailRow('Category', transaction.category!),
          
          // Enhanced fields
          if (transaction.paymentMethod != null)
            _buildDetailRow('Payment Method', transaction.paymentMethod!),
          if (transaction.merchantCategory != null)
            _buildDetailRow('Merchant Category', transaction.merchantCategory!),
          if (transaction.isSubscription)
            _buildDetailRow('Subscription Service', transaction.subscriptionService ?? 'Unknown'),
          if (transaction.cardLastFour != null)
            _buildDetailRow('Card Last 4 Digits', '****${transaction.cardLastFour}'),
          if (transaction.upiTransactionId != null)
            _buildDetailRow('UPI Transaction ID', transaction.upiTransactionId!),
          if (transaction.isRecurring)
            _buildDetailRow('Recurring Payment', 'Yes'),
          
          _buildDetailRow('Confidence Score', '${(transaction.confidence * 100).toStringAsFixed(1)}%'),
          
          const SizedBox(height: 16),
          const Text(
            'Raw SMS:',
            style: TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: 16,
            ),
          ),
          const SizedBox(height: 8),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.grey.shade100,
              borderRadius: BorderRadius.circular(8),
            ),
            child: Text(
              transaction.smsText,
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey[700],
              ),
            ),
          ),
          
          const SizedBox(height: 24),
        ],
      ),
    );
  }

  Widget _buildDetailRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 80,
            child: Text(
              '$label:',
              style: TextStyle(
                fontWeight: FontWeight.w500,
                color: Colors.grey[600],
              ),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: const TextStyle(fontWeight: FontWeight.w500),
            ),
          ),
        ],
      ),
    );
  }
}

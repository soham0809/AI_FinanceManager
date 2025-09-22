import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/transaction_provider.dart';

class ConnectionStatusCard extends StatelessWidget {
  const ConnectionStatusCard({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer<TransactionProvider>(
      builder: (context, provider, child) {
        return Card(
          color: provider.isConnected 
              ? Colors.green.shade50 
              : Colors.red.shade50,
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Row(
              children: [
                Icon(
                  provider.isConnected 
                      ? Icons.cloud_done 
                      : Icons.cloud_off,
                  color: provider.isConnected 
                      ? Colors.green 
                      : Colors.red,
                  size: 32,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        provider.isConnected 
                            ? 'Connected to Server' 
                            : 'Server Disconnected',
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          color: provider.isConnected 
                              ? Colors.green.shade700 
                              : Colors.red.shade700,
                        ),
                      ),
                      Text(
                        provider.isConnected 
                            ? 'AI Financial Co-Pilot is ready!' 
                            : 'Please start the backend server',
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey[600],
                        ),
                      ),
                      if (provider.error != null) ...[
                        const SizedBox(height: 4),
                        Text(
                          provider.error!,
                          style: TextStyle(
                            fontSize: 11,
                            color: Colors.red.shade600,
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
                if (provider.isLoading)
                  const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  ),
              ],
            ),
          ),
        );
      },
    );
  }
}

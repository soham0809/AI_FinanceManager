import 'package:flutter/material.dart';
import '../services/sms_service.dart';

class SMSPermissionCard extends StatefulWidget {
  final Function(bool) onPermissionChanged;
  
  const SMSPermissionCard({
    super.key,
    required this.onPermissionChanged,
  });

  @override
  State<SMSPermissionCard> createState() => _SMSPermissionCardState();
}

class _SMSPermissionCardState extends State<SMSPermissionCard> {
  final SMSService _smsService = SMSService();
  bool _hasPermissions = false;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _checkPermissions();
  }

  Future<void> _checkPermissions() async {
    setState(() => _isLoading = true);
    
    try {
      final hasPermissions = await _smsService.hasPermissions();
      setState(() {
        _hasPermissions = hasPermissions;
        _isLoading = false;
      });
      widget.onPermissionChanged(hasPermissions);
    } catch (e) {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _requestPermissions() async {
    setState(() => _isLoading = true);
    
    try {
      final granted = await _smsService.requestPermissions();
      setState(() {
        _hasPermissions = granted;
        _isLoading = false;
      });
      widget.onPermissionChanged(granted);
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(granted 
                ? 'SMS permissions granted! Auto-tracking enabled.' 
                : 'SMS permissions denied. Manual entry only.'),
            backgroundColor: granted ? Colors.green : Colors.orange,
          ),
        );
      }
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error requesting permissions: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      color: _hasPermissions ? Colors.green.shade50 : Colors.orange.shade50,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  _hasPermissions ? Icons.sms : Icons.sms_failed,
                  color: _hasPermissions ? Colors.green : Colors.orange,
                  size: 32,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        _hasPermissions 
                            ? 'SMS Auto-Tracking Enabled' 
                            : 'SMS Permissions Required',
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          color: _hasPermissions 
                              ? Colors.green.shade700 
                              : Colors.orange.shade700,
                        ),
                      ),
                      Text(
                        _hasPermissions 
                            ? 'Automatically capturing transaction SMS' 
                            : 'Grant SMS access for zero-touch expense tracking',
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey[600],
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            
            if (!_hasPermissions) ...[
              const SizedBox(height: 12),
              const Text(
                'Why do we need SMS access?',
                style: TextStyle(
                  fontWeight: FontWeight.w600,
                  fontSize: 14,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                '• Automatically read bank & UPI transaction alerts\n'
                '• Zero manual entry - expenses tracked instantly\n'
                '• Works with all major Indian banks and UPI apps\n'
                '• Your SMS data stays private and secure',
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.grey[600],
                ),
              ),
              const SizedBox(height: 12),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: _isLoading ? null : _requestPermissions,
                  icon: _isLoading 
                      ? const SizedBox(
                          width: 16,
                          height: 16,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Icon(Icons.security),
                  label: Text(_isLoading ? 'Requesting...' : 'Grant SMS Access'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.orange.shade600,
                    foregroundColor: Colors.white,
                  ),
                ),
              ),
            ] else ...[
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: _isLoading ? null : _checkPermissions,
                      icon: const Icon(Icons.refresh),
                      label: const Text('Refresh Status'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.green.shade600,
                        foregroundColor: Colors.white,
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }
}

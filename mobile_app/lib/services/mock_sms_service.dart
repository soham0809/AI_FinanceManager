import 'dart:math';

class MockSmsService {
  static final List<String> _mockSmsMessages = [
    "Your account debited by Rs.250 at Zomato on 2025-01-10. Available balance: Rs.5,750. UPI Ref: 123456789",
    "Rs.1200 debited from your SBI account for Amazon purchase on 2025-01-09. Balance: Rs.8,500",
    "HDFC Bank: Rs.450 spent at McDonald's on 2025-01-08. Card ending 1234. Available limit: Rs.45,000",
    "UPI payment of Rs.180 to Uber successful. Transaction ID: UPI123456. ICICI Bank",
    "Your account credited with Rs.5000 salary on 2025-01-07. Total balance: Rs.15,750",
    "Paytm: Rs.320 paid to Swiggy for food delivery. Wallet balance: Rs.2,180",
    "AXIS Bank alert: Rs.800 withdrawn from ATM at City Mall on 2025-01-06",
    "GPay payment Rs.150 to Metro Card recharge successful. PhonePe wallet",
    "Rs.2500 debited for electricity bill payment via HDFC NetBanking",
    "Your SBI account debited Rs.75 for SMS charges on 2025-01-05",
    "BookMyShow: Rs.600 for movie tickets paid via UPI. ICICI Bank",
    "Rs.1800 spent at Reliance Digital using HDFC debit card",
    "Ola ride payment Rs.120 successful via PhonePe UPI",
    "Your account credited Rs.500 cashback from Amazon Pay",
    "Rs.350 debited for Spotify Premium subscription via Google Pay"
  ];

  static final List<String> _categories = [
    'Food & Dining',
    'Shopping', 
    'Transportation',
    'Entertainment',
    'Bills & Utilities',
    'Healthcare',
    'Education'
  ];

  static final List<String> _vendors = [
    'Zomato', 'Swiggy', 'McDonald\'s', 'KFC', 'Starbucks',
    'Amazon', 'Flipkart', 'Myntra', 'Reliance Digital',
    'Uber', 'Ola', 'Metro Card', 'Rapido',
    'BookMyShow', 'Netflix', 'Spotify', 'YouTube Premium',
    'Apollo Pharmacy', 'MedPlus', 'Practo'
  ];

  /// Get a random mock SMS message
  static String getRandomSms() {
    final random = Random();
    return _mockSmsMessages[random.nextInt(_mockSmsMessages.length)];
  }

  /// Generate a custom SMS with random data
  static String generateCustomSms() {
    final random = Random();
    final amount = (random.nextInt(2000) + 50).toDouble();
    final vendor = _vendors[random.nextInt(_vendors.length)];
    final date = DateTime.now().subtract(Duration(days: random.nextInt(30)));
    
    final templates = [
      "Your account debited by Rs.$amount at $vendor on ${date.toString().split(' ')[0]}. Available balance: Rs.${(random.nextInt(50000) + 1000)}",
      "Rs.$amount spent at $vendor on ${date.toString().split(' ')[0]}. Card ending ${1000 + random.nextInt(9000)}",
      "UPI payment of Rs.$amount to $vendor successful. Transaction ID: UPI${random.nextInt(999999999)}",
      "$vendor: Rs.$amount paid successfully. Wallet balance: Rs.${random.nextInt(10000) + 500}"
    ];
    
    return templates[random.nextInt(templates.length)];
  }

  /// Get multiple mock SMS messages
  static List<String> getMockSmsMessages({int count = 5}) {
    final random = Random();
    final messages = <String>[];
    
    for (int i = 0; i < count; i++) {
      if (random.nextBool()) {
        messages.add(getRandomSms());
      } else {
        messages.add(generateCustomSms());
      }
    }
    
    return messages;
  }

  /// Simulate real-time SMS arrival
  static Stream<String> simulateSmsStream() async* {
    while (true) {
      await Future.delayed(Duration(seconds: 10 + Random().nextInt(20)));
      yield generateCustomSms();
    }
  }
}

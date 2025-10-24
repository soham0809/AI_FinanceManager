class NetworkConfig {
  // 🌐 CONFIGURATION MODE
  // Set to true for production (Cloudflare Tunnel)
  // Set to false for local development
  static const bool useCloudflare = true;
  
  // ============================================
  // 🏠 LOCAL DEVELOPMENT CONFIGURATION
  // ============================================
  // Run 'ipconfig' and update this IP address when your network changes
  static const String localServerIp = '192.168.0.100';
  static const int localServerPort = 8000;
  
  // ============================================
  // ☁️ CLOUDFLARE TUNNEL CONFIGURATION
  // ============================================
  // Your Cloudflare Tunnel URL (update this after setup)
  static const String cloudflareUrl = 'ai-finance.sohamm.xyz';
  static const bool useHttps = true; // Always true for Cloudflare
  
  // ============================================
  // 🔧 AUTO-GENERATED URLs (Don't modify)
  // ============================================
  static String get serverIp => useCloudflare ? cloudflareUrl : localServerIp;
  static int get serverPort => useCloudflare ? (useHttps ? 443 : 80) : localServerPort;
  static String get protocol => (useCloudflare && useHttps) ? 'https' : 'http';
  
  static String get baseUrl => useCloudflare 
      ? '$protocol://$cloudflareUrl' 
      : 'http://$localServerIp:$localServerPort';
      
  static String get healthUrl => '$baseUrl/health';
  static String get authUrl => '$baseUrl/auth';
  static String get apiUrl => '$baseUrl/v1';
  
  // Network settings
  static const int connectionTimeout = 15; // seconds (increased for Cloudflare)
  static const int receiveTimeout = 20; // seconds (increased for Cloudflare)
  
  // Debug info
  static void printConfig() {
    print('🌐 Network Configuration:');
    print('   Mode: ${useCloudflare ? "☁️ Cloudflare Tunnel (Production)" : "🏠 Local Development"}');
    print('   Protocol: $protocol');
    print('   Server: $serverIp');
    print('   Port: $serverPort');
    print('   Base URL: $baseUrl');
    print('   Auth URL: $authUrl');
    print('   API URL: $apiUrl');
  }
}

package com.example.student_finance_copilot;

import io.flutter.embedding.android.FlutterActivity;
import io.flutter.embedding.engine.FlutterEngine;
import io.flutter.plugin.common.MethodChannel;
import java.util.List;

public class MainActivity extends FlutterActivity {
    private static final String CHANNEL = "sms_reader";
    private SmsReader smsReader;

    @Override
    public void configureFlutterEngine(FlutterEngine flutterEngine) {
        super.configureFlutterEngine(flutterEngine);
        
        smsReader = new SmsReader(this);
        
        new MethodChannel(flutterEngine.getDartExecutor().getBinaryMessenger(), CHANNEL)
            .setMethodCallHandler(
                (call, result) -> {
                    switch (call.method) {
                        case "getAllSMS":
                            try {
                                List<String> messages = smsReader.getAllSmsMessages();
                                result.success(messages);
                            } catch (Exception e) {
                                result.error("SMS_ERROR", "Failed to read SMS: " + e.getMessage(), null);
                            }
                            break;
                        case "getTransactionSMS":
                            try {
                                Integer limit = call.argument("limit");
                                if (limit == null) limit = 100;
                                List<String> messages = smsReader.getTransactionSmsMessages(limit);
                                result.success(messages);
                            } catch (Exception e) {
                                result.error("SMS_ERROR", "Failed to read transaction SMS: " + e.getMessage(), null);
                            }
                            break;
                        default:
                            result.notImplemented();
                            break;
                    }
                }
            );
    }
}

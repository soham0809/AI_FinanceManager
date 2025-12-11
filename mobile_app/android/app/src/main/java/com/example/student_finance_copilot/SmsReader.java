package com.example.student_finance_copilot;

import android.content.Context;
import android.database.Cursor;
import android.net.Uri;
import android.provider.Telephony;
import java.util.ArrayList;
import java.util.List;

public class SmsReader {
    private Context context;

    public SmsReader(Context context) {
        this.context = context;
    }

    public List<String> getAllSmsMessages() {
        List<String> smsList = new ArrayList<>();
        
        try {
            Uri uri = Uri.parse("content://sms/inbox");
            String[] projection = new String[] { "body", "address", "date" };
            
            Cursor cursor = context.getContentResolver().query(
                uri, 
                projection, 
                null, 
                null, 
                "date DESC LIMIT 1000"
            );
            
            if (cursor != null && cursor.moveToFirst()) {
                do {
                    String body = cursor.getString(cursor.getColumnIndexOrThrow("body"));
                    String address = cursor.getString(cursor.getColumnIndexOrThrow("address"));
                    long date = cursor.getLong(cursor.getColumnIndexOrThrow("date"));
                    
                    // Format: "FROM: address | DATE: timestamp | BODY: message"
                    String formattedSms = "FROM: " + address + " | DATE: " + date + " | BODY: " + body;
                    smsList.add(formattedSms);
                } while (cursor.moveToNext());
                
                cursor.close();
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        
        return smsList;
    }
    
    public List<String> getTransactionSmsMessages(int limit) {
        List<String> transactionSmsList = new ArrayList<>();
        
        try {
            android.util.Log.d("SmsReader", "Starting SMS scan for transactions, limit: " + limit);
            
            Uri uri = Uri.parse("content://sms/inbox");
            String[] projection = new String[] { "body", "address", "date" };
            
            // First try to get all SMS to check total count
            Cursor allCursor = context.getContentResolver().query(
                uri, 
                projection, 
                null,
                null,
                "date DESC"
            );
            
            int totalSmsCount = 0;
            if (allCursor != null) {
                totalSmsCount = allCursor.getCount();
                allCursor.close();
            }
            
            android.util.Log.d("SmsReader", "Total SMS in inbox: " + totalSmsCount);
            
            // Filter for transaction-related SMS with broader criteria
            String selection = "body LIKE ? OR body LIKE ? OR body LIKE ? OR body LIKE ? OR body LIKE ? OR body LIKE ? OR body LIKE ? OR body LIKE ? OR body LIKE ? OR body LIKE ?";
            String[] selectionArgs = {"%debited%", "%credited%", "%UPI%", "%bank%", "%₹%", "%Rs%", "%paid%", "%received%", "%transaction%", "%amount%"};
            
            Cursor cursor = context.getContentResolver().query(
                uri, 
                projection, 
                selection,
                selectionArgs,
                "date DESC LIMIT " + limit
            );
            
            if (cursor != null) {
                android.util.Log.d("SmsReader", "Transaction SMS cursor count: " + cursor.getCount());
                
                if (cursor.moveToFirst()) {
                    do {
                        String body = cursor.getString(cursor.getColumnIndexOrThrow("body"));
                        String address = cursor.getString(cursor.getColumnIndexOrThrow("address"));
                        long date = cursor.getLong(cursor.getColumnIndexOrThrow("date"));
                        
                        // Format: "FROM: address | DATE: timestamp | BODY: message"
                        String formattedSms = "FROM: " + address + " | DATE: " + date + " | BODY: " + body;
                        transactionSmsList.add(formattedSms);
                        
                        android.util.Log.d("SmsReader", "Added SMS from: " + address + " body preview: " + body.substring(0, Math.min(50, body.length())));
                    } while (cursor.moveToNext());
                }
                
                cursor.close();
            } else {
                android.util.Log.e("SmsReader", "Cursor is null - no SMS access permission or SMS provider unavailable");
            }
            
            android.util.Log.d("SmsReader", "Final transaction SMS count: " + transactionSmsList.size());
            
        } catch (Exception e) {
            android.util.Log.e("SmsReader", "Error reading SMS: " + e.getMessage());
            e.printStackTrace();
        }
        
        return transactionSmsList;
    }
}

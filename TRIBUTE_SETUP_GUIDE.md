# Tribute.tg Integration Setup Guide

## For Client: Step-by-Step Instructions

### Step 1: Register on Tribute.tg
1. Go to https://tribute.tg/docs
2. Create merchant account
3. Verify phone number

### Step 2: Merchant Setup
1. Fill business profile
2. Add business information
3. Upload logo

### Step 3: Get API Keys
1. Login to Dashboard → Settings → API
2. Generate API Key and Webhook Secret
3. **CRITICAL:** Save them securely!

### Step 4: Configure Webhook
- URL: `https://your-domain.railway.app/api/webhooks/tribute`
- Events: `payment.succeeded`, `payment.failed`
- Test webhook via interface

### Step 5: Create Products
- PRO subscription: 300 RUB / 30 days (30000 kopecks)
- ULTRA subscription: 600 RUB / 30 days (60000 kopecks)

### Step 6: ENV Variables
```bash
TRIBUTE_API_KEY=your_api_key_here
TRIBUTE_WEBHOOK_SECRET=your_webhook_secret_here
TRIBUTE_MERCHANT_ID=your_merchant_id_here
```

### Step 7: Test Integration
- Use Tribute test mode
- Check webhook on Railway
- Validate payment logs

### Step 8: Monitoring
- Dashboard → Transactions
- Setup error alerts
- Weekly reports

### Step 9: Final Checklist
- ✅ API keys configured
- ✅ Webhook active and tested
- ✅ Products created with correct prices
- ✅ Test payment successful
- ✅ Logs show correct processing

## Support
If issues arise, contact Tribute support: https://tribute.tg/support

# Example Output 3: Correct Abstention / "Need More Info" Path

## Test Case: Vague Complaint with Missing Information

**Ticket ID:** TRICKY-006  
**Category:** Ambiguous - Missing Critical Info  
**Date:** January 2024

---

## INPUT

### Customer Ticket:
```
I ordered something last month and it never arrived. I want my money back. 
This is unacceptable!
```

### Order Context:
```json
{
  "order_context": null
}
```

---

## OUTPUT

### === INTERNAL ANALYSIS ===

**CLASSIFICATION:** Shipping & Delivery - Lost Package (Confidence: 70%)

**RATIONALE:**
1. Customer claims non-delivery but provides no verifiable order information
2. Policy requires order number, delivery address verification, and tracking check before processing claims (POL-002 §6.1)
3. Cannot proceed without critical information - must request details before resolution

**ASSUMPTIONS / NOT IN POLICY:**
- Order number unknown
- Purchase date vague ("last month" = could be 5-35 days ago)
- Item details unknown
- Shipping address unknown
- Tracking status unknown
- Payment method unknown

**METRICS:**
- Citation Coverage: 100%
- Unsupported Claims: 0/3
- Decision Confidence: 0% (insufficient information to make decision)

**POLICY REFERENCES:**
- Shipping and Delivery Policy (Document: POL-002, Section: 6.1 - Package Marked Delivered)
- Shipping and Delivery Policy (Document: POL-002, Section: 6.2 - Investigation Process)

**DECISION:** NEEDS MORE INFO

**CLARIFYING QUESTIONS:**
1. What is your order number? (Required to locate your order in our system)
2. What was the approximate date you placed this order?
3. What item(s) did you order?

**NEXT STEPS (Internal):**
1. Request order number from customer
2. Once order located, check tracking status
3. Verify delivery address on file
4. Follow lost package protocol per POL-002 §6.1-6.2
5. If tracking shows delivered, follow 24-hour wait + investigation process
6. If tracking shows not delivered, process refund or replacement

---

### === CUSTOMER RESPONSE ===

Dear Customer,

Thank you for contacting us. I'm sorry to hear you haven't received your order - I'd like to help resolve this as quickly as possible.

To locate your order and investigate what happened, I need a few key pieces of information:

**Required Information:**
1. **Order Number** - This is the confirmation number sent to your email when you placed the order (format: ORD-XXXXX or similar)
2. **Approximate Order Date** - When did you place this order? (You mentioned "last month" - a specific date or date range would help)
3. **Item Description** - What product(s) did you order?

**Optional but Helpful:**
4. Email address used for the order (if different from the one you're contacting us from)
5. Shipping address where the order should have been delivered

Once I have your order number, I can:
- Check the tracking status and delivery confirmation
- Verify the shipping address on file
- Investigate with the carrier if needed
- Process a refund or replacement based on what we find

According to our Shipping Policy, if a package shows as delivered but you didn't receive it, we'll file an investigation with the carrier and work toward a resolution. If tracking shows the package was never delivered, we can process a refund or send a replacement right away.

Please reply with your order number and the other details above, and I'll get this sorted out for you immediately.

Best regards,  
Customer Support Team

---

## EVALUATION NOTES

**Why This Example Shows Correct Abstention:**

1. ✅ **Insufficient Information Identified:** System correctly recognized missing critical data
2. ✅ **No Assumptions Made:** Did not guess order details, dates, or amounts
3. ✅ **Specific Questions Asked:** Requested exactly what's needed (order number, date, items)
4. ✅ **Policy-Based Requirements:** Questions based on POL-002 investigation requirements
5. ✅ **No Hallucination:** Did not invent order details or make promises without data
6. ✅ **Clear Path Forward:** Explained what happens once information is provided
7. ✅ **Professional Tone:** Maintained empathy despite vague complaint

**Missing Information:**
- ❌ Order number (CRITICAL - cannot locate order)
- ❌ Specific purchase date (vague "last month")
- ❌ Item details (unknown what was ordered)
- ❌ Shipping address (cannot verify delivery location)
- ❌ Tracking information (cannot check delivery status)
- ❌ Payment method (cannot process refund without order)

**Why System Could NOT Proceed:**
- Policy POL-002 §6.1 requires order number to check tracking
- Policy POL-002 §6.2 requires verification before investigation
- Cannot determine if package was delivered, lost, or stolen without tracking
- Cannot process refund without order details
- Cannot verify customer identity without order information

**Correct Decision Path:**
1. ❌ **WRONG:** Approve refund without verification (would be hallucination/fraud risk)
2. ❌ **WRONG:** Deny request (customer may have legitimate claim)
3. ❌ **WRONG:** Escalate (not needed - just missing basic info)
4. ✅ **CORRECT:** Request required information (NEEDS MORE INFO)

**Assessment Criteria Met:**
- ✅ Ambiguous case identified correctly
- ✅ Missing information flagged (6 critical pieces)
- ✅ Clarifying questions asked (3 required questions)
- ✅ No unsupported claims or invented details
- ✅ Proper abstention from making decision without data
- ✅ Clear explanation of what's needed and why
- ✅ Policy citations provided (POL-002 §6.1, §6.2)

**What Happens Next:**
Once customer provides order number:
1. System can re-process with complete information
2. Check tracking status
3. Apply appropriate policy (delivered vs not delivered)
4. Provide specific resolution based on facts

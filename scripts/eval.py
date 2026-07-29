import asyncio
import os
import sys

# Ensure backend modules can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.services.llm_service import llm_service

TEST_SET = [
    {
        "id": 1,
        "text": "Invoice #1001 from CloudNet Inc to Acme Corp on 2024-01-10. 1x Enterprise Server Subscription ($500.00). Tax: $50.00. Total: $550.00 USD."
    },
    {
        "id": 2,
        "text": "Receipt from Cafe Deluxe. Date: May 12, 2024. Client: Alex. Items: 2 Espressos ($4.00 each = $8.00), 1 Croissant ($4.50). Subtotal: $12.50. Tax: $1.00. Grand Total: $13.50."
    },
    {
        "id": 3,
        "text": "Billed to John Smith by DevStudio LLC (Inv-998) on 03/15/2024. Web Design Services (10 hours @ $80/hr = $800.00). Total Due: $800.00 USD."
    },
    {
        "id": 4,
        "text": "Invoice INV-2024-X12. Vendor: Fast Logistics. Customer: Global Traders. Date: June 1, 2024. Shipping Fee: $250. Total: $250 USD."
    },
    {
        "id": 5,
        "text": "Messy text: Hey boss, here is the billing info for Office Supplies Co to us (Beta Inc) dated 2024-02-20. We got 10 Paper Reams for $50 total and 2 Ink Cartridges for $100. Total came out to $150 plus $15 tax, total $165."
    },
    {
        "id": 6,
        "text": "Invoice #771. From Tech Gadgets to Sarah Connor on 2024-04-04. 1x Keyboard ($120), 1x Mouse ($50). Subtotal: $170. Total: $170."
    },
    {
        "id": 7,
        "text": "Simple invoice: Vendor AI Solutions, Date 2024-07-01, Client Corp. Model fine-tuning (1 unit at $1500). Total amount $1500 USD."
    },
    {
        "id": 8,
        "text": "Billing note: Inv 404 from DataCorp to Alpha Ltd. Date: 10 Jan 2024. Database storage 50GB ($50). Tax $5. Final total $55."
    },
    {
        "id": 9,
        "text": "Receipt 8823. Cleaners Inc. Customer: Mary. Date: 2024-06-15. Dry cleaning service x3 ($45 total). Paid $45."
    },
    {
        "id": 10,
        "text": "Invoice #9000. SaaS Tool Inc -> Heavy User. 2024-08-01. Pro Tier Subscription ($29.99). Total: $29.99 USD."
    }
]

async def run_eval():
    print("\n" + "="*70)
    print("🚀 RUNNING PROMPT EVALUATION LOOP ON 10-ITEM TEST SET")
    print("="*70 + "\n")

    passed = 0
    total_tokens = 0
    total_cost = 0.0

    for idx, test in enumerate(TEST_SET, 1):
        print(f"[{idx}/10] Testing Item ID {test['id']}...")
        result = await llm_service.extract_invoice(test["text"])
        
        success = result["success"]
        attempts = result["attempts"]
        tokens = result["tokens_used"]["total_tokens"]
        cost = result["estimated_cost"]

        total_tokens += tokens
        total_cost += cost

        if success:
            passed += 1
            vendor = result['data'].vendor_name
            total_amt = result['data'].total_amount
            print(f"   ✅ PASS (Attempts: {attempts} | Vendor: {vendor} | Total: ${total_amt} | Tokens: {tokens})")
        else:
            print(f"   ❌ FAIL (Error: {result['error']})")

    print("\n" + "="*70)
    print("📊 EVALUATION SUMMARY")
    print("="*70)
    print(f"Pass Rate:        {passed}/10 ({passed/10*100:.1f}%)")
    print(f"Total Tokens:     {total_tokens}")
    print(f"Est. Total Cost:  ${total_cost:.6f}")
    print("="*70 + "\n")

if __name__ == "__main__":
    asyncio.run(run_eval())
import pandas as pd
import json
import time
import os
from zoho_client import ZohoDeskClient
import sentiment_engine
import utils

def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

def main():
    config = load_config()
    zoho_config = config['ZOHO']
    excel_config = config['EXCEL']

    input_file = excel_config['INPUT_FILE']
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        return

    print(f"📊 Loading Excel: {input_file}")
    df = pd.read_excel(input_file)

    # Initialize columns if they don't exist
    required_cols = [
        "Inbound Thread", "Outbound Thread", "Sentiment Score",
        "Sentiment Label", "Emotion", "Complaint Risk Level",
        "Ticket Category", "processing_status"
    ]
    for col in required_cols:
        if col not in df.columns:
            df[col] = ""

    # Identify ticket and contact columns
    ticket_col = next((c for c in df.columns if c.lower() in ["ticket id", "ticketnumber", "ticket number"]), None)
    contact_col = next((c for c in df.columns if c.lower() in ["contact name", "contactname", "contact name (ticket)", "customer name"]), None)

    if not ticket_col:
        print("❌ Could not find Ticket ID column.")
        return

    zoho = ZohoDeskClient(zoho_config)
    
    print(f"🚀 Starting Processing...")
    
    processed_count = 0
    
    for index, row in df.iterrows():
        # Skip already processed
        if pd.notna(row['processing_status']) and str(row['processing_status']).strip() != "":
            continue

        ticket_number = str(row[ticket_col]).strip()
        contact_name = str(row[contact_col]).strip() if contact_col and pd.notna(row[contact_col]) else ""

        if not ticket_number or ticket_number == "nan":
            df.at[index, 'processing_status'] = "Skipped - No Ticket"
            continue

        print(f"\n🎫 Ticket {ticket_number} | Contact: {contact_name}")

        try:
            ticket_info = zoho.get_ticket_by_number(ticket_number)

            if "data" not in ticket_info or not ticket_info["data"]:
                df.at[index, 'processing_status'] = "Failed - Ticket Not Found"
                continue

            ticket_id = ticket_info["data"][0]["id"]
            threads_list = zoho.get_threads_list(ticket_id)

            inbound_list, outbound_list = zoho.extract_full_threads(ticket_id, threads_list, contact_name)

            inbound_text = utils.build_thread_text(inbound_list)
            outbound_text = utils.build_thread_text(outbound_list)

            df.at[index, 'Inbound Thread'] = inbound_text
            df.at[index, 'Outbound Thread'] = outbound_text

            print(f"✅ Fetched: {len(inbound_list)} inbound, {len(outbound_list)} outbound")

            if inbound_text.strip():
                print(f"🧠 Analyzing sentiment...")
                res = sentiment_engine.analyze_sentiment(inbound_text)
                
                df.at[index, 'Sentiment Score'] = res['sentiment_score']
                df.at[index, 'Sentiment Label'] = res['sentiment_label']
                df.at[index, 'Emotion'] = res['emotion']
                df.at[index, 'Complaint Risk Level'] = res['complaint_risk_level']
                df.at[index, 'Ticket Category'] = res['ticket_category']
                df.at[index, 'processing_status'] = "Completed"
            else:
                df.at[index, 'processing_status'] = "Completed - No Inbound"

            processed_count += 1
            
            # Save progress periodically
            if processed_count % 5 == 0:
                df.to_excel(excel_config['OUTPUT_FILE'], index=False)
                print(f"💾 Progress saved to {excel_config['OUTPUT_FILE']}")

            time.sleep(2) # Avoid rate limits

        except Exception as e:
            print(f"❌ Error processing ticket {ticket_number}: {e}")
            df.at[index, 'processing_status'] = f"Failed - {str(e)}"
            continue

    # Final save
    df.to_excel(excel_config['OUTPUT_FILE'], index=False)
    print(f"\n✅ Processing complete. Saved to: {excel_config['OUTPUT_FILE']}")

if __name__ == "__main__":
    main()

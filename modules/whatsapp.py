from playwright.sync_api import sync_playwright
from modules.parser import parse_payment_message
from modules.database import save_payment

USER_DATA_DIR = "data/user_data"


# =========================================================
# LOAD WHATSAPP CHATS
# =========================================================

def get_whatsapp_chats():

    chats = []

    with sync_playwright() as p:

        context = p.chromium.launch_persistent_context(
            USER_DATA_DIR,
            headless=False
        )

        # Use existing page if available
        if context.pages:
            page = context.pages[0]
        else:
            page = context.new_page()

        print("Opening WhatsApp Web...")

        page.goto("https://web.whatsapp.com")

        # Wait for full page load
        page.wait_for_load_state("networkidle")

        # Wait for QR/login if needed
        page.wait_for_timeout(15000)

        try:

            # Wait for sidebar
            page.wait_for_selector(
                'div[aria-label="Chat list"]',
                timeout=60000
            )

            print("WhatsApp loaded successfully.")

        except Exception as e:

            print("WhatsApp not loaded.")
            print(e)

            context.close()

            return []

        # Extra wait for rendering
        page.wait_for_timeout(5000)

        try:

            # Read visible titles
            chat_titles = page.locator(
                'span[dir="auto"]'
            )

            count = chat_titles.count()

            print(f"Found {count} titles")

            for i in range(count):

                try:

                    text = chat_titles.nth(i).inner_text().strip()

                    # Filter unwanted UI text
                    if (
                        text
                        and len(text) < 40
                        and text not in chats
                        and text.lower() not in [
                            "you",
                            "typing...",
                            "online",
                            "search",
                            "meta ai"
                        ]
                    ):

                        chats.append(text)

                except:
                    pass

        except Exception as e:

            print("Chat extraction error:", e)

        context.close()

    # Remove duplicates
    chats = list(dict.fromkeys(chats))

    return chats


# =========================================================
# SCAN SELECTED CHAT
# =========================================================

def scan_selected_chat(target_chat):

    with sync_playwright() as p:

        context = p.chromium.launch_persistent_context(
            USER_DATA_DIR,
            headless=False
        )

        # Use existing page
        if context.pages:
            page = context.pages[0]
        else:
            page = context.new_page()

        print("Opening WhatsApp Web...")

        page.goto("https://web.whatsapp.com")

        # Wait for page load
        page.wait_for_load_state("networkidle")

        # Wait for QR/login
        page.wait_for_timeout(15000)

        try:

            page.wait_for_selector(
                'div[aria-label="Chat list"]',
                timeout=60000
            )

            print("WhatsApp loaded successfully.")

        except Exception as e:

            print("WhatsApp not loaded.")
            print(e)

            context.close()

            return

        # =====================================================
        # OPEN CHAT
        # =====================================================

        try:

            print(f"Searching for chat: {target_chat}")

            # Focus page
            page.click("body")

            page.wait_for_timeout(1000)

            # Open search
            page.keyboard.press("Control+Alt+/")

            page.wait_for_timeout(2000)

            # Type target chat
            page.keyboard.type(target_chat)

            page.wait_for_timeout(3000)

            # Open chat
            page.keyboard.press("Enter")

            print("Chat opened successfully.")

        except Exception as e:

            print("Error opening chat.")
            print(e)

            context.close()

            return

        # =====================================================
        # WAIT FOR CHAT LOAD
        # =====================================================

        page.wait_for_timeout(5000)

        # =====================================================
        # READ MESSAGES
        # =====================================================

        try:

            messages = page.locator(
                'div[data-testid="msg-container"]'
            )

            count = messages.count()

            print(f"Found {count} message containers")

            saved_count = 0

            for i in range(count):

                try:

                    msg_container = messages.nth(i)

                    # -------------------------------------------------
                    # FULL MESSAGE TEXT
                    # -------------------------------------------------

                    full_text = msg_container.inner_text().strip()

                    print("\nFULL MESSAGE:")
                    print(full_text)

                    # -------------------------------------------------
                    # EXTRACT WHATSAPP TIMESTAMP
                    # -------------------------------------------------

                    whatsapp_datetime = ""

                    try:

                        pre_plain = msg_container.locator(
                            '[data-pre-plain-text]'
                        ).first

                        if pre_plain.count() > 0:

                            whatsapp_datetime = pre_plain.get_attribute(
                                "data-pre-plain-text"
                            )

                            print("WHATSAPP DATETIME:")
                            print(whatsapp_datetime)

                    except Exception as time_error:

                        print(
                            "Timestamp extraction error:",
                            time_error
                        )

                    # -------------------------------------------------
                    # DETECT PAYREQ
                    # -------------------------------------------------

                    if "PAYREQ" in full_text.upper():

                        print("PAYREQ DETECTED")

                        parsed = parse_payment_message(full_text)

                        if parsed:

                            saved = save_payment(
                                parsed,
                                whatsapp_datetime
                            )

                            if saved:

                                saved_count += 1

                                print("SAVED:", parsed)

                except Exception as inner_error:

                    print(
                        "Message read error:",
                        inner_error
                    )

            print(
                f"\nTotal PAYREQ entries saved: {saved_count}"
            )

        except Exception as e:

            print("Error scanning messages:", e)

        context.close()

from playwright.sync_api import sync_playwright
from modules.parser import parse_payment_message
from modules.database import save_payment
import os


# =========================================================
# USER DATA DIRECTORY
# =========================================================

USER_DATA_DIR = "data/user_data"

os.makedirs(USER_DATA_DIR, exist_ok=True)


# =========================================================
# CREATE CLOUD-SAFE CONTEXT
# =========================================================

def create_browser_context(playwright):

    context = playwright.chromium.launch_persistent_context(

        USER_DATA_DIR,

        headless=True,

        args=[
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--disable-setuid-sandbox",
            "--disable-extensions",
            "--disable-infobars",
            "--disable-blink-features=AutomationControlled"
        ]
    )

    return context


# =========================================================
# LOAD WHATSAPP CHATS
# =========================================================

def get_whatsapp_chats():

    chats = []

    try:

        with sync_playwright() as p:

            context = create_browser_context(p)

            # =================================================
            # PAGE
            # =================================================

            if context.pages:
                page = context.pages[0]
            else:
                page = context.new_page()

            print("Opening WhatsApp Web...")

            page.goto(
                "https://web.whatsapp.com",
                wait_until="networkidle"
            )

            page.wait_for_timeout(10000)

            # =================================================
            # CHECK LOGIN
            # =================================================

            try:

                page.wait_for_selector(
                    'div[aria-label="Chat list"]',
                    timeout=30000
                )

                print("WhatsApp loaded successfully.")

            except:

                print("WhatsApp login required.")

                context.close()

                return []

            # =================================================
            # EXTRA WAIT
            # =================================================

            page.wait_for_timeout(5000)

            # =================================================
            # FETCH CHAT TITLES
            # =================================================

            try:

                chat_titles = page.locator(
                    'span[dir="auto"]'
                )

                count = chat_titles.count()

                print(f"Found {count} titles")

                for i in range(count):

                    try:

                        text = chat_titles.nth(i).inner_text().strip()

                        # -----------------------------------------
                        # FILTER UI TEXTS
                        # -----------------------------------------

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

    except Exception as e:

        print("Playwright Error:", e)

    # =====================================================
    # REMOVE DUPLICATES
    # =====================================================

    chats = list(dict.fromkeys(chats))

    return chats


# =========================================================
# SCAN SELECTED CHAT
# =========================================================

def scan_selected_chat(target_chat):

    try:

        with sync_playwright() as p:

            context = create_browser_context(p)

            # =================================================
            # PAGE
            # =================================================

            if context.pages:
                page = context.pages[0]
            else:
                page = context.new_page()

            print("Opening WhatsApp Web...")

            page.goto(
                "https://web.whatsapp.com",
                wait_until="networkidle"
            )

            page.wait_for_timeout(10000)

            # =================================================
            # CHECK LOGIN
            # =================================================

            try:

                page.wait_for_selector(
                    'div[aria-label="Chat list"]',
                    timeout=30000
                )

                print("WhatsApp loaded successfully.")

            except:

                print("WhatsApp login required.")

                context.close()

                return

            # =================================================
            # OPEN CHAT
            # =================================================

            try:

                print(f"Searching for chat: {target_chat}")

                page.click("body")

                page.wait_for_timeout(1000)

                # Open search
                page.keyboard.press("Control+Alt+/")

                page.wait_for_timeout(2000)

                # Type chat name
                page.keyboard.type(target_chat)

                page.wait_for_timeout(3000)

                # Open chat
                page.keyboard.press("Enter")

                print("Chat opened successfully.")

            except Exception as e:

                print("Error opening chat:", e)

                context.close()

                return

            # =================================================
            # WAIT FOR CHAT LOAD
            # =================================================

            page.wait_for_timeout(5000)

            # =================================================
            # READ MESSAGES
            # =================================================

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

                        # -----------------------------------------
                        # FULL MESSAGE TEXT
                        # -----------------------------------------

                        full_text = msg_container.inner_text().strip()

                        print("\nFULL MESSAGE:")
                        print(full_text)

                        # -----------------------------------------
                        # EXTRACT WHATSAPP DATETIME
                        # -----------------------------------------

                        whatsapp_datetime = ""

                        try:

                            pre_plain = msg_container.locator(
                                '[data-pre-plain-text]'
                            ).first

                            if pre_plain.count() > 0:

                                whatsapp_datetime = (
                                    pre_plain.get_attribute(
                                        "data-pre-plain-text"
                                    )
                                )

                                print("WHATSAPP DATETIME:")
                                print(whatsapp_datetime)

                        except Exception as time_error:

                            print(
                                "Timestamp extraction error:",
                                time_error
                            )

                        # -----------------------------------------
                        # DETECT PAYREQ
                        # -----------------------------------------

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

    except Exception as e:

        print("Playwright Fatal Error:", e)

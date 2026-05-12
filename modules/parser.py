import re


def parse_payment_message(message):

    try:

        print("RAW MESSAGE:")
        print(message)

        # Clean message
        cleaned = message.replace("\n", " ")

        print("CLEANED MESSAGE:")
        print(cleaned)

        # Flexible regex
        pattern = r"PAYREQ\|Amount:(\d+)\|Name[:;]?\s*([A-Za-z ]+)"

        match = re.search(
            pattern,
            cleaned,
            re.IGNORECASE
        )

        if match:

            amount = int(match.group(1))

            name = match.group(2).strip()

            print("MATCH FOUND")
            print(amount, name)

            return {
                "amount": amount,
                "name": name,
                "raw_message": cleaned
            }

        else:

            print("NO MATCH FOUND")

    except Exception as e:

        print("Parser Error:", e)

    return None
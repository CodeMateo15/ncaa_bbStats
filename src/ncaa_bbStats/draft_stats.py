import re

import requests
from bs4 import BeautifulSoup


def _clean(text: str) -> str:
    """Collapse the newlines Baseball Almanac embeds mid-cell from 2026 on.

    Earlier seasons' markup keeps each cell on one line, so this is a no-op
    there and the whole cache stays in one format.
    """
    text = " ".join(text.split())
    text = re.sub(r"\(\s+", "(", text)
    return re.sub(r"\s+\)", ")", text)


def parse_mlb_draft(year: int) -> list[dict]:
    """
    Parses MLB draft results from Baseball Almanac for a given year (1965–2026).
    It strips the final row, which is known to be malformed or misplaced.

    Returns:
        List of dictionaries, one per draft pick.
    """
    if not (1965 <= year <= 2026):
        raise ValueError("Year must be between 1965 and 2026.")

    url = f"https://www.baseball-almanac.com/draft/baseball-draft.php?yr={year}"
    headers = {'User-Agent': 'Mozilla/5.0'}

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("table")
    if not table:
        raise ValueError(f"No draft data table found for {year}.")

    rows = table.find_all("tr")

    # Define expected columns
    column_names = [
        "Round", "Pick", "Phase", "Player Name", "Drafted By", "POS", "Drafted From"
    ]

    # Remove header and incorrect last row
    data_rows = rows[2:-2]

    results = []
    for row in data_rows:
        cols = [_clean(td.get_text(strip=True)) for td in row.find_all("td")]
        if len(cols) != 7:
            continue  # Skip any malformed rows
        record = dict(zip(column_names, cols))
        record["Year"] = year
        results.append(record)

    print(f"Parsed {len(results)} draft picks for {year}.")
    return results

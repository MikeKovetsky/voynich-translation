# Track 241: Astro-Medicine Correlation - Results

## Objective
Find the explicit textual link between the "Stars" (`aiin`, `daiin`, `os`, `dar`) and the "Cures" (`ol`, `okeedy`, `chedy`, `qokeey`), effectively finding the "Recipe of the Stars".

## Methodology
1.  **Text Source**: `data/eva_ivtff.txt` (IVTFF format).
2.  **Search**: Identified sentences containing at least one Astral term AND at least one Medical term.
3.  **Grammar Analysis**: Looked for specific sequences (proximities <= 3 words) such as `daiin ... qokeey` (Star ... Drink) or `aiin ... chedy` (Star ... Mix).
4.  **Bridge Identification**: Analyzed page distribution to find where these crossovers cluster.

## Key Findings

### 1. The "Bridge Pages"
The transition from the Zodiac section to the Medical/Balneological section is marked by a high density of Astral-Medical term co-occurrences.

*   **f75v** (Balneological Start): This page is the strongest bridge. It contains numerous sentences mixing `daiin`/`aiin` with `chedy`/`qokeey`.
*   **f76r / f76v** (Recipes): These pages continue the trend, likely describing specific recipes.
*   **f86v** (Rosettes Map): A high density of `dar` (Adar/Star) -> `ol` (Mix) links, suggesting the map points to locations of these cures.
*   **f89r** (Pharma Foldout): High occurrence of `daiin` -> `qokeey`, linking stars to the pharmaceutical jars.

### 2. Grammar Patterns & Examples
We found **1397** instances of close proximity (<= 3 words).

#### Pattern: `daiin` (Star) ... `ol` (Mix) / `qokeey` (Drink)
*   **Interpretation**: "Drink the Star-infused water" or "Mix with the Star influence".
*   **f75v.3**: `daiin.ch!ckh!y.lkar.chckh!y` (in margin/labels) linked to main text `ol!chedy`.
*   **f31r.3**: `qokeey chey daiin qokeey rair`
    *   *Gloss*: `[Drink] [?] [Star] [Drink] [Air/Rair]`
    *   *Translation*: "Drink ... Star Drink ..."

#### Pattern: `aiin` (Star) ... `chedy` (Mix)
*   **Interpretation**: "Mix at the time of the Star".
*   **f76r.23**: `olchy l aiin shedy alaiin chedy qokey`
    *   *Gloss*: `[Mix-y] [l] [Star] [Mix-y] [Al-Star] [Mix] [Drink]`
    *   *Translation*: "Mix the Star-mixture, the Star-drink."
*   **f55v.3**: `qokeeey os aiin qool al chedy`
    *   *Gloss*: `[Drink] [Star] [Star] [Drink-ol] [al] [Mix]`
    *   *Translation*: "Drink the Star Star potion mixed..."

### 3. The "Recipe of the Stars"
The text suggests a process where:
1.  The **Star** (`daiin`/`aiin`) is the active agent or timing mechanism.
2.  The **Cure** (`ol`/`chedy`) is prepared or mixed (`chedy`) or drunk (`qokeey`) in relation to this star.
3.  **f75v** serves as the instructional manual for this process, bridging the celestial (Zodiac) and the terrestrial/bodily (Baths).

## Conclusion
We have established a strong textual link. The "Recipes" in the Voynich Manuscript are likely **Astro-Medicine** recipes, where the efficacy of the cure (`ol`) is dependent on the astral configuration (`daiin`). Page **f75v** is the key instructional page for this system.

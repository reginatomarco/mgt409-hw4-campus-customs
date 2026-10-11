"""Short GIGACHAD-style product blurbs, built from templates (no AI calls, no cost)."""

import hashlib

RESIDENTIAL_COLLEGES = [
    "Benjamin Franklin", "Berkeley", "Branford", "Davenport", "Ezra Stiles", "Grace Hopper",
    "Jonathan Edwards", "Morse", "Pauli Murray", "Pierson", "Saybrook", "Silliman",
    "Timothy Dwight", "Trumbull",
]
FAMILY = ["Grandma", "Grandpa", "Mom", "Dad", "Aunt", "Uncle", "Brother", "Cousin"]
SPORTS = [
    "Field Hockey", "Ice Hockey", "Track", "Baseball", "Basketball", "Football", "Hockey",
    "Soccer", "Tennis", "Diving", "Fencing", "Sailing", "Squash", "Lacrosse", "Volleyball",
    "Golf", "Swimming",
]

# The theme line says who the product is for; the garment line says why it hits.
THEMES = {
    "harvard": "Harvard sees this and quietly reconsiders its life choices.",
    "family": "Being a Yale {who} isn't a title. It's a rank.",
    "college": "{who} loyalty, worn on the chest. The crest doesn't lie.",
    "school": "Grad school is hard. Looking this good while doing it is harder. You did it anyway.",
    "sport": "Built for {who}. Whether you play or just watch, it reps the same.",
    "bulldog": "Vintage Bulldog energy. Calm, loyal, absolutely unbothered.",
    "generic": "Pure Yale. No gimmicks. Just presence.",
}
GARMENTS = [
    (("fleece", "jacket", "bomber"), ["New Haven winters fear this layer.", "Wind hits it and apologizes."]),
    (("1 4 zip", "quarter"), ["Half business, half beast mode.", "Zip it up for class, zip it down for victory."]),
    (("hood",), ["Hood up, distractions down.", "The 2 a.m. problem-set hoodie. It does not quit."]),
    (("crew", "mockneck"), ["Heavyweight confidence in crewneck form.", "Throw it on and your posture fixes itself."]),
    (("long sleeve", "l s"), ["Sweat-wicking. Excuse-wicking.", "Engineered for people who finish the workout."]),
    (("t shirt", "tee", "heavyweight"), ["Simple tee. Main-character energy.", "Light fabric, heavy aura."]),
]


def _pick(options: list[str], seed: str) -> str:
    return options[int(hashlib.md5(seed.encode()).hexdigest(), 16) % len(options)]


def _theme(name: str) -> str:
    lower = name.lower()
    if "harvard" in lower:
        return THEMES["harvard"]
    for who in FAMILY:
        if f"yale {who.lower()}" in lower:
            return THEMES["family"].format(who=who)
    for who in RESIDENTIAL_COLLEGES:
        if who.lower() in lower:
            return THEMES["college"].format(who=who)
    if "school" in lower:
        return THEMES["school"]
    for who in SPORTS:
        if who.lower() in lower:
            return THEMES["sport"].format(who=who.lower())
    if "bulldog" in lower:
        return THEMES["bulldog"]
    return THEMES["generic"]


def gigachad_blurb(product_id: str, name: str) -> str:
    lower = name.lower()
    garment = next(
        (_pick(lines, product_id) for keys, lines in GARMENTS if any(k in lower for k in keys)),
        "Yale on the outside. Unstoppable on the inside.",
    )
    return f"{garment} {_theme(name)}"

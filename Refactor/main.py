from WikiGraph_Manager import WikiGraph_Manager

def main():
    QIDS = [
    "Q247",         # Half-Life 2
    "Q1299",        # The Beatles
    "Q42",          # Douglas Adams
    "Q30",          # United States
    "Q8338",        # Harry Potter
    "Q140960",      # Marvel Cinematic Universe
    "Q380",         # Star Wars
    "Q317521",      # Elon Musk
    "Q328",         # Wikipedia
    "Q2065",        # Linux
    "Q155",         # Pokémon
    "Q17365",       # Minecraft
    "Q76",          # Barack Obama
    "Q95",          # Google
    "Q93105",       # Iron Man
    "Q84",          # London
    "Q12010",       # Shrek
    "Q134268",      # Breaking Bad
    "Q134231",      # Pokémon Go
    "Q29598584",    # OpenAI
    "Q42",          # Douglas Adams (duplicate for testing)
    "Q42",          
]
    manger = WikiGraph_Manager()
    manger.build(QIDS[0], 2)
    manger.save_all()

main()

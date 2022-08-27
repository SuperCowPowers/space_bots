"""GenerateVoiceLines: Utility Class for Space Bot Voice Line Generation (using text to speech)"""
import pyttsx3


class GenerateVoiceLines:
    """GenerateVoiceLines: Utility Class for Space Bot Voice Line Generation (using text to speech)"""
    def __init__(self, voice='female'):

        # Set up the voice engine
        self.rate = 200
        self.engine = pyttsx3.init()
        voices = self.engine.getProperty('voices')
        # Note: Might also use 17 for female
        self.voice_info = {'male': voices[7].id, 'female': voices[28].id, "squad_leader_1": voices[18].id}

    def save_voice_line(self, tag, voice, line):
        """Have the GenerateVoiceLines say some stuff"""

        # Set the voice
        self.engine.setProperty('voice', self.voice_info[voice])

        # Save this to a file with naming schema
        file_name = f"{tag}_{voice}.mp3"
        print(f"Generating {file_name}...")
        self.engine.save_to_file(line, file_name)

    def run(self):
        self.engine.runAndWait()


# Simple test of the GenerateVoiceLines functionality
def test():
    """Test for GenerateVoiceLines Class"""

    # Create some GenerateVoiceLiness
    gen_lines = GenerateVoiceLines()

    # Lets save off the following voice lines
    voice_lines = {
        'lets_rumble': "Let's get ready to rumble!",
        'won_match': "Nice job! It was tricky in some spots.. but the GigaVerse Mining team pulled it off!",
        'lost_match': "Oh! Tough loss.. Well better luck to the GigaVerse Mining team next time.",
        'great_match': "It's going to be a great match! ... The Zerg are incoming and have started attacking...",
        'mining_zenite': "Miner has started extracting ZeNite...obviously a top priority for GigaVerse Corporation",
        'tank_low': "Tank Low!",
        'tank_down': "Tank Down!",
        'healer_low': "Healer Low!",
        'healer_down': "Healer Down!",
        'miner_low': "Miner Low!",
        'miner_down': "Miner Down!",
        'fighter_low': "Fighter Low!",
        'fighter_down': "Fighter Down!",
        'drone_low': "Drone Low",
        'drone_down': "Drone Down",
        'tank_cast_pain': "Tank casts 'Take the Pain'!",
        'healer_cast_salvation': "Healer casts Salvation!"
    }
    # Announcers
    for voice in ['male', 'female']:
        for tag, line in voice_lines.items():
            gen_lines.save_voice_line(tag, voice, line)
    gen_lines.run()

    # Squad Leaders
    """
    voice_lines = {
        'lets_rock': "Let's Rock!",
        'yee_haw': "Yee Haw!"
    }
    for voice in ['squad_leader_1']:
        for tag, line in voice_lines.items():
            gen_lines.save_voice_line(tag, voice, line)
    gen_lines.run()
    """


if __name__ == "__main__":
    test()

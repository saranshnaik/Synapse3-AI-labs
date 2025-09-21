import random
import math
import matplotlib.pyplot as plt
from midiutil import MIDIFile

class RaagBhairavMelodyGenerator:
    def __init__(self, length=16):
        self.notes = ['S', 'r', 'G', 'm', 'P', 'd', 'N', "S'"]
        self.note_values = {'S': 60, 'r': 61, 'G': 62, 'm': 63, 
                           'P': 64, 'd': 65, 'N': 66, "S'": 67}
        
        self.signature_patterns = [
            ['G', 'm', 'r', 'G'],
            ['r', 'S'],
            ['d', 'P', 'm', 'G'],
            ['G', 'm', 'P', 'd'],
            ['N', 'd', 'P', 'm'],
            ['S', 'r', 'G', 'm'],
            ['m', 'G', 'r', 'S'],
            ['r', 'r', 'S'],
            ['d', 'd', 'P'],
            ['G', 'm', 'd', 'd', 'P'],
            ['G', 'm', 'r', 'r', 'S'],
            ['m', 'P', 'G', 'm', 'P'], 
            ['G', 'P', 'm'], 
            ['G', 'm', 'N', 'd'], 
            ['d', 'N', 'S\''], 
            ['N', 'S\'', 'r\'', 'r\'', 'S\''], 
            ['d', 'd', 'P', 'm', 'P'], 
            ['G', 'm', 'P'], 
            ['G', 'm', 'P', 'P', 'm', 'G', 'm'], 
            ['G', 'm', 'P'], 
            ['G', 'm', 'r', 'S'], 
            ['G', 'm', 'd', 'm', 'P'], 
            ['P', 'm', 'P'], 
            ['d', 'P', 'd', 'N', 'd', 'N', 'S\''], 
            ['r\'', 'r\'', 'G\'', 'm\'', 'r\'', 'S\''], 
            ['N', 'd', 'P'],
            ['d', 'd', 'P', 'm', 'P', 'm', 'G', 'm', 'P'], 
            ['m', 'm', 'r', 'r', 'S']
        ]
        
        self.rhythms = [
            [1.5, 0.5, 1.0, 1.0],
            [1.0, 0.5, 0.5, 1.5, 1.0],
            # [2.0, 1.0, 0.5, 0.5, 1.0],
            [0.5, 0.5, 1.0, 0.5, 1.5],
            # [2.5, 1.0, 2.0],       
        ]

        self.vishranti_sthan = [
            ['S'], ['m'], ['P'], ['d'], ['S\''], ['d'], ['P'], ['r']
        ]

        self.mukhya_ang = [
            ['r', 'r', 'S'],
            ['d', 'd', 'P'],
            ['G', 'm', 'd', 'd', 'P'],
            ['G', 'm', 'r', 'r', 'S'],
            #[',N', 'S']
        ]
        self.aroha_patterns = [
            ['S', 'G', 'm', 'd', 'P'],
            ['G', 'm', 'd', 'N', "S'"]
        ]
        
        self.avaroha_patterns = [
            ["S'", 'N', 'd', 'P'],
            ['P', 'm', 'G', 'm', 'r', 'S'],
            ['G', 'm', 'r', 'S']
        ]
        
        self.length = length
        self.max_iterations = 2000
        
    def create_initial_melody(self):
        """Seed melody with Bhairav motifs and expand with rhythmic cycles"""
        melody = []
        rhythm = random.choice(self.rhythms)

        # Pick a seed motif from mukhya_ang
        base_phrase = random.choice(self.mukhya_ang)

        # Flatten with durations and add oscillation for r/d
        for i, note in enumerate(base_phrase):
            duration = rhythm[i % len(rhythm)] # * 1.3
            melody.append((note, duration))
            if note in ['r', 'd'] and random.random() < 0.5:
                # add oscillation
                melody.append((note, duration * 0.8))

        # Expand: alternate between aroha/avaroha fragments + stepwise moves
        while len(melody) < self.length:
            choice = random.random()
            if choice < 0.3:
                phrase = random.choice(self.aroha_patterns)
            elif choice < 0.6:
                phrase = random.choice(self.avaroha_patterns)
            else:
                phrase = random.choice(self.mukhya_ang)

            for i, note in enumerate(phrase):
                duration = rhythm[(len(melody)+i) % len(rhythm)] * (1.2 if note in ['r','d'] else 1.0)
                melody.append((note, duration))
                if len(melody) >= self.length:
                    break

        # Ensure melody ends on Sa
        melody[-1] = ('S', melody[-1][1])# * 1.5)
        return melody


    def evaluate_melody(self, melody):
        """Score melody based on Bhairav grammar and motif adherence"""
        score = 0
        notes_only = [note for note, _ in melody]
        note_string = ''.join(notes_only)

        # Reward signature patterns
        for pattern in self.mukhya_ang + self.aroha_patterns + self.avaroha_patterns:
            pattern_str = ''.join(pattern)
            if pattern_str in note_string:
                score -= 50  # stronger reward

        # Penalize large leaps
        for i in range(len(melody)-1):
            current_idx = self.notes.index(melody[i][0]) if melody[i][0] in self.notes else 0
            next_idx = self.notes.index(melody[i+1][0]) if melody[i+1][0] in self.notes else 0
            jump_size = abs(current_idx - next_idx)
            if jump_size > 2:
                score += jump_size * 10

        # Strong reward for vadi/samvadi and oscillations
        r_count = sum(1 for note, _ in melody if note == 'r')
        d_count = sum(1 for note, _ in melody if note == 'd')
        score -= r_count * 12
        score -= d_count * 10

        # Reward longer durations on r/d
        # avg_r_duration = sum(duration for note, duration in melody if note == 'r') / max(1, r_count)
        # avg_d_duration = sum(duration for note, duration in melody if note == 'd') / max(1, d_count)
        # if avg_r_duration > 1.2:
        #     score -= 5
        # if avg_d_duration > 1.2:
        #     score -= 5

        # Reward starting and ending on Sa
        if notes_only[0] == 'S':
            score -= 20
        if notes_only[-1] == 'S':
            score -= 20

        # Penalize too many repeated notes in a row
        for i in range(len(notes_only)-2):
            if notes_only[i] == notes_only[i+1] == notes_only[i+2]:
                score += 30

        # Encourage enough note changes
        note_changes = sum(1 for i in range(len(notes_only)-1) if notes_only[i] != notes_only[i+1])
        if note_changes < len(notes_only) * 0.5:
            score += 40

        return score

    def create_variation(self, melody):
        """Create variations emphasizing Bhairav motifs, oscillations, and stepwise movement"""
        new_melody = melody.copy()
        choice = random.random()

        if choice < 0.4:
            # Replace a segment with a motif (mukhya_ang or aroha/avaroha)
            start = random.randint(0, len(new_melody)-5)
            motif = random.choice(self.mukhya_ang + self.aroha_patterns + self.avaroha_patterns)
            for i, note in enumerate(motif):
                if start+i < len(new_melody):
                    dur = new_melody[start+i][1] * (1.3 if note in ['r','d'] else 1.0)
                    new_melody[start+i] = (note, dur)
                else:
                    dur = 1.2 * (1.3 if note in ['r','d'] else 1.0)
                    new_melody.append((note, dur))


            # Optionally add oscillation for r/d
            for i, (note, dur) in enumerate(new_melody[start:start+len(motif)]):
                if note in ['r', 'd'] and random.random() < 0.5:
                    new_melody.insert(start+i+1, (note, dur*0.8))

        elif choice < 0.7:
            # Stepwise small modification
            idx = random.randint(1, len(new_melody)-1)
            # Stepwise small modification only if prev_note is in base octave
            prev_note = new_melody[idx-1][0]
            if prev_note not in self.notes:
                return new_melody  # skip stepwise modification
            prev_idx = self.notes.index(prev_note)
            step = random.choice([-1,1])
            new_idx = max(0, min(len(self.notes)-1, prev_idx + step))
            new_melody[idx] = (self.notes[new_idx], new_melody[idx][1])


        else:
            # Smooth out rhythm
            rhythm = random.choice(self.rhythms)
            for i, (note, _) in enumerate(new_melody):
                dur = rhythm[i % len(rhythm)] * (1.3 if note in ['r','d'] else 1.0)
                new_melody[i] = (note, dur)

        # Ensure last note is Sa
        new_melody[-1] = ('S', new_melody[-1][1]*1.5)

        return new_melody

    
    def generate_melody(self):
        """Generate a melody using simplified optimization"""
        current_melody = self.create_initial_melody()
        current_score = self.evaluate_melody(current_melody)
        best_melody = current_melody.copy()
        best_score = current_score
        
        temperature = 1000
        cooling_rate = 0.995
        score_history = []
        
        print("Generating melody...")
        
        for iteration in range(self.max_iterations):
            new_melody = self.create_variation(current_melody)
            new_score = self.evaluate_melody(new_melody)
            
            # Sometimes accept worse solutions to avoid getting stuck
            if new_score < current_score or random.random() < math.exp((current_score - new_score) / temperature):
                current_melody = new_melody
                current_score = new_score
                
                if current_score < best_score:
                    best_melody = current_melody.copy()
                    best_score = current_score
            
            temperature *= cooling_rate
            score_history.append(best_score)
            
            # if iteration % 500 == 0:
            #     print(f"Progress: {iteration}/{self.max_iterations}, Current Score: {best_score}")
        
        return best_melody, best_score, score_history
    
    def create_midi(self, melody, filename="raag_bhairav.mid", tempo=85):
        from midiutil import MIDIFile
        midi = MIDIFile(1)
        track = 0
        time = 0
        channel = 0
        volume = 100

        midi.addTrackName(track, time, "Raag Bhairav Melody")
        midi.addTempo(track, time, tempo)

         # Set instrument to Harmonium (program 22, 0-based index 21)
        midi.addProgramChange(track, channel, time, 21)

        overlap = 0.15  # more overlap for legato

        for i, (note, duration) in enumerate(melody):
            pitch = self.note_values[note]

            # Make strong swars longer, passing swars shorter
            if note in ['S', 'r', 'd']:
                note_duration = duration * 1.2 # * 1.6
            else:
                note_duration = duration * 0.8

            # Add slight overlap
            if i > 0:
                time -= overlap

            midi.addNote(track, channel, pitch, time, note_duration, volume)

            # Add glide (pitch bend) if moving stepwise
            if i < len(melody)-1:
                next_pitch = self.note_values[melody[i+1][0]]
                if abs(next_pitch - pitch) == 1:  # neighbor note
                    bend_time = time + note_duration * 0.7
                    bend_value = (next_pitch - pitch) * 200  # scaled pitch bend
                    midi.addPitchWheelEvent(track, channel, bend_time, bend_value)

            time += note_duration

        with open(filename, "wb") as output_file:
            midi.writeFile(output_file)

        print(f"MIDI file saved as {filename}")

    
    def create_visualizations(self, melody, score_history):
        """Create visualizations of the melody"""
        notes_only = [note for note, _ in melody]
        durations = [duration for _, duration in melody]
        note_numbers = [self.notes.index(note) for note in notes_only]
        
        # Plot 1: Melody contour
        plt.figure(figsize=(10, 5))
        plt.plot(note_numbers, 'o-')
        plt.yticks(range(len(self.notes)), self.notes)
        plt.xlabel('Position')
        plt.ylabel('Note')
        plt.title('Melody Contour')
        plt.grid(True, alpha=0.3)
        plt.savefig('melody_contour.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # Plot 2: Score improvement
        plt.figure(figsize=(10, 5))
        plt.plot(score_history)
        plt.xlabel('Iterations')
        plt.ylabel('Score (lower is better)')
        plt.title('Optimization Progress')
        plt.grid(True, alpha=0.3)
        plt.savefig('optimization_progress.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # Plot 3: Note distribution
        plt.figure(figsize=(10, 5))
        note_count = {note: notes_only.count(note) for note in self.notes}
        colors = ['red' if note in ['d', 'r'] else 'blue' for note in self.notes]
        plt.bar(range(len(note_count)), list(note_count.values()), color=colors)
        plt.xticks(range(len(self.notes)), self.notes)
        plt.xlabel('Notes')
        plt.ylabel('Frequency')
        plt.title('Note Distribution (red = important notes in Bhairav)')
        plt.grid(True, alpha=0.3)
        plt.savefig('note_distribution.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # # Plot 4: Note durations
        # plt.figure(figsize=(10, 5))
        # plt.plot(durations, 's-')
        # plt.xlabel('Note Position')
        # plt.ylabel('Duration')
        # plt.title('Note Durations')
        # plt.grid(True, alpha=0.3)
        # plt.savefig('note_durations.png', dpi=300, bbox_inches='tight')
        # plt.show()
    
    def analyze_melody(self, melody):
        """Analyze how well the melody follows Raag Bhairav"""
        notes_only = [note for note, _ in melody]
        note_string = ''.join(notes_only)
        
        print("\n" + "="*50)
        print("MELODY ANALYSIS")
        print("="*50)
        
        print("Notes:", " ".join(notes_only))
        
        # Check for signature patterns
        found_patterns = []
        for pattern in self.signature_patterns:
            pattern_str = ''.join(pattern)
            if pattern_str in note_string:
                found_patterns.append(pattern_str)
        
        print(f"\nSignature patterns found: {len(found_patterns)}")
        for pattern in found_patterns:
            print(f"  - {pattern}")
        
        # Check important notes
        r_count = notes_only.count('r')
        d_count = notes_only.count('d')
        print(f"\nImportant notes in Bhairav:")
        print(f"  'r' (komal re) appears {r_count} times. It is the Vadi (most important note) of the raag.")
        print(f"  'd' (komal dha) appears {d_count} times. It is the Samvadi (second most important note) of the raag.")
        
        # Check start and end
        # print(f"\nStarts on 'S': {notes_only[0] == 'S'}")
        # print(f"Ends on 'S': {notes_only[-1] == 'S'}")
        
        # Average duration
        avg_duration = sum(duration for _, duration in melody) / len(melody)
        print(f"Average note duration: {avg_duration:.2f} beats")
        
        return {
            'patterns_found': found_patterns,
            'd_count': d_count,
            'r_count': r_count,
            'starts_on_S': notes_only[0] == 'S',
            'ends_on_S': notes_only[-1] == 'S',
            'avg_duration': avg_duration
        }

def main():
    print("Raag Bhairav Melody Generator")
    print("=" * 30)
    
    # Create generator
    generator = RaagBhairavMelodyGenerator(length=10)
    
    # Generate melody
    melody, score, score_history = generator.generate_melody()
    
    # Analyze melody
    analysis = generator.analyze_melody(melody)
    
    # Create MIDI file
    generator.create_midi(melody)
    
    # Create visualizations
    print("\nCreating visualizations...")
    generator.create_visualizations(melody, score_history)
    
    # Final summary
    print("\n" + "="*50)
    print("GENERATION COMPLETE!")
    print("="*50)
    print("Files created:")
    print("  - raag_bhairav.mid (MIDI file to play)")
    print("  - melody_contour.png (visualization)")
    print("  - optimization_progress.png (visualization)")
    print("  - note_distribution.png (visualization)")
    print("  - note_durations.png (visualization)")

if __name__ == "__main__":
    main()
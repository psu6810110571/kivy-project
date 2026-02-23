from kivy.clock import Clock
import random

class GameEngine:
    def __init__(self):
        self.score = 0
        self.time_left = 60
        self.is_playing = False
        self.timer_event = None

    def start_game(self):
        self.score = 0
        self.time_left = 60
        self.is_playing = True
        
        self.timer_event = Clock.schedule_interval(self.update_time, 1)
        print("Game Started!")

    def update_time(self, dt):
        if self.time_left > 0:
            self.time_left -= 1
            print(f"Time left: {self.time_left}")
            
            if self.time_left == 10:
                print("10 seconds left!")
        else:
            self.game_over()

    def check_answer(self, user_answer, correct_answer):
        if user_answer == correct_answer:
            self.score += 1
            print(f"Correct! Score is now {self.score}")
            return True
        else:
            self.time_left -= 5
            print(f"Wrong! Time penalty -5s. Time left: {self.time_left}")
            return False
"""Solve Wordle with SeleniumBase."""
from seleniumbase import BaseCase
from llmWordle import LlmWordleSolver

from dotenv import load_dotenv
import os
import time

class WordleTests(BaseCase):

    def setup_wordle_game(self):
        self.open("https://www.nytimes.com/games/wordle/index.html")
        self.click_if_visible("button.purr-blocker-card__button", timeout=2)
        self.click_if_visible('button:contains("Play")', timeout=2)
        self.click_if_visible('svg[data-testid="icon-close"]', timeout=2)
        self.remove_elements("div.place-ad")

    def make_guess(self, word):
        letters = []
        for letter in word:
            letters.append(letter)
            button = 'button[data-key="%s"]' % letter
            self.click(button)
        button = 'button[class*="oneAndAHalf"]'
        self.click(button)

    def check_word_status(self, num_attempts):
        row = (
            'div[class*="Board"] div[class*="Row-module"]:nth-of-type(%s) '
            % num_attempts
        )
        tile = row + 'div:nth-child(%s) div[class*="module_tile__"]'
        self.wait_for_element(tile % "5" + '[data-state$="t"]')
        self.wait_for_element(tile % "5" + '[data-animation="idle"]')
        letter_status = []
        for i in range(1, 6):
            letter_eval = self.get_attribute(tile % str(i), "data-state")
            letter_status.append(letter_eval)
        return letter_status

    def play_wordle(self, watsonx : LlmWordleSolver):
        num_attempts = 0
        found_word = False

        for attempt in range(6):
            num_attempts += 1
            word = watsonx.guessWord().lower()
            self.make_guess()
            letter_status = self.check_word_status(num_attempts)
            watsonx.update_current_status(word, letter_status)
            watsonx.update_history(word)
            if letter_status.count("correct") == 5:
                found_word = True
                break

        self.save_screenshot_to_logs()

        if found_word:
            print('\nWord: "%s"\nAttempts: %s' % (word.upper(), num_attempts))
        else:
            print('Final guess: "%s" (Not the correct word!)' % word.upper())
            self.fail("Unable to solve for the correct word in 6 attempts!")
        time.sleep(3)

    def test_wordle(self):
         # Load the .env file
        load_dotenv()

        # Get the variables
        my_credentials = {
            "url": os.getenv("URL"),
            "apikey": os.getenv("APIKEY")
        }
        project_id = os.getenv("PROJECT_ID")

        watsonx = LlmWordleSolver(my_credentials=my_credentials, project_id=project_id)
        # setup wordle game
        self.open("https://www.nytimes.com/games/wordle/index.html")
        self.click_if_visible("button.purr-blocker-card__button", timeout=2)
        self.click_if_visible('button:contains("Play")', timeout=2)
        self.click_if_visible('svg[data-testid="icon-close"]', timeout=2)
        self.remove_elements("div.place-ad")

        # self.play_wordle(watsonx)
        # play wordle
        num_attempts = 0
        found_word = False

        for attempt in range(6):
            num_attempts += 1
            word = watsonx.guessWord()
            
            # self.make_guess(word)
            # make word
            letters = []
            for letter in word.lower():
                letters.append(letter)
                button = 'button[data-key="%s"]' % letter
                self.click(button)
            button = 'button[class*="oneAndAHalf"]'
            self.click(button)            

            letter_status = self.check_word_status(num_attempts)
            watsonx.update_current_status(word, letter_status)
            watsonx.update_history(word)
            if letter_status.count("correct") == 5:
                found_word = True
                break

        self.save_screenshot_to_logs()

        if found_word:
            print('\nWord: "%s"\nAttempts: %s' % (word.upper(), num_attempts))
        else:
            print('Final guess: "%s" (Not the correct word!)' % word.upper())
            self.fail("Unable to solve for the correct word in 6 attempts!")
        time.sleep(3)        




if __name__ == "__main__":
    from pytest import main
    main([__file__, "-s"])